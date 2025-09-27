# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class EDIStopDetail(models.Model):
    _name = "edi.stop.detail"

    # Segment Name = OID
    reference_identification = fields.Char(
        string='Reference Identification',
        size=30,
        help='Code specifying the weight unit.'
    )

    division_code = fields.Char(
        string='Division Code',
        help='Division code as defined in the Division Code Appendix.'
    )

    purchase_order_number = fields.Char(
        string='Purchase Order Number',
        size=22,
        help='Code defining the type of weight.'
    )

    delivery_order_id = fields.Char(
        string='Delivery Order ID',
        help='Unique ID for the delivery order.'
    )

    unit_measurement_code = fields.Selection(
        [
            ('LB', 'Pounds'),
            ('KG', 'Kilograms'),
            ('EA', 'Each'),
        ],
        string='Unit or Basis for Measurement Code',
        help='Code specifying the units in which a value is being expressed, or manner in which a measurement has been taken.'
    )

    quantity = fields.Float(
        string='Quantity',
        digits=(15, 3),
        help='Numeric value of quantity.'
    )

    weight_unit_code = fields.Selection(
        [
            ('L', 'Pounds'),
            ('K', 'Kilograms'),
        ],
        string='Weight Unit Code',
        help='Code specifying the weight unit.'
    )

    weight = fields.Float(
        string='Weight',
        digits=(10, 2),
        help='Numeric value of weight.'
    )

    volume_unit_qualifier = fields.Selection(
        [
            ('E', 'Cubic Feet'),
            ('M', 'Cubic Meters'),
        ],
        string='Volume Unit Qualifier',
        help='Code identifying the volume unit.'
    )

    volume = fields.Float(
        string='Volume',
        digits=(8, 2),
        help='Value of volumetric measure.'
    )

    # Section for relational fields to other tables
    edi_stop_id = fields.Many2one('edi.order.stops', string='EDI Stops')
