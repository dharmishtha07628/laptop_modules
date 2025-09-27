# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions
from datetime import datetime, timedelta
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
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

keys = ['date', 'payment_ref', 'ref', 'partner_id', 'amount', 'currency_id']


class ImportInvoiceWizard(models.TransientModel):
    _name = 'import.budget.wizard'
    _description = "Import Budget Wizard"

    attachment_ids = fields.Many2many('ir.attachment', string='Files', required=True,
                                      help='Get you bank statements in electronic format from your bank and'
                                           ' select them here.')
    mapping_ids = fields.One2many('account.budget.import.mapping', 'statement_import_id', string='Mapping IDs')

    @api.onchange('attachment_ids')
    def _onchange_attachment_ids(self):
        file_columns = self.get_file_columns()
        if file_columns:
            mapping_data = [fields.Command.clear()]
            suggested_fields = self._get_field_suggession(file_columns)
            mapping_data += [
                fields.Command.create({'name': line, 'field_id': suggested_fields[i]})
                for i, line in enumerate(file_columns)
            ]
            self.mapping_ids = mapping_data

    def get_file_columns(self):
        for data_file in self.attachment_ids:
            file_name = data_file.name.lower()
            try:
                if file_name.strip().endswith('.csv') or file_name.strip().endswith('.xlsx'):
                    if file_name.strip().endswith('.csv'):
                        try:
                            csv_data = base64.b64decode(data_file.datas)
                            data_file = io.StringIO(csv_data.decode("utf-8"))
                            data_file.seek(0)
                            file_reader = []
                            csv_reader = csv.reader(data_file, delimiter=',')
                            file_reader.extend(csv_reader)
                        except:
                            raise UserError(_("Invalid file!"))
                        return file_reader[0]
                    elif file_name.strip().endswith('.xlsx'):
                        try:
                            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                            fp.write(binascii.a2b_base64(data_file.datas))
                            fp.seek(0)
                            workbook = xlrd.open_workbook(fp.name)
                            sheet = workbook.sheet_by_index(0)
                        except:
                            raise UserError(_("Invalid file!"))
                        fields = list(map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(
                            row.value), sheet.row(0)))
                        return fields
                else:
                    raise ValidationError(_("Unsupported File Type"))
            except Exception as e:
                raise ValidationError(_(e))  # "Please upload in specified format ! \n"
                # "date, payment reference, reference, partner, amount, currency !"))

    def _get_field_suggession(self, file_columns):
        suggested_field_list = []
        for column in file_columns:
            if column == 'BUDGET REPORTING GROUP':
                suggested_field_list.append(self.env.ref('om_account_budget.field_crossovered_budget_lines__general_budget_id').id)
            elif column == 'ANALYTIC ACCOUNT':
                suggested_field_list.append(self.env.ref('om_account_budget.field_crossovered_budget_lines__analytic_account_id').id)
            elif column == 'START DATE':
                suggested_field_list.append(self.env.ref('om_account_budget.field_crossovered_budget_lines__date_from').id)
            elif column == 'END DATE':
                suggested_field_list.append(self.env.ref('om_account_budget.field_crossovered_budget_lines__date_to').id)
            elif column == 'PAID DATE':
                suggested_field_list.append(self.env.ref('om_account_budget.field_crossovered_budget_lines__paid_date').id)
            elif column == 'PLANNED AMOUNT':
                suggested_field_list.append(self.env.ref('om_account_budget.field_crossovered_budget_lines__planned_amount').id)
            elif column == 'PRACTICAL AMOUNT':
                suggested_field_list.append(self.env.ref('om_account_budget.field_crossovered_budget_lines__practical_amount').id)
            elif column == 'THEORETICAL AMOUNT':
                suggested_field_list.append(self.env.ref('om_account_budget.field_crossovered_budget_lines__theoritical_amount').id)
            elif column == 'ACHIEVEMENT':
                suggested_field_list.append(self.env.ref('om_account_budget.field_crossovered_budget_lines__percentage').id)
            else:
                suggested_field_list.append('')
        return suggested_field_list

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
        for data_file in self.attachment_ids:
            file_name = data_file.name.lower()
            try:
                if file_name.strip().endswith('.csv') or file_name.strip().endswith('.xlsx'):
                    statement = False
                    keys = self.mapping_ids.mapped('field_name')
                    if file_name.strip().endswith('.xlsx'):
                          fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                          fp.write(binascii.a2b_base64(data_file.datas))
                          fp.seek(0)
                          values = {}
                          workbook = xlrd.open_workbook(fp.name)
                          sheet = workbook.sheet_by_index(0)
                          vals_list = []
                          for row_no in range(1, sheet.nrows):
                                line = list(map(
                                    lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(
                                        row.value), sheet.row(row_no)))
                                values = dict(zip(keys, line))
                                print(values)
                                values.update({
                                    'general_budget_id':self.get_budget_report(values.get('general_budget_id')),
                                    'analytic_account_id':self.get_analytic_line(values.get('analytic_account_id')),
                                    'date_from': self.convert_date(values.get('date_from')),
                                    'date_to': self.convert_date(values.get('date_to')),
                                    'paid_date': self.convert_date(values.get('paid_date')),
                                    'planned_amount': float(values.get('planned_amount') or 0),
                                    'practical_amount': float(values.get('practical_amount') or 0),
                                    'theoritical_amount': float(values.get('theoritical_amount') or 0),
                                    'percentage': float(values.get('percentage') or 0),
                                    'crossovered_budget_id': self.env.context.get('active_id')
                                })
                                self.env['crossovered.budget.lines'].create(values)
                if file_name.strip().endswith('.csv'):
                    try:
                        csv_data = base64.b64decode(data_file.datas)
                        data_file = io.StringIO(csv_data.decode("utf-8"))
                        data_file.seek(0)
                        file_reader = []
                        values = {}
                        csv_reader = csv.reader(data_file, delimiter=',')
                        file_reader.extend(csv_reader)
                    except:
                        raise UserError(_("Invalid file!"))
                    vals_list = []
                    date = False
                    for i in range(1, len(file_reader)):
                        field = list(map(str, file_reader[i]))
                        values = dict(zip(keys, field))
                        # print(">>>>>>>>>>>> values", values)
                        if values:
                            # if i == 0:
                            #     continue
                            # else:
                            if not date:
                                date = field[0]
                            values.update({
                                'general_budget_id': self.get_budget_report(values.get('general_budget_id')),
                                'analytic_account_id': self.get_analytic_line(values.get('analytic_account_id')),
                                'date_from': self.convert_date(values.get('date_from')),
                                'date_to': self.convert_date(values.get('date_to')),
                                'paid_date': self.convert_date(values.get('paid_date')),
                                'planned_amount': float(values.get('planned_amount') or 0),
                                'practical_amount': float(values.get('practical_amount') or 0),
                                'theoritical_amount': float(values.get('theoritical_amount') or 0),
                                'percentage': float(values.get('percentage') or 0),
                                'crossovered_budget_id': self.env.context.get('active_id')
                            })
                            self.env['crossovered.budget.lines'].create(values)
            except Exception as e:
                raise ValidationError(_(e))
    def get_budget_report(self, data):
        bud_repo = self.env['account.budget.post'].search([('name', '=ilike', data)])
        return bud_repo.id if bud_repo else False

    def get_analytic_line(self, data):
        account_any = self.env['account.analytic.account'].search([('name', '=ilike', data)])
        return account_any.id if account_any else False

    def convert_date(self, date):
        """
        Convert a numeric date (days since 1900-01-01) or a standard date string (YYYY-MM-DD) to Odoo date format (YYYY-MM-DD).
        If the date is empty, return None.

        :param date: Numeric date string (e.g., '45508.0'), standard date string (e.g., '2024-08-04'), or an empty string
        :return: Converted date in 'YYYY-MM-DD' format or None if the input is empty
        """
        if not date:
            return None  # Return None instead of an empty string if date is empty

        try:
            # Try converting from a numeric date string
            date_num = float(date)

            # Define the epoch (starting point) as January 1, 1900
            epoch = datetime(1900, 1, 1)

            # Convert the numeric date to an actual date
            converted_date = epoch + timedelta(days=date_num - 2)

            # Format the date as 'YYYY-MM-DD'
            con_date = converted_date.strftime('%Y-%m-%d')

        except ValueError:
            # If conversion fails, assume it's a standard date string
            try:
                # Parse the standard date string
                parsed_date = datetime.strptime(date, '%Y-%m-%d')
                con_date = parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                # Handle unexpected date format
                return None

        return con_date

    def add_invoice_line_from_values(self, values):
        invoice = self.env['account.move'].browse(self._context.get('active_id'))
        product_name = values.get('product')
        # uom_name = values.get('uom')
        account_name = values.get('account')

        product = self.env['product.product'].search([('name', '=', product_name)], limit=1)

        account = self.env['account.account'].search([('code', '=', account_name.rsplit(' ')[0])])

        if not account:
            raise ValidationError(_('Account "%s" not found in your system') % values.get('account'))

        # uom_record = self.env['uom.uom'].search([('name', '=', uom_name)])
        # if not uom_record:
        #     raise ValidationError(_('UOM "%s" is Not Available') % uom_name)

        if not product:
            raise ValidationError(_('"%s" Product not found in your system') % product_name)
        else:
            product_id = product

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
            'product_id': product_id.id,
            'revenue_product_id': product_id.id,
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


class AccountBudgetImportMapping(models.TransientModel):
    _name = 'account.budget.import.mapping'
    _description = 'Use this model for fields mapping dynamically'

    name = fields.Char(string='File Column')
    field_id = fields.Many2one('ir.model.fields', domain=[('model_id', '=', 'crossovered.budget.lines'), ('name', 'in', keys)], string='System Field')
    field_name = fields.Char(string='Filed Name', related='field_id.name')
    statement_import_id = fields.Many2one('import.budget.wizard', string='Statement Id')
