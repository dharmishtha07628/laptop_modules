# -*- coding: utf-8 -*-
###############################################################################
#
#   Cybrosys Technologies Pvt. Ltd.
#
#   Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#   Author: Aslam A K( odoo@cybrosys.com )
#
#   You can modify it under the terms of the GNU AFFERO
#   GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#   You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#   (AGPL v3) along with this program.
#   If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import fields, models, _
from odoo.exceptions import UserError


class CheckTypes(models.TransientModel):
    """Wizard model to select check type."""
    _name = "check.types"
    _description = "Check Types"

    check_format_id = fields.Many2one('check.format', string='Check Format',
                                       help='Check Print Formats')
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 help='Payee Name')
    check_amount_in_words = fields.Text(string='Amount in words',
                                         help='Check Amount in Words')
    check_date = fields.Date(string='Date', help='Check Date')
    company_id = fields.Many2one('res.company', string="company",
                                 default=lambda self: self.env.company,
                                 help='Company Name')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related='company_id.currency_id',
                                  help='Currency')
    check_amount = fields.Monetary(currency_field='currency_id',
                                    string='Amount', help='Amount to be paid')
    check_number = fields.Char(string='Check Number', help='Check sequence '
                                                           'Number')
    payment_id = fields.Many2one('account.payment', string='Payment Type',
                                 help='Payment id')

    def action_print_selected_check(self):
        """
        Print selected Check format by calling template.
        """
        if not self.check_format_id:
            raise UserError(_("Please select a Check Format."))
        self.payment_id.mark_as_sent()
        if self.check_format_id.date_remove_slashes:
            check_date = self.check_date.strftime("%d%m%Y")
        else:
            check_date = self.check_date.strftime("%d/%m/%Y")
        data = {
            'check_width': self.check_format_id.check_width,
            'check_height': self.check_format_id.check_height,
            'font_size': self.check_format_id.font_size,
            'is_account_payee': self.check_format_id.is_account_payee,
            'a_c_payee_top_margin': self.check_format_id.a_c_payee_top_margin,
            'a_c_payee_left_margin': self.check_format_id.a_c_payee_left_margin,
            'a_c_payee_width': self.check_format_id.a_c_payee_width,
            'a_c_payee_height': self.check_format_id.a_c_payee_height,
            'date_top_margin': self.check_format_id.date_top_margin,
            'date_left_margin': self.check_format_id.date_left_margin,
            'date_letter_spacing': self.check_format_id.date_letter_spacing,
            'beneficiary_top_margin': self.check_format_id.beneficiary_top_margin,
            'beneficiary_left_margin': self.check_format_id.beneficiary_left_margin,
            'amount_word_tm': self.check_format_id.amount_word_tm,
            'amount_word_lm': self.check_format_id.amount_word_lm,
            'amount_word_ls': self.check_format_id.amount_word_ls,
            'amount_digit_tm': self.check_format_id.amount_digit_tm,
            'amount_digit_lm': self.check_format_id.amount_digit_lm,
            'amount_digit_ls': self.check_format_id.amount_digit_ls,
            'partner': self.partner_id.name,
            'amount_in_words': self.check_amount_in_words,
            'amount_in_digit': self.check_amount,
            'check_date': check_date,
            'print_currency': self.check_format_id.print_currency,
            'currency_symbol': self.env.company.currency_id.symbol,
            'amount_digit_size': self.check_format_id.amount_digit_size,
            'print_check_number': self.check_format_id.print_check_number,
            'check_number': self.check_number,
            'check_no_tm': self.check_format_id.check_no_tm,
            'check_no_lm': self.check_format_id.check_no_lm
        }
        return self.env.ref(
            'odoo_print_check.print_check_action').report_action(None,
                                                                   data=data)
