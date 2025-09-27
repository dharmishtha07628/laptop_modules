from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta

class RetainedEarningsWizard(models.TransientModel):
    _name = 'retained.earnings.wizard'
    _description = 'Retained Earnings Calculation'

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)

    def action_generate_retained_earnings(self):
        company = self.env.company

        # Get the journal with name 'Closing' (case insensitive)
        journal = self.env['account.journal'].search([
            ('is_closing_journal', '=', True),
            ('type', '=', 'general'),
            ('company_id', '=', company.id)
        ], limit=1)

        if not journal:
            raise UserError("No journal found with name containing 'Closing'.")

        account_retained = company.account_retained_earnings_id
        account_offset = company.account_current_year_earnings_id

        if not account_retained or not account_offset:
            raise UserError("Please configure both retained and current year earnings accounts in company settings.")

        # Get all posted income/expense lines in the selected date range
        move_lines = self.env['account.move.line'].search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('account_id.account_type', 'in', ['income', 'expense','expense_depreciation','expense_direct_cost']),
            ('move_id.state', '=', 'posted'),
            ('company_id', '=', company.id),
        ])

        income_lines = move_lines.filtered(lambda l: l.account_id.account_type == 'income')
        expense_lines = move_lines.filtered(lambda l: l.account_id.account_type in ['expense', 'expense_depreciation', 'expense_direct_cost'])

        total_income = sum(income_lines.mapped('balance'))
        total_expense = sum(expense_lines.mapped('balance'))
        retained_balance = total_income + total_expense

        if retained_balance == 0:
            raise UserError("No profit or loss to post for the selected period.")

        # move_vals = {
        #     'journal_id': journal.id,
        #     'date': self.date_to,  # Next day after the end date
        #     'ref': 'Year-End Retained Earnings',
        #     'company_id': company.id,
        #     'line_ids': [
        #         (0, 0, {
        #             'name': f'{self.date_to}, Retained Earnings Closing',
        #             'account_id': account_retained.id,
        #             'debit': abs(retained_balance) if retained_balance < 0 else 0.0,
        #             'credit': retained_balance if retained_balance > 0 else 0.0,
        #         }),
        #         (0, 0, {
        #             'name':  f'{self.date_to}, Retained Earnings Closing',
        #             'account_id': account_offset.id,
        #             'credit': abs(retained_balance) if retained_balance < 0 else 0.0,
        #             'debit': retained_balance if retained_balance > 0 else 0.0,
        #         }),
        #     ]
        # }
        #
        # move = self.env['account.move'].create(move_vals)
        # move.action_post()
        if retained_balance < 0:
            move_vals = {
                'journal_id': journal.id,
                'date': self.date_to,
                'ref': 'Year-End Retained Earnings - Profit',
                'company_id': company.id,
                'line_ids': [
                    (0, 0, {
                        'name': f'{self.date_to}, Retained Earnings Closing (Profit)',
                        'account_id': account_retained.id,
                        'credit': retained_balance,
                        'debit': 0.0,
                    }),
                    (0, 0, {
                        'name': f'{self.date_to}, Retained Earnings Closing (Profit)',
                        'account_id': account_offset.id,
                        'debit': retained_balance,
                        'credit': 0.0,
                    }),
                ]
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()
        elif retained_balance > 0:
            move_vals = {
                'journal_id': journal.id,
                'date': self.date_to,
                'ref': 'Year-End Retained Earnings - Loss',
                'company_id': company.id,
                'line_ids': [
                    (0, 0, {
                        'name': f'{self.date_to}, Retained Earnings Closing (Loss)',
                        'account_id': account_retained.id,
                        'debit': abs(retained_balance),
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'name': f'{self.date_to}, Retained Earnings Closing (Loss)',
                        'account_id': account_offset.id,
                        'credit': abs(retained_balance),
                        'debit': 0.0,
                    }),
                ]
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()
        else:
            raise UserError("No profit or loss to post for the selected period.")