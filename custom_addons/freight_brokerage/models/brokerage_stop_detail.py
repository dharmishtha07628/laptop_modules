# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BrokerageStopDetails(models.Model):
    _name = "brokerage.stop.details"
    _description = "Brokerage Stop Details"
    _rec_name = 'customer_reference_id'

    customer_reference_id = fields.Char(string='Customer Reference ID')
    customer_po_number = fields.Char(string='Customer PO Number')
    customer_delivery_po = fields.Char(string='Customer Delivery PO')
    quantity = fields.Float(string='Quantity')
    unit_description = fields.Char(string='Unit Description')
    weight = fields.Float(string='Weight')
    weight_uom = fields.Char(string='Weight UOM')
    volume = fields.Float(string='Volume')
    volume_uom = fields.Char(string='Volume UOM')

    # Relational Fields
    stop_id = fields.Many2one('brokerage.order.stop', string='Brokerage Order Stop')
