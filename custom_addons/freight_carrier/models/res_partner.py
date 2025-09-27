# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_type = fields.Selection(
        selection_add=[('transport_customer', 'Transport Customer')],
        ondelete={'transport_customer': 'cascade'})
