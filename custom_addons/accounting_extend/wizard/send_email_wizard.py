from odoo import api, fields, models
from odoo.exceptions import UserError

class SendEmailWizard(models.TransientModel):
    _name = 'send.email.wizard'
    _description = 'Wizard to Send Emails'

    account_move_ids = fields.Many2many('account.move', string="Invoices")

    @api.model
    def default_get(self, fields_list):
        res = super(SendEmailWizard, self).default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['account_move_ids'] = [(6, 0, active_ids)]
        return res

    def action_send_email(self):
        account_move_send_obj  = self.env['account.move.send']
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError("No records selected.")
        for active in active_ids:
            move_id = self.env['account.move'].search([('id', '=', active)])
            mail_template_id = False
            if move_id:
                if move_id.move_type == 'out_invoice':
                    mail_template_id = self.env.ref('account.email_template_edi_invoice').id
                if move_id.move_type == 'out_refund':
                    mail_template_id = self.env.ref('account.email_template_edi_credit_note').id
            values = {
                "move_ids" : [active],
                "mail_template_id" : mail_template_id,
            }
            move_send_id = account_move_send_obj.create(values)
            move_send_id.action_send_and_print()
            move_send_id.mail_template_id.send_mail(active, force_send=True)

    # def action_send_email(self):
    #     """Method to send emails to selected active_ids"""
    #     active_ids = self.env.context.get('active_ids', [])
    #     if not active_ids:
    #         raise UserError("No records selected.")

    #     # Create the record for account.move.send
    #     move_send_id = self.env['account.move.send'].create({
    #         "move_ids": active_ids,
    #         "mail_template_id" : self.env.ref('account.email_template_edi_invoice').id
    #     })

    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'account.move.send',
    #         'view_mode': 'form',
    #         'res_id': move_send_id.id,
    #         'target': 'new',
    #     }

# def action_send_email(self):
#     """Method to send emails to selected active_ids"""
#     active_ids = self.env.context.get('active_ids', [])
#     if not active_ids:
#         raise UserError("No records selected.")

#     # Create the record for account.move.send
#     move_send_id = self.env['account.move.send'].create({
#         "move_ids": active_ids,
#         "mail_template_id" : self.env.ref('account.email_template_edi_invoice').id
#     })

#     return {
#         'type': 'ir.actions.act_window',
#         'res_model': 'account.move.send',
#         'view_mode': 'form',
#         'res_id': move_send_id.id,
#         'target': 'new',
#     }
