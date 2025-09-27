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
from odoo import models


class AccountPayment(models.Model):
    """
    This class inherits from the 'account.payment' model to add specific
    features and behavior related to printing checks and handling payment
    information. It overrides the 'print_checks' method to provide a custom
    wizard view for selecting and formatting check printing options.
    """
    _inherit = 'account.payment'

    def print_checks(self):
        """
        Overriding print_checks button to generate a wizard view to print
        check by selecting a check print format.
        """
        if self.payment_method_line_id.payment_method_id.name == 'Checks':
            check_date = self.date
        elif self.payment_method_line_id.payment_method_id.name == 'PDC':
            check_date = self.effective_date
        return {
            'name': "Check Format",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'check.types',
            'target': 'new',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_check_amount_in_words': self.check_amount_in_words,
                'default_check_date': check_date,
                'default_check_amount': self.amount,
                'default_check_number': self.check_number,
                'default_payment_id': self.id
            }
        }
