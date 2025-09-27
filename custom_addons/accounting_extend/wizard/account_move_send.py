# -*- coding: utf-8 -*-
import datetime
import io
import base64

from PIL import Image
from odoo.tools import pdf
from datetime import timedelta
# from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class AccountMoveSend(models.TransientModel):
    _name = "account.move.send"
    _inherit = ['account.move.send', 'mail.thread', 'mail.activity.mixin']

    attachments_ids = fields.Many2many('ir.attachment', string='Attachments', compute='_compute_attachments',
                                       store=True, readonly=False)
    is_attachment_required = fields.Boolean(string='Is Attachment Required ?', compute='_compute_attachments_required')
    send_merged_pdfs = fields.Boolean(string="Send Merged Pdf's")
    # , compute='_compute_attachments_required', readonly=False
    merged_attachments_ids = fields.Many2many('ir.attachment', 'merged_pdf_attachments_rel',
                                              string='Attachments for merge', compute='compute_merged_attachments_ids',
                                              store=True, readonly=False)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        move_id = self.env.context.get('active_id')
        if move_id:
            customer_send_merged_pdfs = self.env['account.move'].browse(move_id).partner_id.require_merged_attachment
            res.update({'send_merged_pdfs': customer_send_merged_pdfs})
        return res

    def action_send_and_print(self, force_synchronous=False, allow_fallback_pdf=False, **kwargs):
        # for move in self.move_ids:
        print(">>>>>>>>>>> action_send_and_print", self)
        print(">>>>>>>>>>>> self.send_merged_pdfs", self.send_merged_pdfs,self.attachments_ids , len(self.mail_attachments_widget))
        move_id = self.env.context.get('active_id')
        moves = self.env['account.move'].browse(move_id)
        if self.send_merged_pdfs and self.attachments_ids and len(self.mail_attachments_widget) > 1:

            # print(">>>>>>>>>>>> self.attachments_ids", self.attachments_ids)
            moves_data = {
                move: {
                    **(move.send_and_print_values if not self else self._get_wizard_values()),
                    **self._get_mail_move_values(move, self),
                }
                for move in moves
            }

            # Generate all invoice documents.
            self._generate_invoice_documents(moves_data, allow_fallback_pdf=allow_fallback_pdf)

            # print("OOOOOOOOOOOOO >>>>>>>>>>>>>> moves.invoice_pdf_report_id", moves.invoice_pdf_report_id)
            # print(">>>>>>>>>>>> self.attachments_ids", self.attachments_ids)
            # print(">>>>>>>>>>>>> self.send_merged_pdfs", self.send_merged_pdfs)
            # print(">>>>>>>>>>>>> self.mail_attachments_widget", self.mail_attachments_widget)
            # attachments_ids = [attachment['id'] for attachment in self.mail_attachments_widget]
            # attachments_ids = self.env['ir.attachment'].browse(attachments_ids)

            attachments_ids = self._get_invoice_extra_attachments(moves)
            # print("\n\n\n\n\n\n SUCCESS  >>>>>>>>>>>>> attachments_ids", attachments_ids)
            # moves.invoice_pdf_report_id + self.attachments_ids

            # write the logic for generate new merged attachment
            stream_list = []
            new = []
            for attachment in attachments_ids:
                if attachment.mimetype == 'application/pdf':
                    stream_list.append(attachment.raw)
                elif attachment.mimetype.startswith('image'):
                    stream = io.BytesIO(attachment.raw)
                    img = Image.open(stream)
                    new_stream = io.BytesIO()
                    img.convert("RGB").save(new_stream, format="pdf")
                    stream.close()
                    stream_list.append(new_stream.getvalue())
            if stream_list:
                merged_pdf = pdf.merge_pdf(stream_list)
                merged_pdf_attachment = self.env['ir.attachment'].create({
                    'name': self.move_ids[0].name + "_all_documents",
                    'type': 'binary',
                    'datas': base64.b64encode(merged_pdf),
                    'res_model': self._name,
                    'res_id': self.id,
                    'mimetype': 'application/pdf',
                })
                new.append({
                    'id': merged_pdf_attachment.id,
                    'name': merged_pdf_attachment.name,
                    'mimetype': merged_pdf_attachment.mimetype,
                    'placeholder': False,
                    'protect_from_deletion': True,
                })
            self.mail_attachments_widget = new
        moves.message = " Invoice Sent via Email on {}".format(datetime.datetime.now())
        super().action_send_and_print(force_synchronous=force_synchronous, allow_fallback_pdf=allow_fallback_pdf,
                                      **kwargs)
        moves.is_move_sent = True
        print("=========")

    # def _get_default_mail_attachments_widget(self, move, mail_template):
    #     res = super()._get_default_mail_attachments_widget(move=move, mail_template=mail_template)
    #     return res + self._get_logger_attachments_data(move)

    @api.model
    def _get_invoice_extra_attachments(self, move):
        # return move.invoice_pdf_report_id
        res = super()._get_invoice_extra_attachments(move)
        res += move.attachment_ids._origin
        return res

    @api.model
    def _get_mail_params(self, move, move_data):
        # We must ensure the newly created PDF are added. At this point, the PDF has been generated but not added
        # to 'mail_attachments_widget'.
        mail_attachments_widget = move_data.get('mail_attachments_widget')
        # print("\n\n\n\n HHHHHH >>>>>>>>>> mail_attachments_widget", mail_attachments_widget)
        seen_attachment_ids = set()
        to_exclude = {x['name'] for x in mail_attachments_widget if x.get('skip')}
        for attachment_data in mail_attachments_widget:
            if attachment_data['name'] in to_exclude:
                continue

            try:
                attachment_id = int(attachment_data['id'])
            except ValueError:
                continue

            seen_attachment_ids.add(attachment_id)

        mail_attachments = [
            (attachment.name, attachment.raw)
            for attachment in self.env['ir.attachment'].browse(list(seen_attachment_ids)).exists()
        ]
        
        print("-=-=acc extend body-=-=-")
        
        return {
            'body': move_data['mail_body'],
            'subject': move_data['mail_subject'],
            'partner_ids': move_data['mail_partner_ids'].ids,
            'attachments': mail_attachments,
            'author_id': move_data['sp_partner_id'],
            'scheduled_date': fields.Datetime.now() + timedelta(minutes=2)
        }

    # @api.model
    # def _get_logger_attachments_data(self, move):
    #     # attachments = False
    #     active_id = self._context.get('active_id')
    #     if active_id:
    #         move_id = self.env['account.move'].browse(active_id)
    #         if move_id and move_id.move_type in ['out_invoice'] and move_id.partner_id.is_attachment_required:
    #             return [
    #                 {
    #                     'id': attachment.id,
    #                     'name': attachment.name,
    #                     'mimetype': attachment.mimetype,
    #                     'placeholder': False,
    #                     'protect_from_deletion': True,
    #                 }
    #                 for attachment in self.attachments_ids._origin
    #             ]
    #     return []

    @api.depends('mail_template_id', 'attachments_ids')
    def _compute_mail_attachments_widget(self):
        for wizard in self:
            if wizard.mode == 'invoice_single':
                manual_attachments_data = [x for x in wizard.mail_attachments_widget or [] if x.get('manual')]
                wizard.mail_attachments_widget = (
                        wizard._get_default_mail_attachments_widget(wizard.move_ids, wizard.mail_template_id)
                        + manual_attachments_data
                )
            else:
                wizard.mail_attachments_widget = []

    @api.depends('mail_template_id')
    def _compute_attachments_required(self):
        for wizard in self:
            wizard.is_attachment_required = False
            if wizard._context.get('active_id'):
                move_id = self.env['account.move'].browse(self._context.get('active_id'))
                if move_id.partner_id.is_attachment_required:
                    wizard.is_attachment_required = True
                # if move_id.partner_id.require_merged_attachment:
                #     wizard.send_merged_pdfs = True

    @api.depends('mail_template_id')
    def _compute_attachments(self):
        for wizard in self:
            attachments = self.env['ir.attachment'].search(
                [('res_model', '=', 'account.move'), ('res_id', '=', self._context.get('active_id'))])
            if wizard.mode == 'invoice_single' and attachments:
                wizard.attachments_ids = attachments.ids
            else:
                wizard.attachments_ids = None

    @api.depends('attachments_ids')
    def compute_merged_attachments_ids(self):
        for wizard in self:
            if wizard.attachments_ids and wizard.send_merged_pdfs:
                wizard.merged_attachments_ids = wizard.attachments_ids.ids
            else:
                wizard.merged_attachments_ids = False

    @api.model
    def _link_invoice_documents(self, invoice, invoice_data):
        """
        Create the attachments containing the pdf/electronic documents for the invoice,
        only if not already present.
        """
        invoice_sudo = invoice.sudo()

        # Check if attachment already exists
        if invoice_sudo.message_main_attachment_id:
            invoice_sudo.is_move_sent = True
            # Skip if already added
            return

        # Create new attachment
        attachment = self.env['ir.attachment'].create(invoice_data['pdf_attachment_values'])
        invoice_sudo.message_main_attachment_id = attachment

        # Invalidate cache to refresh computed fields
        invoice_sudo.invalidate_recordset(fnames=['invoice_pdf_report_id', 'invoice_pdf_report_file'])

        # Mark as sent
        invoice_sudo.is_move_sent = True
