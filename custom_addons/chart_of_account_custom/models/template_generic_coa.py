from odoo import models, _
from odoo.addons.account.models.chart_template import template



class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template('generic_coa')
    def _get_generic_coa_template_data(self):
        """Return the data necessary for the chart template.

        :return: all the values that are not stored but are used to instancieate
                 the chart of accounts. Common keys are:
                 * property_*
                 * code_digits
        :rtype: dict
        """
        return {
            'name': _("United States of America (Generic)"),
            'country': None,
            'property_account_receivable_id': 'receivable',
            'property_account_payable_id': 'payable',
            'property_account_expense_categ_id': 'expense',
            'property_account_income_categ_id': 'income',
            'property_stock_account_input_categ_id': 'stock_in',
            'property_stock_account_output_categ_id': 'stock_out',
            'property_stock_valuation_account_id': 'stock_valuation',
            'property_stock_account_production_cost_id': 'cost_of_production',
        }

    @template('generic_coa', 'res.company')
    def _get_generic_coa_res_company(self):
        """Return the data to be written on the company.

        The data is a mapping the XMLID to the create/write values of a record.

        :rtype: dict[(str, int), dict]
        """
        return {
            self.env.company.id: {
                'anglo_saxon_accounting': True,
                'account_fiscal_country_id': 'base.us',
                'bank_account_code_prefix': '1014',
                'cash_account_code_prefix': '1015',
                'transfer_account_code_prefix': '1017',
                'account_default_pos_receivable_account_id': 'pos_receivable',
                'income_currency_exchange_account_id': 'income_currency_exchange',
                'expense_currency_exchange_account_id': 'expense_currency_exchange',
                'default_cash_difference_income_account_id': 'cash_diff_income',
                'default_cash_difference_expense_account_id': 'cash_diff_expense',
                'account_journal_early_pay_discount_loss_account_id': 'cash_discount_loss',
                'account_journal_early_pay_discount_gain_account_id': 'cash_discount_gain',
            }
        }


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template(model='account.journal')
    def _get_account_journal(self, template_code):
        return {
            "sale": {
                'name': _('Customer Invoices'),
                'type': 'sale',
                'code': _('INV'),
                'show_on_dashboard': True,
                'color': 11,
                'sequence': 5,
            },
            "purchase": {
                'name': _('Vendor Bills'),
                'type': 'purchase',
                'code': _('BILL'),
                'show_on_dashboard': True,
                'color': 11,
                'sequence': 6,
            },
            "general": {
                'name': _('Journal Entry'),
                'type': 'general',
                'code': _('JE'),
                'show_on_dashboard': True,
                'sequence': 7,
            },
            "exch": {
                'name': _('Exchange Difference'),
                'type': 'general',
                'code': _('EXCH'),
                'show_on_dashboard': False,
                'sequence': 9,
            },
            "caba": {
                'name': _('Cash Basis Taxes'),
                'type': 'general',
                'code': _('CABA'),
                'show_on_dashboard': False,
                'sequence': 10,
            },
            "bank": {
                'name': _('Bank'),
                'type': 'bank',
                'show_on_dashboard': True,
            },
            "cash": {
                'name': _('Cash'),
                'type': 'cash',
                'show_on_dashboard': True,
            },
        }
