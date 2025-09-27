from odoo import fields, models

class BankCheckAttribute(models.Model):
    _inherit = 'bank.check.attribute'

    attribute = fields.Selection(
        selection_add=[
            ('remittance_table_ids', 'Remittance Table'),
            ('check_number', 'Check Number'),
            ('partner', 'Vendor'),
            ('company_address', 'Company Address'),
            ('company_name', 'Company Name'),
            ('signature', 'Signature'),
            ('date_label', 'Date Label'),
            ('order_label','Order Label'),
            ('address_line_1','Address Line 1'),
            ('address_line_2','Address Line 2'),
            ('address_line_3','Address Line 3'),
            ('underline','Under Line')
        ], ondelete={'remittance_table_ids': 'cascade', 'check_number': 'cascade', 'partner': 'cascade',
                     'company_address': 'cascade', 'company_name': 'cascade', 'signature': 'cascade',
                     'date_label': 'cascade',
                     'order_label':'cascade',
                     'address_line_1':'cascade',
                     'address_line_2':'cascade',
                     'address_line_3':'cascade',
                     'underline':'cascade'
                     })
