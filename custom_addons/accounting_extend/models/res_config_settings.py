from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def _default_fiscal_country_id(self):
        return self.env['res.country'].search([('code', '=', 'US')], limit=1).id

    account_fiscal_country_id = fields.Many2one(string="Fiscal Country Code",
                                                related="company_id.account_fiscal_country_id", readonly=False,
                                                store=False, default=_default_fiscal_country_id)
    product_weight_in_lbs = fields.Selection([
        ('0', 'Kilograms'),
        ('1', 'Pounds'),
    ], 'Weight unit of measure', config_parameter='product.weight_in_lbs', default='1')
    product_volume_volume_in_cubic_feet = fields.Selection([
        ('0', 'Cubic Meters'),
        ('1', 'Cubic Feet'),
    ], 'Volume unit of measure', config_parameter='product.volume_in_cubic_feet', default='1')

#    show_invoice_delivery_address = fields.Boolean(related='company_id.show_invoice_delivery_address', readonly=False,
#                                                   default=True)
    anglo_saxon_accounting = fields.Boolean(
        related="company_id.anglo_saxon_accounting",
        readonly=False, string="Use anglo-saxon accounting",
        help="Record the cost of a good as an expense when this good is invoiced to a final customer.",
        default=False
    )
    bank_account_id = fields.Many2one(
        'res.partner.bank',
        string="Default Bank",
        related='company_id.account_bank_account_id',
        readonly=False,
        check_company=True,
    )
