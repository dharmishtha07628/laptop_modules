# -*- coding: utf-8 -*-

from odoo.addons.sttl_plaid_integration.controller.plaid import PlaidController

from odoo import models, api, _, fields
import logging

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _get_bank_statements_available_sources(self):
        return self.__get_bank_statements_available_sources()

    status = fields.Selection([('not_connected', 'Not connected'), ('connected', 'Connected')], default="not_connected")
    access_token = fields.Char(readonly=True)
    account_id = fields.Char()
    start_date = fields.Date(string="Last Fetch Date",   compute="_compute_transaction_dates",store=True)
    end_date = fields.Date(
        string="End Date",
        store=True,
        default=fields.Date.context_today
    )
    bank_statements_source = fields.Selection(selection=_get_bank_statements_available_sources,
                                              default='',
                                              string='Bank Feeds',
                                              help="Defines how the bank statements will be registered")
    plaid_response = fields.Text('Plaid Response')
    plaid_balance = fields.Float(string="Plaid Balance", store=True)
    plaid_status = fields.Selection([('not_connected', 'Not Connected'), ('connected', 'Connected')])
    plaid_reconnect = fields.Boolean(default=False)



    @api.depends('bank_transaction_line_ids.date','bank_transaction_line_ids')
    def _compute_transaction_dates(self):
        for journal in self:
            lines = journal.bank_transaction_line_ids.filtered(lambda l: l.date)
            if lines:
                last_date = max(lines.mapped('date'))
                journal.start_date = last_date
            else:
                journal.start_date = fields.Date.context_today(journal)
                journal.end_date = fields.Date.context_today(journal)

    def __get_bank_statements_available_sources(self):
        return [
            ('plaid', _('Plaid')),
        ]


    def find_transactions_records(self):
        return {
            'name': _('Find Transactions'),
            'view_mode': 'form',
            'res_model': 'plaid.transaction.wizard',
            'type': 'ir.actions.act_window',
            'context': {'current_journal':self.id},
            'target':'new'
        }

    def _fill_bank_cash_dashboard_data(self, dashboard_data):
        # Call super to get all the original logic
        super()._fill_bank_cash_dashboard_data(dashboard_data)

        # Apply your custom addition after super() call
        bank_cash_journals = self.filtered(lambda journal: journal.type in ('bank', 'cash'))

        for journal in bank_cash_journals:
            # Safely get end date from the last statement, fallback to None
            end_date = journal.end_date if journal.end_date else None
            formatted_date = journal.end_date.strftime('%m/%d/%y') if journal.end_date else None
            currency_symbol = journal.currency_id.symbol if journal.currency_id else journal.company_id.currency_id.symbol
            balance = journal.plaid_balance if journal.plaid_balance else 0.0
            balance_with_currency = f"{currency_symbol}{balance:,.2f}"
            dashboard_data[journal.id].update({
                'end_date': formatted_date,
                'bank_balance': balance_with_currency
            })
