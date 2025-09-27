# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Chart of Accounts'),
            'template': '/accounting_extend/static/imports_functionality/Chart_of_Accounts.xlsx'
        }]

    company_ids = fields.Many2many(
        'res.company',
        string='Allowed Companies',
        help='Only users from these companies can access this account.'
    )