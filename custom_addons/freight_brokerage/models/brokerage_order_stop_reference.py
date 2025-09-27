# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BrokerageOrderStopReference(models.Model):
    _name = "brokerage.order.stop.reference"
    _description = "Brokerage Order Stop Reference"

    reference_identification_qualifier = fields.Many2one('reference.identification.qualifier.edi.segment', string='Reference Identification Qualifier')
    reference = fields.Char(string='Reference')

    brokerage_order_stop_id = fields.Many2one('brokerage.order.stop', string='Brokerage Order Stop')
