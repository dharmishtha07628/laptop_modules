# -*- coding: utf-8 -*-

import io
import base64

from PIL import Image
from odoo.tools import pdf
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _, exceptions
from odoo.tools import formatLang
import json


class AccountMove(models.Model):
    _inherit = 'account.move'

    show_invoice_delivery_address = fields.Boolean(related='company_id.show_invoice_delivery_address')
    vendor_bill_ref = fields.Char(string="Vendor Bill Reference", copy=False, required=False)
    po_ref = fields.Char(string="Po Number")
    is_po_ref_req = fields.Boolean(string="Is po number required", related="partner_id.is_po_ref_req", store=True)
    related_journal_entry_ids = fields.Many2many('account.move.line', 'rel_payment_related_journal_entry',
                                                 string='Related Journal Entries',
                                                 compute="_compute_payment_related_journal_entry")
    total_without_global_discount = fields.Monetary()
    global_discount = fields.Float(default=0.0)
    discount_total = fields.Monetary()
    display_name = fields.Char(compute='_compute_display_name')
    display_attachment_warning = fields.Text(string='Attachment Warning',
                                             compute='_compute_partner_attachment', copy=False)
    message = fields.Char()
    email_status = fields.Selection([('sent', 'Email Sent'), ('not_sent', 'Not Sent')], string="Email Status",
                                    default="not_sent", compute="compute_email_status", store=True)

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        if res.partner_id:
            res.message_unsubscribe([res.partner_id.id])
        return res

    def write(self, vals):
        if vals.get('partner_id', False):
            user_id = self.env['res.partner'].sudo().search([('id', '=', vals.get('partner_id', False))], limit=1)
            if user_id:
                res = super(AccountMove, self).write(vals)
                if self:
                    for rec in self:
                        rec.message_unsubscribe([user_id.id])
                return res
        return super(AccountMove, self).write(vals)


    @api.depends('bank_partner_id')
    def _compute_partner_bank_id(self):
        for move in self:
            # This will get the bank account from the partner in an order with the trusted first
            move.partner_bank_id = move.company_id.account_bank_account_id

    @api.depends('move_type', 'line_ids.amount_residual')
    def _compute_payments_widget_reconciled_info(self):
        for move in self:
            payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}

            if move.state == 'posted' and move.is_invoice(include_receipts=True):
                reconciled_vals = []
                reconciled_partials = move.sudo()._get_all_reconciled_invoice_partials()
                for reconciled_partial in reconciled_partials:
                    counterpart_line = reconciled_partial['aml']
                    if counterpart_line.move_id.ref:
                        reconciliation_ref = '%s (%s)' % (counterpart_line.move_id.name, counterpart_line.move_id.ref)
                    else:
                        reconciliation_ref = counterpart_line.move_id.name
                    if counterpart_line.amount_currency and counterpart_line.currency_id != counterpart_line.company_id.currency_id:
                        foreign_currency = counterpart_line.currency_id
                    else:
                        foreign_currency = False

                    reconciled_vals.append({
                        'name': counterpart_line.name,
                        'journal_name': counterpart_line.journal_id.name,
                        'company_name': counterpart_line.journal_id.company_id.name if counterpart_line.journal_id.company_id != move.company_id else False,
                        'amount': reconciled_partial['amount'],
                        'currency_id': move.company_id.currency_id.id if reconciled_partial['is_exchange'] else
                        reconciled_partial['currency'].id,
                        'date': counterpart_line.date,
                        'partial_id': reconciled_partial['partial_id'],
                        'account_payment_id': counterpart_line.payment_id.id,
                        'payment_method_name': counterpart_line.payment_id.payment_method_line_id.name,
                        'move_id': counterpart_line.move_id.id,
                        'ref': reconciliation_ref,
                        'memo': counterpart_line.payment_id.ref or '',  # Add memo field here
                        'is_exchange': reconciled_partial['is_exchange'],
                        'amount_company_currency': formatLang(self.env, abs(counterpart_line.balance),
                                                              currency_obj=counterpart_line.company_id.currency_id),
                        'amount_foreign_currency': foreign_currency and formatLang(self.env,
                                                                                   abs(counterpart_line.amount_currency),
                                                                                   currency_obj=foreign_currency)
                    })
                payments_widget_vals['content'] = reconciled_vals

            if payments_widget_vals['content']:
                move.invoice_payments_widget = payments_widget_vals
            else:
                move.invoice_payments_widget = False

    @api.onchange('invoice_date')
    def onchange_invoice_date(self):
        for rec in self:
            if rec.invoice_date and rec.move_type == 'in_invoice':
                rec.date = rec.invoice_date

    @api.depends('message')
    def compute_email_status(self):
        for rec in self:
            if rec.message:
                rec.email_status = 'sent'
            else:
                rec.email_status = 'not_sent'

    @api.constrains('vendor_bill_ref', 'partner_id')
    def _check_unique_vendor_and_bill_ref(self):
        for rec in self:
            duplicate_vendor_ids = self.search([
                ('id', '!=', rec.id),
                ('partner_id', '=', rec.partner_id.id),
                ('vendor_bill_ref', '!=', False),
                ('vendor_bill_ref', '=', rec.vendor_bill_ref),
                ('move_type', '=', 'in_invoice')
            ])
            if duplicate_vendor_ids:
                raise ValidationError(
                    _("Same Data is exists with the Vendor : {} and Vendor Bill Ref : {} ".format(rec.partner_id.name,
                                                                                                  rec.vendor_bill_ref)))

    def action_open_invoice_payment(self):
        reconciled_partials = self.sudo()._get_all_reconciled_invoice_partials()
        payment_ids = []
        invoice_partner = self.partner_id
        for reconciled_partial in reconciled_partials:
            counterpart_line = reconciled_partial['aml']
            for payment in counterpart_line.move_id.payment_ids:
                # Only include payments where the partner matches the invoice's partner
                if payment.partner_id == invoice_partner:
                    payment_ids.append(payment.id)

        # code for set the payment line

        journals = self.env['account.journal'].search([
            '|',
            ('company_id', 'parent_of', self.env.company.id),
            ('company_id', 'child_of', self.env.company.id),
            ('type', 'in', ('bank', 'cash')),
        ])

        available_journal_ids = journals.filtered('outbound_payment_method_line_ids')

        journal_id = self.env['account.journal'].search([
            *self.env['account.journal']._check_company_domain(self.company_id),
            ('type', 'in', ('bank', 'cash')),
            ('id', 'in', available_journal_ids.ids)
        ], limit=1)
        if journal_id:
            available_payment_method_lines = journal_id._get_available_payment_method_lines('outbound')
        else:
            available_payment_method_lines = False

            # Select the first available one by default.
        if available_payment_method_lines:
            payment_method_line_id = available_payment_method_lines[0]._origin
        else:
            payment_method_line_id = False

        # for reconciled_partial in reconciled_partials:
        #     counterpart_line = reconciled_partial['aml']
        #     payment_ids += counterpart_line.move_id.payment_ids.ids

        action = self.env["ir.actions.act_window"]._for_xml_id("account.action_account_payments_payable")
        action['domain'] = [
            ('id', 'in', payment_ids)
        ]
        # bill_line_ids.payment_amount =
        action['context'] = {'default_payment_type': 'outbound', 'default_partner_type': 'supplier',
                             'default_move_journal_types': ('bank', 'cash'),
                             'display_account_trust': True, 'default_partner_id': self.partner_id.id,
                             'default_journal_id': journal_id.id,
                             'default_amount': self.amount_total,
                             'default_payment_method_line': payment_method_line_id,
                             'default_paid_line_id': self.id, }

        return action

    # @api.depends('restrict_mode_hash_table', 'state')
    # def _compute_show_reset_to_draft_button(self):
    #     for move in self:
    #         move.show_reset_to_draft_button = not move.restrict_mode_hash_table and (
    #             (move.state == 'posted' and not move.need_cancel_request)) and move.move_type != 'entry'

    def action_open_vendor_bill_payment(self):
        pass

    # TODO (MUB): need to remove this
    # following is the old methods for open payments related to move.
    # def action_open_invoice_payment(self):
    #     action = self.env["ir.actions.act_window"]._for_xml_id("account.action_account_payments_payable")
    #     action['domain'] = [('partner_id', '=', self.partner_id.id), ("partner_type", "=", "customer"),
    #                         ("is_internal_transfer", "=", False)]
    #     action['context'] = {
    #         'default_payment_type': 'inbound',
    #         'default_partner_type': 'customer',
    #         'search_default_inbound_filter': 1,
    #         'default_move_journal_types': ('bank', 'cash'),
    #         'display_account_trust': True
    #     }
    #     return action

    # def action_open_vendor_bill_payment(self):
    #     action = self.env["ir.actions.act_window"]._for_xml_id("account.action_account_payments_payable")
    #     action['domain'] = [('partner_id', '=', self.partner_id.id), ("partner_type", "=", "supplier"),
    #                         ("is_internal_transfer", "=", False)]
    #     action['context'] = {'default_payment_type': 'outbound', 'default_partner_type': 'supplier',
    #                          'search_default_outbound_filter': 1, 'default_move_journal_types': ('bank', 'cash'),
    #                          'display_account_trust': True, }
    #     return action

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     for rec in self:
    #         if rec.move_type in ['out_invoice', 'out_refund'] and rec.partner_id.revenue_code_id:
    #             vals = {
    #                 'revenue_product_id': rec.partner_id.revenue_code_id.id,
    #                 'move_id': rec.id,
    #             }
    #             rec.invoice_line_ids = [(0, 0, vals)]
    #         if rec.move_type in ['in_invoice', 'in_refund'] and rec.partner_id.expense_code_id:
    #             vals = {
    #                 'product_id': rec.partner_id.expense_code_id.id,
    #                 'move_id': rec.id,
    #             }
    #             rec.invoice_line_ids = [(0, 0, vals)]

    @api.constrains('invoice_date', 'invoice_date_due')
    def _check_due_date(self):
        """Ensure the due date is not earlier than the bill date"""
        for move in self:
            if move.invoice_date_due and move.invoice_date and move.invoice_date_due < move.invoice_date:
                raise ValidationError("The due date cannot be earlier than the bill date.")

    @api.onchange('invoice_date')
    def _onchange_invoice_date(self):
        """Automatically update due date when the bill date is changed, or based on payment terms"""
        if self.invoice_date:
            self.invoice_date_due = self.invoice_date

    @api.onchange('invoice_date_due')
    def _onchange_invoice_due_date(self):
        for move in self:
            if move.invoice_date_due and move.invoice_date and move.invoice_date_due < move.invoice_date:
                raise ValidationError("The due date cannot be earlier than the bill date.")

    def merged_all_pdf(self):
        if self.merged_pdf:
            self.merged_pdf.unlink()
        stream_list = []
        for attachment in self.attachment_ids:
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
                'name': self.name + "_all_documents",
                'type': 'binary',
                'datas': base64.b64encode(merged_pdf),
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/pdf',
            })
            self.merged_pdf = merged_pdf_attachment.id

    @api.depends('partner_id')
    def _compute_partner_attachment(self):
        for move in self:
            move.display_attachment_warning = ''
            show_warning = move.state == 'draft' and \
                           move.move_type == 'out_invoice' and \
                           move.partner_id.is_attachment_required
            if show_warning:
                move.display_attachment_warning = _('Attachment required to validate Invoice')

    @api.depends('vendor_bill_ref', 'name')
    def _compute_display_name(self):
        for account in self:
            if account.vendor_bill_ref and account.move_type == 'in_invoice':
                account.display_name = f"{account.vendor_bill_ref}"
            elif account.move_type == 'entry' and account.name == '/':
                account.display_name = "New Journal Entry"
            else:
                account.display_name = f"{account.name}"

    def action_register_payment(self):
        payment_type = 'inbound'
        journals = self.env['account.journal'].search([
            '|',
            ('company_id', 'parent_of', self.env.company.id),
            ('company_id', 'child_of', self.env.company.id),
            ('type', 'in', ('bank', 'cash')),
        ])
        partner_type = 'customer'
        # if self.move_type in ['in_invoice', 'out_refund']:
        #     payment_type = 'outbound'
        #     partner_type = 'supplier'
        # elif self.move_type in ['out_invoice', 'in_refund']:
        #     payment_type = 'inbound'
        #     partner_type = 'customer'
        if self.move_type == 'in_invoice':
            payment_type = 'outbound'
            partner_type = 'supplier'
        elif self.move_type == 'in_refund':
            payment_type = 'inbound'
            partner_type = 'supplier'
        elif self.move_type == 'out_invoice':
            payment_type = 'inbound'
            partner_type = 'customer'
        elif self.move_type == 'out_refund':
            payment_type = 'outbound'
            partner_type = 'customer'
        else:
            payment_type = 'inbound'
            partner_type = 'customer'

        for pay in self:
            if payment_type == 'inbound':
                available_journal_ids = journals.filtered('inbound_payment_method_line_ids')
            else:
                available_journal_ids = journals.filtered('outbound_payment_method_line_ids')

        journal_id = self.env['account.journal'].search([
            *self.env['account.journal']._check_company_domain(self.company_id),
            ('type', 'in', ('bank', 'cash')),
            ('id', 'in', available_journal_ids.ids)
        ], limit=1)
        if journal_id:
            available_payment_method_lines = journal_id._get_available_payment_method_lines(payment_type)
        else:
            available_payment_method_lines = False

            # Select the first available one by default.
        if available_payment_method_lines:
            payment_method_line_id = available_payment_method_lines[0]._origin
        else:
            payment_method_line_id = False

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'target': 'current',
            'context': dict(self._context, **{
                'default_partner_id': self.partner_id.id,
                'default_payment_type': payment_type,
                'default_journal_id': journal_id.id,
                'default_amount': self.amount_total,
                'default_payment_method_line': payment_method_line_id,
                'default_paid_line_id': self.id,
                'default_partner_type': partner_type
            })
        }

    # discount_type = fields.Selection([
    #     ('fixed', 'Fixed Amount'),
    #     ('percentage', 'Percentage')
    # ], string='Discount Type', default='percentage')

    # @api.depends('global_discount', 'invoice_line_ids.price_unit')
    # def _compute_total_discount(self):
    #     for move in self:
    #         total_untaxed, total_untaxed_currency = 0.0, 0.0
    #         total_tax, total_tax_currency = 0.0, 0.0
    #         total_residual, total_residual_currency = 0.0, 0.0
    #         total, total_currency = 0.0, 0.0
    #         for line in move.line_ids.filtered(lambda line: not line.global_discount_line):
    #             if move.is_invoice(True):
    #                 # === Invoices ===
    #                 if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
    #                     # Tax amount.
    #                     total_tax += line.balance
    #                     total_tax_currency += line.amount_currency
    #                     total += line.balance
    #                     total_currency += line.amount_currency
    #                 elif line.display_type in ('product', 'rounding'):
    #                     # Untaxed amount.
    #                     total_untaxed += line.balance
    #                     total_untaxed_currency += line.amount_currency
    #                     total += line.balance
    #                     total_currency += line.amount_currency
    #                 elif line.display_type == 'payment_term':
    #                     # Residual amount.
    #                     total_residual += line.amount_residual
    #                     total_residual_currency += line.amount_residual_currency
    #             else:
    #                 # === Miscellaneous journal entry ===
    #                 if line.debit:
    #                     total += line.balance
    #                     total_currency += line.amount_currency
    #         sign = move.direction_sign
    #         move.total_without_global_discount = sign * total_currency
    #         move.discount_total = - (sign * total_untaxed_currency) * (move.global_discount / 100)
    #
    # @api.onchange('global_discount')
    # def _onchange_global_discount(self):
    #     for record in self:
    #         if record.global_discount:
    #             record._compute_invoice_totals()
    #             discount_amount = record.discount_total
    #             record.amount_total = record.amount_untaxed + record.amount_tax - discount_amount
    #
    # def _compute_invoice_totals(self):
    #     for move in self:
    #         move.amount_untaxed = sum(line.price_subtotal for line in move.invoice_line_ids)
    #         move.amount_tax = sum(line.tax_line_id.amount for line in move.line_ids if line.tax_line_id)
    #         discount_amount = move.discount_total
    #         move.amount_total = move.amount_untaxed + move.amount_tax - discount_amount
    #
    #         if move.amount_total == 0:
    #             raise UserError('The invoice total amount cannot be zero after applying the discount.')
    #
    #         # Ensure the discount line is added only if there's a discount
    #         if move.global_discount > 0:
    #             discount_product = self.env.ref('accounting_extend.global_product_discount')
    #             account_id = discount_product.property_account_income_id.id or move.journal_id.default_account_id.id
    #
    #             # Remove any existing discount lines to prevent duplication
    #             move.line_ids = [(2, line.id, 0) for line in move.line_ids if
    #                              line.name == 'Global Discount' or line.global_discount_line]
    #             move.invoice_line_ids = [(2, line.id, 0) for line in move.line_ids if
    #                                      line.name == 'Global Discount' or line.global_discount_line]
    #
    #             # Create discount line
    #             discount_line_vals = {
    #                 'move_id': move._origin.id,
    #                 'name': 'Global Discount',
    #                 'debit': discount_amount if move.move_type == 'in_invoice' else 0.0,
    #                 'credit': discount_amount if move.move_type == 'out_invoice' else 0.0,
    #                 'account_id': account_id,
    #                 'price_unit': discount_amount,
    #                 'global_discount_line': True
    #             }
    #             move.line_ids.create(discount_line_vals)

    @api.model
    def get_import_templates(self):
        if self._context.get('default_move_type') == 'out_invoice':
            return [{
                'label': _('Import Invoice'),
                'template': '/accounting_extend/static/imports_functionality/Customer_Invoice_WithLineDetails.xlsx'
            }]
        if self._context.get('default_move_type') == 'out_refund':
            return [{
                'label': _('Import Credit Notes'),
                'template': '/accounting_extend/static/imports_functionality/Customer_CreditNote_WithLineDetails.xlsx'
            }]
        if self._context.get('default_move_type') == 'in_invoice':
            return [{
                'label': _('Import Vendor Bills'),
                'template': '/accounting_extend/static/imports_functionality/Vendor_Bill_WithLineDetails.xlsx'
            }]
        if self._context.get('default_move_type') == 'in_refund':
            return [{
                'label': _('Import Vendor Credits'),
                'template': '/accounting_extend/static/imports_functionality/Vendor_CreditNote_WithLineDetails.xlsx'
            }]
        if self._context.get('default_move_type') == 'entry':
            return [{
                'label': _('Import Journal entry'),
                'template': '/accounting_extend/static/imports_functionality/Vendor_CreditNote_WithLineDetails.xlsx'
            }]


    @api.depends('ref', 'move_type', 'partner_id', 'invoice_date')
    def _compute_duplicated_ref_ids(self):
        move_to_duplicate_move = self.with_context(force_sales=True)._fetch_duplicate_supplier_reference()
        for move in self:
            # Uses move._origin.id to handle records in edition/existing records and 0 for new records
            move.duplicated_ref_ids = move_to_duplicate_move.get(move._origin, self.env['account.move'])

    @api.model
    def get_purchase_types(self, include_receipts=False):
        data = ['in_invoice', 'in_refund'] + (include_receipts and ['in_receipt'] or [])
        if 'force_sales' in self._context:
            data += self.get_sale_types(include_receipts=include_receipts)
        return data

    def action_open_vendor_bill_attachment(self):
        self.ensure_one()
        return {
            'name': 'Vendor Bill: Attachments',
            'view_mode': 'form',
            'view_id': self.env.ref('accounting_extend.view_vendor_bill_attachment').id,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    def _compute_payment_related_journal_entry(self):
        for rec in self:
            if rec.payment_id.related_payment_id and rec.payment_id.related_payment_id.move_id.line_ids:
                rec.related_journal_entry_ids = rec.payment_id.related_payment_id.move_id.line_ids.ids
            else:
                rec.related_journal_entry_ids = False

    @api.onchange('partner_id')
    def _onchange_custom_partner(self):
        self.ref = self.partner_id.po_ref if self.partner_id else False

    @api.onchange('partner_id', 'amount_total')
    def onchange_customer_credit_limit(self):
        for record in self:
            moves = self.search([('partner_id', '=', record.partner_id.id), ('state', '=', 'posted')])
            total_invoiced = sum(moves.mapped('amount_residual'))
            #            if record.state == 'draft':
            #                total_invoiced += record.amount_total
            if record.state == 'draft' and record.move_type == 'out_invoice' and record.partner_id.use_partner_credit_limit and record.partner_id.credit_limit < (
                    total_invoiced + record.amount_total):
                record.partner_credit_warning = _(
                    '%(partner_name)s has reached its credit limit of: %(credit_limit)s and Current Balance is %(current_bal)s',
                    partner_name=record.partner_id.name,
                    credit_limit=formatLang(self.env, record.partner_id.credit_limit,
                                            currency_obj=record.company_id.currency_id),
                    current_bal=formatLang(self.env, total_invoiced,
                                           currency_obj=record.company_id.currency_id)
                )

    #                raise ValidationError(msg)

    @api.depends('company_id', 'partner_id', 'tax_totals', 'currency_id', 'amount_total')
    def _compute_partner_credit_warning(self):
        for record in self:
            record.with_company(record.company_id)
            record.partner_credit_warning = ''
            moves = self.search([('partner_id', '=', record.partner_id.id), ('state', '=', 'posted')])
            total_invoiced = sum(moves.mapped('amount_residual'))
            #            if record.state == 'draft':
            #                total_invoiced += record.amount_total
            if record.state == 'draft' and record.move_type == 'out_invoice' and record.partner_id.use_partner_credit_limit and record.partner_id.credit_limit < (
                    total_invoiced + record.amount_total):
                total_field = 'amount_total' if record.currency_id == record.company_currency_id else 'amount_total_company_currency'
                if record.tax_totals:
                    current_amount = record.tax_totals[total_field]
                    record.partner_credit_warning = self._build_credit_warning_message(
                        record,
                        current_amount=current_amount,
                        exclude_amount=record._get_partner_credit_warning_exclude_amount(),
                    )

    def _post(self, soft=True):
        # Call the original posting logic first
        posted_moves = super()._post(soft=soft)

        # Now remove the partner from followers after posting
        for move in posted_moves:
            if move.partner_id:
                move.message_unsubscribe([move.partner_id.id])

        return posted_moves

    def action_post(self):
        for line in self.invoice_line_ids:
            # json.loads(line.analytic_distribution)
            if line.analytic_distribution:
                analytic_amount_vals = 0
                for key, value in line.analytic_distribution.items():
                    analytic_amount_vals += value

                # if line.price_unit != ((line.price_unit * analytic_amount_vals) / 100):
                #     raise ValidationError("Analytic Distribution amount is more than the Price")
        # inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        if self.partner_id.is_attachment_required and self.move_type in ['out_invoice']:
            attachment = self.env['ir.attachment'].search(
                [('res_model', '=', 'account.move'), ('res_id', '=', self.id)])
            if not attachment:
                raise ValidationError(_('Attachment required to validate Invoice'))
        moves = self.search([('partner_id', '=', self.partner_id.id), ('state', '=', 'posted')])
        total_invoiced = sum(moves.mapped('amount_residual'))
        if self.move_type == 'out_invoice' and self.partner_id.use_partner_credit_limit and self.partner_id.credit_limit < (
                total_invoiced + self.amount_total):
            msg = _(
                '%(partner_name)s has reached its credit limit of: %(credit_limit)s and Current Balance is %(current_bal)s',
                partner_name=self.partner_id.name,
                credit_limit=formatLang(self.env, self.partner_id.credit_limit,
                                        currency_obj=self.company_id.currency_id),
                current_bal=formatLang(self.env, total_invoiced,
                                       currency_obj=self.company_id.currency_id)
            )
            raise ValidationError(msg)
        return super(AccountMove, self).action_post()

    def _build_credit_warning_message(self, record, current_amount=0.0, exclude_current=False, exclude_amount=0.0):
        partner_id = record.partner_id.commercial_partner_id
        credit_to_invoice = partner_id.credit_to_invoice - exclude_amount
        total_credit = partner_id.credit + credit_to_invoice + current_amount
        if not partner_id.credit_limit or total_credit <= partner_id.credit_limit or record.move_type == 'in_invoice':
            return ''
        moves = self.search([('partner_id', '=', record.partner_id.id), ('state', '=', 'posted')])
        total_invoiced = sum(moves.mapped('amount_residual'))
        #        if self.state == 'draft':
        #            total_invoiced += self.amount_total
        msg = _(
            '%(partner_name)s has reached its credit limit of: %(credit_limit)s and Current Balance is %(current_bal)s',
            partner_name=partner_id.name,
            credit_limit=formatLang(self.env, partner_id.credit_limit, currency_obj=record.company_id.currency_id),
            current_bal=formatLang(self.env, total_invoiced, currency_obj=record.company_id.currency_id)
        )
        total_credit_formatted = formatLang(self.env, total_credit, currency_obj=record.company_id.currency_id)
        if credit_to_invoice > 0 and current_amount > 0:
            msg + '\n' + _(
                'Total amount due (including sales orders and this document): %(total_credit)s',
                total_credit=total_credit_formatted
            )
        elif credit_to_invoice > 0:
            msg + '\n' + _(
                'Total amount due (including sales orders): %(total_credit)s',
                total_credit=total_credit_formatted
            )
        elif current_amount > 0:
            msg + '\n' + _(
                'Total amount due (including this document): %(total_credit)s',
                total_credit=total_credit_formatted
            )
        else:
            msg + '\n' + _(
                'Total amount due: %(total_credit)s',
                total_credit=total_credit_formatted
            )
        return msg

    # def action_invoice_sent(self):
    #     """ Override to regenerate and attach the main invoice PDF as message_main_attachment_id """
    #     self.ensure_one()
    #
    #     # Call original behavior
    #     report_action = super().action_invoice_sent()
    #
    #     # Check for admin and layout configuration
    #     if self.env.is_admin() and not self.env.company.external_report_layout_id and not self.env.context.get(
    #             'discard_logo_check'):
    #         return self.env['ir.actions.report']._action_configure_external_report_layout(report_action)
    #
    #     # 🔁 Regenerate PDF and set as main attachment
    #     if self.message_main_attachment_id:
    #         self.message_main_attachment_id.unlink()
    #     # Generate invoice PDF
    #     pdf_content, _report_format = self.env['ir.actions.report'].with_company(self.company_id)._render(
    #         'account.account_invoices', self.ids, data={'proforma': True})
    #     # Create new attachment
    #     attachment = self.env['ir.attachment'].create({
    #         'name': self._get_invoice_report_filename(),
    #         'type': 'binary',
    #         'datas': base64.b64encode(pdf_content),
    #         'res_model': self._name,
    #         'res_id': self.id,
    #         'mimetype': 'application/pdf',
    #     })
    #     self.invoice_pdf_report_id = attachment.id
    #
    #     # Assign to main attachment field
    #     self.message_main_attachment_id = attachment.id
    #
    #     # Optionally post in chatter
    #     self.message_post(body="Main invoice PDF regenerated and attached.", attachment_ids=[attachment.id])
    #
    #     return report_action
    def action_invoice_sent(self):
        """Override to regenerate and attach main invoice PDF safely without deleting user-uploaded files"""
        self.ensure_one()

        # Call super method first
        report_action = super().action_invoice_sent()

        # Remove previous system-generated PDF (if exists and tagged)
        if (
                self.message_main_attachment_id
                and self.message_main_attachment_id.description == 'system_generated_invoice_pdf'
        ):
            self.message_main_attachment_id.unlink()

        # Generate new system PDF
        pdf_content, _format = self.env['ir.actions.report'].with_company(self.company_id)._render(
            'account.account_invoices', self.ids, data={'proforma': True}
        )

        # Create new system-generated attachment and tag it
        new_attachment = self.env['ir.attachment'].create({
            'name': self._get_invoice_report_filename(),
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
            'description': 'system_generated_invoice_pdf',  # Tag for safe deletion
        })

        # Update main attachment
        self.invoice_pdf_report_id = new_attachment.id
        self.message_main_attachment_id = new_attachment.id

        # Optional: Post in chatter
        self.message_post(
            body="✅ Main invoice PDF regenerated and attached.",
            attachment_ids=[new_attachment.id]
        )

        return report_action

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    revenue_product_id = fields.Many2one(comodel_name='product.product',
                                         string='Revenue Product',
                                         check_company=True)

    @api.constrains('account_id', 'display_type')
    def _check_payable_receivable(self):
        """overrride and pass data"""
        for line in self:
           pass

    @api.onchange('revenue_product_id')
    def product_id_default_memo(self):
        for rec in self:
            if rec.revenue_product_id:
                rec.product_id = rec.revenue_product_id.id
                rec.name = rec.revenue_product_id.default_memo

    @api.onchange('product_id')
    def set_the_price_based_on_the_product(self):
        for rec in self:
            if rec.product_id and rec.move_id.move_type == 'in_invoice':
                # rec.product_id.purchase_ok = True
                # rec.product_id.sale_ok = False
                expense_code_id = rec.move_id.partner_id.expense_code_ids.filtered(
                    lambda l: l.product_id == rec.product_id)
                if expense_code_id:
                    rec.price_unit = expense_code_id.price
            elif rec.product_id and rec.move_id.move_type == 'out_invoice':
                # rec.product_id.sale_ok = True
                # rec.product_id.purchase_ok = False
                revenue_code_id = rec.move_id.partner_id.revenue_code_ids.filtered(
                    lambda l: l.product_id == rec.product_id)
                if revenue_code_id:
                    rec.price_unit = revenue_code_id.price



