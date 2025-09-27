# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_type = fields.Selection(
        selection_add=[('brokerage_customer', 'Brokerage Customer')],
        ondelete={'brokerage_customer': 'cascade'})
