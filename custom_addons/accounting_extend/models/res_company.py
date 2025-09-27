# -- coding:utf-8 --

from odoo import fields, models, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    show_invoice_delivery_address = fields.Boolean("Show Delivery Address In Invoice")
    write_off_account_id = fields.Many2one(
        'account.account',
        string='Default Write-Off Account',
        help='Default account used for write-offs'
    )
    account_bank_account_id = fields.Many2one('res.partner.bank')

    # # override this method for default load fiscal position (Chart Of Accounts)
    # @api.model_create_multi
    # def create(self, values):
    #     for value in values:
    #         value['chart_template'] = 'generic_coa_custom'
    #     return super(ResCompany, self).create(values)

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)

        if view_type == 'form':
            for node in arch.xpath(
                    "//field[@name='name']"
                    "|//field[@name='vat']"
            ):
                node.attrib['widget'] = ''

        return arch, view

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_invoice_delivery_address = fields.Boolean(related='company_id.show_invoice_delivery_address', readonly=False,default=True)
    write_off_account_id = fields.Many2one(
        'account.account',
        related='company_id.write_off_account_id',
        readonly=False,
        string="Write-Off Account",
        help='The accounting account used where automatic exchange differences will be added'
    )
