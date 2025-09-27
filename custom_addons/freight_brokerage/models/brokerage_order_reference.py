# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BrokerageOrderReference(models.Model):
    _name = "brokerage.order.reference"
    _description = "Brokerage Order Reference"

    reference_identification_qualifier = fields.Many2one('reference.identification.qualifier.edi.segment', string='Reference Identification Qualifier')
    reference = fields.Char(string='Reference')

    brokerage_order_id = fields.Many2one('brokerage.order', string='Brokerage Order')
