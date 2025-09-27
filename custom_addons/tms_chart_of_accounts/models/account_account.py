# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions


class AccountAccount(models.Model):
    _inherit = 'account.account'

    custom_account_id = fields.Many2one('custom.account', string="Custom Account", ondelete='set null', index=True)
    @api.model_create_multi
    def create(self, vals_list):
        accounts = super().create(vals_list)

        for account in accounts:
            if account.deprecated:
                continue

            # Search if a matching custom.account already exists
            custom = self.env['custom.account'].sudo().search([
                ('code', '=', account.code),
                ('name', '=', account.name),
            ], limit=1)

            if custom:
                # Link back to custom_account_id
                account.custom_account_id = custom.id

                # Add this company if not already linked
                if account.company_id.id not in custom.company_ids.ids:
                    custom.company_ids = [(4, account.company_id.id)]
            else:
                # Create a new custom.account and link
                custom = self.env['custom.account'].sudo().create({
                    'name': account.name,
                    'code': account.code,
                    'account_type': account.account_type,
                    'company_ids': [(6, 0, [account.company_id.id])],
                    'note': account.note,
                    'default_account': True
                })
                account.custom_account_id = custom.id

            # Set default receivable/payable accounts for partner if appropriate
            if account.account_type in ['asset_receivable', 'liability_payable']:
                property_field = ''
                if account.account_type == 'asset_receivable':
                    property_field = 'property_account_receivable_id'
                elif account.account_type == 'liability_payable':
                    property_field = 'property_account_payable_id'

                if property_field:
                    self.env['ir.property'].with_context(force_company=account.company_id.id)._set_default(
                        property_field, 'res.partner', account
                    )

        return accounts