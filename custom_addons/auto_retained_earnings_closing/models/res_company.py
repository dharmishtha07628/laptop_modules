from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_retained_earnings_id = fields.Many2one(
        'account.account',
        string='Retained Earnings Account',
        help='Account to use for retained earnings transfer at year-end.'
    )

    account_current_year_earnings_id = fields.Many2one(
        'account.account',
        string='Current Year Earnings Account',
        help='Temporary account to offset retained earnings entry.'
    )
