# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models, api
import logging

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    sophtron_account_type = fields.Char(string="Sophtron Account Type")
    sophtron_member_id = fields.Many2one('sophtron.api.member')

    def action_configure_bank_journal(self):
        """ This function is called by the "configure" button of bank journals,
        visible on dashboard if no bank statement source has been defined yet
        """
        # We simply call the setup bar function.
        action = self.env.ref('sophtron_integration.action_setting_sophtron_synchronisation').sudo().read()[0]
        sophtron = self.env['sophtron.api.client'].sudo().search([('journal_id', '=', self.id)], limit=1)
        action['params'] = {'journal_id': self.id, 'sophtron_id': sophtron.id if sophtron else False}
        action['context'] = {'active_test': False, 'create': False}
        return action

    def _fill_bank_cash_dashboard_data(self, dashboard_data):
        # Call the super method to retain existing behavior
        super(AccountJournal, self)._fill_bank_cash_dashboard_data(dashboard_data)

        # Add 'account_amount' key to each journal's data
        for journal in self.filtered(lambda journal: journal.type in ('bank', 'cash')):
            bank_balance = self.env['account.bank.transaction.line'].search([
                ('journal_id', '=', journal.id)
            ]).mapped('amount')
            currency = journal.currency_id or self.env['res.currency'].browse(journal.company_id.sudo().currency_id.id)

            dashboard_data[journal.id].update({
                'bank_balance': currency.format(sum(bank_balance)),  # Sum the amounts
            })

    def action_fetch_account_transaction(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sophtron.api.transactions',
            'view_mode': 'form',
            'view_id': self.env.ref('sophtron_integration.view_sophtron_api_transactions_form').id,
            'target': 'new',
            'context': {
                'default_sophtron_id': self.sophtron_member_id.sophtron_id.id,
                'default_journal_id': self.id,
            }
        }

    def action_view_transaction_line(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "tms_account_reconcile.action_bank_statement_line_extended_in_review")
        action['domain'] = [('journal_id', 'in', self.ids), ('account_id', '=', self.default_account_id.id)]
        return action
