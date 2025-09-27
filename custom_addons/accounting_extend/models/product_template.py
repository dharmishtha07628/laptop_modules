from odoo import _, fields, models, api
from odoo.tools import format_amount
from odoo.exceptions import UserError

ACCOUNT_DOMAIN = "['&', ('deprecated', '=', False), ('account_type', 'not in', ('asset_receivable','liability_payable','asset_cash','liability_credit_card','off_balance'))]"


class ProductTemplate(models.Model):
    _inherit = "product.template"

    default_memo = fields.Char()
    supplier_tax_string = fields.Char(compute="_compute_supplier_tax_string")
    default_code = fields.Char(
        'Internal Reference', compute='_compute_default_code',
        inverse='_set_default_code', store=True, size=5)

    property_account_expense_id = fields.Many2one('account.account', company_dependent=True,
                                                  string="Expense Account",
                                                  domain=ACCOUNT_DOMAIN,
                                                  help="Keep this field empty to use the default value from the product category. If anglo-saxon accounting with automated valuation method is configured, the expense account on the product category will be used.")

    property_account_income_id = fields.Many2one('account.account', company_dependent=True,
                                                 string="Income Account",
                                                 domain=ACCOUNT_DOMAIN,
                                                 help="Keep this field empty to use the default value from the product category.")

    # @api.model
    # def get_import_templates(self):
    #     if self.env.context.get('is_revenue_codes'):
    #         return [{
    #             'label': _('Import Template for Revenue Codes'),
    #             'template': '/accounting_extend/static/base_import_sample_file/sample_revenue_code.csv'
    #         }]
    #     else:
    #         return super().get_import_templates()

    @api.depends('product_variant_ids.default_code')
    def _compute_default_code(self):
        self._compute_template_field_from_variant_field('default_code')

    def _set_default_code(self):
        self._set_product_variant_field('default_code')

    @api.depends('supplier_taxes_id', 'standard_price')
    def _compute_supplier_tax_string(self):
        for record in self:
            record.supplier_tax_string = record._construct_supplier_tax_string(record.standard_price)

    def _construct_supplier_tax_string(self, price):
        if self.currency_id:
            currency = self.currency_id
        else:
            currency = self.env.company.currency_id
        res = self.supplier_taxes_id.compute_all(price, product=self, partner=self.env['res.partner'])
        joined = []
        included = res['total_included']
        if currency.compare_amounts(included, price):
            joined.append(_('%s Incl. Taxes', format_amount(self.env, included, currency)))
        excluded = res['total_excluded']
        if currency.compare_amounts(excluded, price):
            joined.append(_('%s Excl. Taxes', format_amount(self.env, excluded, currency)))
        if joined:
            tax_string = f"(= {', '.join(joined)})"
        else:
            tax_string = " "
        return tax_string

    @api.onchange('default_code')
    def _onchange_default_code(self):
        rec = super(ProductTemplate, self)._onchange_default_code()
        if not self.default_code:
            return
        elif len(self.default_code) > 5:
            raise UserError(_("Short code should have 5 Character."))
