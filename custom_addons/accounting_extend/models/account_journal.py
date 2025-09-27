# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    name = fields.Char(string='Transaction Name', required=True, translate=True)
    is_credit_card = fields.Boolean('credit card')
    discrepancy_account_id = fields.Many2one('account.account', string="Discrepancy Account",
                                             domain=[('deprecated', '=', False)])
    bank_account_id = fields.Many2one('res.partner.bank',
                                      string="Bank Account",
                                      ondelete='restrict', copy=False,
                                      check_company=True,
                                      domain="[('partner_id','=', company_partner_id),('payment_method_type','!=','credit_card')]")


    @api.model
    def default_get(self, fields):
        res = super(AccountJournal, self).default_get(fields)
        context = self.env.context
        if context.get('default_is_credit_card'):
            res['type'] = 'bank'
            res['is_credit_card'] = True
        elif context.get('default_type') == 'bank':
            res['type'] = 'bank'
        elif context.get('default_type') == 'cash':
            res['type'] = 'cash'
        return res



class AccountPaymentMethodLine(models.Model):
    _inherit = "account.payment.method.line"

    @api.onchange('payment_method_id')
    def add_default_payment_account(self):
        if self.journal_id.default_account_id:
            self.payment_account_id = self.journal_id.default_account_id.id




