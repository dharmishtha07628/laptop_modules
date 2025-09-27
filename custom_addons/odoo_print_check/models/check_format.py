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
from odoo import fields, models


class CheckFormat(models.Model):
    """ Configure check print template."""
    _name = 'check.format'
    _description = 'Check Format'
    _rec_name = 'bank_name'

    bank_name = fields.Char(string='Bank Name',
                            help='Enter the name of the bank.',
                            required=True)
    font_size = fields.Float(string='Font Size',
                             help='Total font size for the text.')
    check_width = fields.Float(string='Width', help='Width of the check.')
    check_height = fields.Float(string='Height', help='Height of the check.')
    print_check_number = fields.Boolean(string='Print Check Number',
                                         help='Enable to print the check '
                                              'sequence number. '
                                              'You can adjust this if the '
                                              'numbering is incorrect.')
    check_no_tm = fields.Float(string='Check No: Top Margin',
                                help="Top margin for the check number.")
    check_no_lm = fields.Float(string='Check No: Left Margin',
                                help="Left margin for the check number.")
    is_account_payee = fields.Boolean(string="Crossed Account Payee Check",
                                      help="Select to make the check a "
                                           "Crossed Account Payee check. "
                                           "Prints ‘A/C Payee Only’ between "
                                           "parallel crossing lines.")
    a_c_payee_top_margin = fields.Float(string='Payee Top Margin',
                                        help="Top margin for the 'A/C Payee' "
                                             "text.")
    a_c_payee_left_margin = fields.Float(string="Payee Left Margin",
                                         help="Left margin for the 'A/C Payee'"
                                              " text.")
    a_c_payee_width = fields.Float(string="Payee Width",
                                   help="Width of the 'A/C Payee' text.")
    a_c_payee_height = fields.Float(string="Payee Height",
                                    help="Height of the 'A/C Payee' text.")
    date_remove_slashes = fields.Boolean(string="Remove Slashes",
                                         help="Enable to remove slashes from"
                                              " the date.")
    date_top_margin = fields.Float(string="Date Top Margin",
                                   help="Top margin for the date.")
    date_left_margin = fields.Float(string="Date Left Margin",
                                    help="Left margin for the date.")
    date_letter_spacing = fields.Float(string="Date Letter Spacing",
                                       help="Spacing between date characters.")
    beneficiary_top_margin = fields.Float(string="Beneficiary Top Margin",
                                          help="Top margin for the beneficiary"
                                               " name.")
    beneficiary_left_margin = fields.Float(string="Beneficiary Left Margin",
                                           help="Left margin for the "
                                                "beneficiary name.")
    amount_word_tm = fields.Float(string="Amount in Words Top Margin",
                                  help="Top margin for the amount in words.")
    amount_word_lm = fields.Float(string="Amount in Words Left Margin",
                                  help="Left margin for the amount in words.")
    amount_word_ls = fields.Float(string="Amount in Words Letter Spacing",
                                  help="Spacing between characters in the "
                                       "amount in words.")
    print_currency = fields.Boolean(string="Print Currency Symbol",
                                    help="Enable to print the currency symbol."
                                         "")
    amount_digit_tm = fields.Float(string="Amount in Digits Top Margin",
                                   help="Top margin for the amount in digits."
                                        "")
    amount_digit_lm = fields.Float(string="Amount in Digits Left Margin",
                                   help="Left margin for the amount in digits."
                                        "")
    amount_digit_ls = fields.Float(string="Amount in Digits Letter Spacing",
                                   help="Spacing between characters in the "
                                        "amount in digits.")
    amount_digit_size = fields.Float(string="Amount in Digits Font Size",
                                     help="Font size for the amount in digits"
                                          ".")

    def action_print_test(self):
        """
        Print a test check to make corrections for the user in check format.
        """
        data = {
            'check_width': self.check_width,
            'check_height': self.check_height,
            'font_size': self.font_size,
            'print_check_number': self.print_check_number,
            'check_no_tm': self.check_no_tm,
            'check_no_lm': self.check_no_lm,
            'is_account_payee': self.is_account_payee,
            'a_c_payee_top_margin': self.a_c_payee_top_margin,
            'a_c_payee_left_margin': self.a_c_payee_left_margin,
            'a_c_payee_width': self.a_c_payee_width,
            'a_c_payee_height': self.a_c_payee_height,
            'date_top_margin': self.date_top_margin,
            'date_left_margin': self.date_left_margin,
            'date_letter_spacing': self.date_letter_spacing,
            'beneficiary_top_margin': self.beneficiary_top_margin,
            'beneficiary_left_margin': self.beneficiary_left_margin,
            'amount_word_tm': self.amount_word_tm,
            'amount_word_lm': self.amount_word_lm,
            'amount_word_ls': self.amount_word_ls,
            'amount_digit_tm': self.amount_digit_tm,
            'amount_digit_lm': self.amount_digit_lm,
            'amount_digit_ls': self.amount_digit_ls,
            'amount_digit_size': self.amount_digit_size,
            'print_currency': self.print_currency,
            'currency_symbol': self.env.company.currency_id.symbol,
            'date_remove_slashes': self.date_remove_slashes
        }
        return self.env.ref(
            'odoo_print_check.test_check_action').report_action(None,
                                                                  data=data)
