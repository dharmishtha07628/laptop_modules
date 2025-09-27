# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions
from datetime import datetime
import binascii
import tempfile
from tempfile import TemporaryFile
from odoo.exceptions import UserError, ValidationError
import logging
import json

_logger = logging.getLogger(__name__)
import io
import re

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class ImportInvoiceWizard(models.TransientModel):
    _name = 'import.invoice.wizard'
    _description = "Import Invoice Wizard"

    file_to_import = fields.Binary(string="Upload File")
    file_name = fields.Char('File Name')

    def check_splcharacter(self, test):
        # Make own character set and pass
        # this as argument in compile method

        string_check = re.compile('@')

        # Pass the string in search
        # method of regex object.
        if (string_check.search(str(test)) == None):
            return False
        else:
            return True

    def get_analytic_data(self, data):
        lines = {}
        if data:
            data = json.loads(data)
            analytic_plan = self.env['account.analytic.plan'].search([('default_applicability', '!=', 'unavailable')])
            for key, value in data.items():
                names = key.split(",")
                id_list = []
                for index in range(0, len(analytic_plan)):
                    if index < len(names):
                        analytic_id = self.env['account.analytic.account'].search([('name', '=', names[index].strip())],
                                                                                  limit=1)
                        id_list.append(str(analytic_id.id))
                    else:
                        id_list.append("")
                if id_list:
                    id_str = ",".join(id_list)
                    lines.update({id_str: value})
        return lines

    def process_import_inv_line(self):
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            temp_file.write(binascii.a2b_base64(self.file_to_import))
            temp_file.seek(0)
            workbook = xlrd.open_workbook(temp_file.name)
            sheet = workbook.sheet_by_index(0)
        except Exception:
            raise ValidationError(_("Invalid file!"))

        line_fields = None
        for row_index in range(sheet.nrows):
            if row_index == 0:
                line_fields = list(map(lambda cell: cell.value, sheet.row(row_index)))
            else:
                line_data = list(map(lambda cell: str(cell.value), sheet.row(row_index)))
                if not line_data[0] and not line_data[1]:
                    # invoice = self.env['account.move'].browse(self._context.get('active_id'))
                    msg = ''
                    # if invoice.move_type == 'out_invoice':
                    #     msg += "Revenue code"
                    # elif invoice.move_type == 'in_invoice':
                    #     msg += "Expense code"
                    raise ValidationError("Account is required for importing the lines")
                values = {
                    'product': line_data[0].split('.')[0],
                    'account': line_data[1],
                    'analytic_distribution': self.get_analytic_data(line_data[2]),
                    'quantity': line_data[3],
                    # 'uom': line_data[4],
                    'description': line_data[4],
                    'price': line_data[5],
                    # 'tax': line_data[7],
                    # 'disc': line_data[8]
                }
                # additional_fields = dict(zip(line_fields[8:], line_data[8:]))
                # values.update(additional_fields)
                self.add_invoice_line_from_values(values)
        return True

    def add_invoice_line_from_values(self, values):
        invoice = self.env['account.move'].browse(self._context.get('active_id'))
        product_name = values.get('product')
        # uom_name = values.get('uom')
        account_name = values.get('account')

        product = self.env['product.product'].search(
            ['|', ('name', '=', product_name), ('default_code', '=', product_name)], limit=1)

        account = self.env['account.account'].search(
            ['|', '|', '|', ('name', '=', account_name), ('code', '=', account_name.rsplit(' ')[0]),
             ('code', '=', account_name.rsplit('.')[0]),
             ('code', '=', account_name)])

        # if not product and not account:
        # msg = ''
        # if invoice.move_type == 'out_invoice':
        #     msg += "Revenue code"
        # elif invoice.move_type == 'in_invoice':
        #     msg += "Expense code"
        # # move_type = 'out_invoice': then revenue code
        # raise ValidationError(_('{} {} not found in your system'.format(product_name, msg)))
        if product:
            product_id = product.id
        else:
            product_id = False

        if not account and not product:
            if self.env.context.get('default_move_type') == 'in_invoice':
                account = product.property_account_expense_id
            if self.env.context.get('default_move_type') == 'out_invoice':
                account = product.property_account_income_id
            # raise ValidationError(_('Account "%s" not found in your system') % values.get('account'))
        if not account and not account_name:
            raise ValidationError("Account is required for importing lines")
        elif not account and account_name:
            raise ValidationError(_('"%s" Account not found in the system') % account_name.rsplit(' ')[0])
        # uom_record = self.env['uom.uom'].search([('name', '=', uom_name)])
        # if not uom_record:
        #     raise ValidationError(_('UOM "%s" is Not Available') % uom_name)

        # if self.env.context.get('default_move_type', 'out_invoice'):
        #     revenue_product_id = product_id.id
        # elif self.env.context.get('default_move_type', 'out_invoice'):
        #     product_id = product_id.id

        # tax_ids = []
        # if values.get('tax'):
        #     tax_names = values.get('tax').split(';') if ';' in values.get('tax') else values.get('tax').split(',')
        #     for name in tax_names:
        #         tax = self.env['account.tax'].search([('name', '=', name.strip()), (
        #         'type_tax_use', '=', 'sale' if invoice.move_type == 'out_invoice' else 'purchase')])
        #         if not tax:
        #             raise ValidationError(_('"%s" Tax not found in your system') % name.strip())
        #         tax_ids.append(tax.id)

        # if invoice.move_type == "out_invoice" and invoice.state == 'draft':
        #     account_id = product_id.property_account_income_id.id or product_id.categ_id.property_account_income_categ_id.id
        # elif invoice.move_type == "in_invoice" and invoice.state == 'draft':
        #     account_id = product_id.property_account_expense_id.id or product_id.categ_id.property_account_expense_categ_id.id
        if invoice.move_type not in ['out_invoice', 'in_invoice'] or invoice.state != 'draft':
            raise UserError(_('Cannot import data in validated or confirmed Invoice.'))

        line_values = {
            'account_id': account.id,
            'product_id': product_id,
            'revenue_product_id': product_id,
            'name': values.get('description'),
            'quantity': values.get('quantity'),
            # 'product_uom_id': uom_record.id,
            'price_unit': values.get('price'),
            # 'discount': values.get('disc'),
            'analytic_distribution': values.get('analytic_distribution')
        }

        # if tax_ids:
        #     line_values.update({'tax_ids': [(6, 0, tax_ids)]})

        for key in values.keys():
            model_record = self.env['ir.model'].search([('model', '=', 'account.move.line')])
            field_name = key.decode('utf-8') if isinstance(key, bytes) else key

            if field_name.startswith('x_'):
                is_special = self.check_special_character(field_name)
                if is_special:
                    technical_name = field_name.split("@")[0]
                    many2x_fields = self.env['ir.model.fields'].search(
                        [('name', '=', technical_name), ('model_id', '=', model_record.id)])
                    if many2x_fields:
                        if many2x_fields.ttype == "many2one":
                            field_value = values.get(key)
                            fetch_m2o = self.env[many2x_fields.relation].search([('name', '=', field_value)])
                            if fetch_m2o:
                                line_values.update({technical_name: fetch_m2o.id})
                            else:
                                raise ValidationError(
                                    _('%s Custom field value "%s" not available in the system') % (key, field_value))
                        elif many2x_fields.ttype == "many2many":
                            m2m_value_list = []
                            field_value = values.get(key)
                            if ';' in field_value:
                                m2m_names = field_value.split(';')
                            elif ',' in field_value:
                                m2m_names = field_value.split(',')
                            else:
                                m2m_names = field_value.split(',')
                            m2m_ids = self.env[many2x_fields.relation].search([('name', 'in', m2m_names)])
                            if m2m_ids:
                                m2m_value_list = m2m_ids.ids
                            line_values.update({technical_name: m2m_value_list})
                    else:
                        raise ValidationError(_('%s Custom field is not available in the system') % technical_name)
                else:
                    normal_fields = self.env['ir.model.fields'].search(
                        [('name', '=', field_name), ('model_id', '=', model_record.id)])
                    if normal_fields:
                        if normal_fields.ttype == 'boolean':
                            line_values.update({field_name: int(values.get(key)) == 1})
                        elif normal_fields.ttype in ['char', 'float', 'integer', 'selection', 'text']:
                            field_value = values.get(key)
                            if normal_fields.ttype == 'float':
                                field_value = float(field_value) if field_value else 0.0
                            elif normal_fields.ttype == 'integer':
                                try:
                                    field_value = int(float(field_value)) if field_value else 0
                                except ValueError:
                                    raise ValidationError(_('Wrong value %s for Integer field') % field_value)
                            line_values.update({field_name: field_value})
                    else:
                        raise ValidationError(_('%s Field is not available in the system') % field_name)

        invoice.write({'invoice_line_ids': [(0, 0, line_values)]})
        return True
