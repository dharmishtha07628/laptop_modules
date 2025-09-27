from odoo import models, fields, api

class CustomAccount(models.Model):
    _name = 'custom.account'
    _description = 'Custom Chart of Account'
    _inherit = ['mail.thread']

    name = fields.Char(string="Account Name", required=True, tracking=True, translate=True)
    code = fields.Char(size=64, required=True, tracking=True, index=True)
    account_type = fields.Selection(
        selection=[
            ("asset_receivable", "Receivable"),
            ("asset_cash", "Bank and Cash"),
            ("asset_current", "Current Assets"),
            ("asset_non_current", "Non-current Assets"),
            ("asset_prepayments", "Prepayments"),
            ("asset_fixed", "Fixed Assets"),
            ("liability_payable", "Payable"),
            ("liability_credit_card", "Credit Card"),
            ("liability_current", "Current Liabilities"),
            ("liability_non_current", "Non-current Liabilities"),
            ("equity", "Equity"),
            ("equity_unaffected", "Current Year Earnings"),
            ("income", "Income"),
            ("income_other", "Other Income"),
            ("expense", "Expenses"),
            ("expense_depreciation", "Depreciation"),
            ("expense_direct_cost", "Cost of Revenue"),
            ("off_balance", "Off-Balance Sheet"),
            ("equity_retained_earning", "Retained Earning")
        ],
        string="Type", tracking=True,
        required=True,
        store=True, readonly=False, precompute=True, index=True,
        help="Account Type is used for information purpose, to generate country-specific legal reports, and set the rules to close a fiscal year and generate opening entries."
    )
    company_ids = fields.Many2many('res.company', string='Companies', required=True)
    note = fields.Text('Internal Notes', tracking=True)
    deprecated = fields.Boolean(default=False, tracking=True)
    cash_flow_category = fields.Selection(
        [('operating_activities', 'Operating Activities'), ('investing_activities', 'Investing Activities'),
         ('financing_activities', 'Financing Activities')])
    reconcile = fields.Boolean()
    default_account = fields.Boolean()
    account_ids = fields.Many2many('account.account')

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.default_account:
            return record
        for company in record.company_ids:
            existing = self.env['account.account'].sudo().search([
                ('custom_account_id', '=', record.id),
                ('company_id', '=', company.id)
            ], limit=1)

            if not existing:
                account = self.env['account.account'].sudo().create({
                    'name': record.name,
                    'code': record.code,
                    'account_type': record.account_type,
                    'company_id': company.id,
                    'custom_account_id': record.id,
                })
                record.account_ids = [(6, 0, account.ids)]
            else:
                record.account_ids = [(6, 0, existing.ids)]
        return record

    def write(self, vals):
        for rec in self:
            original_companies = rec.company_ids.ids

        res = super().write(vals)  # Perform the write first

        for rec in self:
            new_companies = rec.company_ids.ids
            removed_companies = list(set(original_companies) - set(new_companies))

            # Deprecate accounts from removed companies
            if removed_companies:
                accounts_to_deprecate = self.env['account.account'].sudo().search([
                    ('custom_account_id', '=', rec.id),
                    ('company_id', 'in', removed_companies),
                    ('deprecated', '=', False),
                ])
                accounts_to_deprecate.sudo().write({'deprecated': True})
                rec.account_ids = [(3, acc.id, 0) for acc in accounts_to_deprecate]

            # Sync or create for active companies
            for company in rec.company_ids:
                account = self.env['account.account'].sudo().search([
                    ('company_id', '=', company.id),
                    ('custom_account_id', '=', rec.id)
                ], limit=1)

                # Only update code if it's changed
                code = rec.code
                update_code = 'code' in vals and (not account or account.code != vals['code'])

                values = {
                    'name': rec.name,
                    'account_type': rec.account_type,
                    'deprecated': rec.deprecated,
                }

                if update_code:
                    values['code'] = vals['code']

                if account:
                    account.sudo().write(values)
                else:
                    # If no account exists, code must be set
                    account = self.env['account.account'].sudo().create({
                        **values,
                        'code': code,
                        'company_id': company.id,
                        'custom_account_id': rec.id,
                    })
                    rec.account_ids = [(6, 0, account.ids)]

        return res
