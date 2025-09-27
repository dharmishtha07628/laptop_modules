from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date, timedelta

class AccountMoveAutoClosing(models.Model):
    _inherit = 'account.move'


    @api.model
    def run_auto_fiscal_closing(self):
        """ Auto closing of income and expense accounts at year-end """
        company = self.env.company
        today = date.today()

        if today.month == 1 and today.day == 1:  # example for Jan 1st
            retained_account = company.account_retained_earnings_id
            current_year_account = company.account_current_year_earnings_id

            if not retained_account or not current_year_account:
                raise UserError("Retained Earnings accounts not configured in settings.")

            fiscal_start = date(today.year - 1, 1, 1)
            fiscal_end = date(today.year, 12, 31)

            # Get all P&L accounts
            income_expense_lines = self.env['account.move.line'].search([
                ('date', '>=', fiscal_start),
                ('date', '<=', fiscal_end),
                ('account_id.account_type', 'in', ('income', 'expense')),
                ('company_id', '=', company.id),
                ('move_id.state', '=', 'posted')
            ])

            total_income = sum(l.credit - l.debit for l in income_expense_lines if l.account_id.account_type == 'income')
            total_expense = sum(l.debit - l.credit for l in income_expense_lines if l.account_id.account_type == 'expense')

            net_result = total_income - total_expense

            if net_result == 0:
                return  # Nothing to post

            # Create journal entry
            journal = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
            if not journal:
                raise UserError("No general journal found.")

            move = self.create({
                'date': today,
                'journal_id': journal.id,
                'ref': 'Auto Closing Entry for FY',
                'line_ids': [
                    (0, 0, {
                        'account_id': retained_account.id,
                        'credit': net_result if net_result > 0 else 0.0,
                        'debit': -net_result if net_result < 0 else 0.0,
                        'name': 'Profit/Loss Transfer to Retained Earnings',
                    }),
                    (0, 0, {
                        'account_id': current_year_account.id,
                        'debit': net_result if net_result > 0 else 0.0,
                        'credit': -net_result if net_result < 0 else 0.0,
                        'name': 'Offset from Current Year Earnings',
                    }),
                ]
            })

            move.action_post()
