from odoo import models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)

        # Target company logic: fallback to current if not enough companies
        all_companies = self.env['res.company'].sudo().search([], order='id')
        target_company = all_companies[1] if len(all_companies) > 1 else self.env.company

        def find_company_account(account_type):
            return self.env['account.account'].sudo().search([
                ('account_type', '=', account_type),
                ('company_id', '=', target_company.id)
            ], limit=1)

        receivable = find_company_account('asset_receivable')
        payable = find_company_account('liability_payable')

        # Set ir.property using force_company context only if in target company
        if receivable and 'property_account_receivable_id' in fields_list:
            self._set_company_property('property_account_receivable_id', receivable, target_company)
            if self.env.company.id == target_company.id:
                defaults['property_account_receivable_id'] = receivable.id

        if payable and 'property_account_payable_id' in fields_list:
            self._set_company_property('property_account_payable_id', payable, target_company)
            if self.env.company.id == target_company.id:
                defaults['property_account_payable_id'] = payable.id

        return defaults

    def _set_company_property(self, field_name, account, company):
        # Remove any existing property for that field and company
        existing = self.env['ir.property'].sudo().search([
            ('name', '=', field_name),
            ('company_id', '=', company.id),
            ('res_id', '=', False)
        ])
        existing.unlink()

        field = self.env['ir.model.fields'].sudo().search([
            ('model', '=', 'res.partner'),
            ('name', '=', field_name)
        ], limit=1)

        if field:
            self.env['ir.property'].sudo().with_context(force_company=company.id).create({
                'name': field_name,
                'fields_id': field.id,
                'company_id': company.id,
                'value_reference': f'account.account,{account.id}',
                'res_id': False,
            })

    def _set_defaults_for_all_companies(self):
        companies = self.env['res.company'].sudo().search([])
        for company in companies:
            def find_account(account_type):
                return self.env['account.account'].sudo().search([
                    ('account_type', '=', account_type),
                    ('company_id', '=', company.id)
                ], limit=1)

            receivable = find_account('asset_receivable')
            payable = find_account('liability_payable')

            if receivable:
                self._set_company_property('property_account_receivable_id', receivable, company)
            if payable:
                self._set_company_property('property_account_payable_id', payable, company)

    @api.model
    def create(self, vals):
        self._set_defaults_for_all_companies()

        current_company = self.env.company
        if not vals.get('property_account_receivable_id'):
            receivable = self.env['account.account'].sudo().search([
                ('account_type', '=', 'asset_receivable'),
                ('company_id', '=', current_company.id)
            ], limit=1)
            if receivable:
                vals['property_account_receivable_id'] = receivable.id

        if not vals.get('property_account_payable_id'):
            payable = self.env['account.account'].sudo().search([
                ('account_type', '=', 'liability_payable'),
                ('company_id', '=', current_company.id)
            ], limit=1)
            if payable:
                vals['property_account_payable_id'] = payable.id

        return super().create(vals)

    def write(self, vals):
        self._set_defaults_for_all_companies()
        return super().write(vals)