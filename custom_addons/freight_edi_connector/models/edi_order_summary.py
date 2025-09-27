# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class EDIOrderSummary(models.Model):
    _name = "edi.order.summary"

    # Segment Name = L3
    weight = fields.Float(
        string='Weight',
        digits=(10, 2),
        help='Numeric value of the weight.'
    )

    weight_qualifier = fields.Selection(
        [
            ('G', 'Gross Weight'),
        ],
        string='Weight Qualifier',
        help='Code defining the type of weight.'
    )

    charges = fields.Monetary(
        string='Charges',
        currency_field='currency_id',
        digits=(12, 2),
        help='Freight or special charges expressed in the standard monetary denomination.'
    )

    volume = fields.Float(
        string='Volume',
        digits=(8, 0),
        help='Value of volumetric measure.'
    )

    volume_qualifier = fields.Selection(
        [
            ('E', 'Cubic Feet'),
        ],
        string='Volume Qualifier',
        help='Code identifying the volume unit.'
    )

    lading_quantity = fields.Integer(
        string='Lading Quantity',
        help='Number of units (pieces) of the lading commodity.'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        help='Currency used for charges.'
    )

    # Segment Name = S3
    num_included_segments = fields.Integer(
        string="Number of Included Segments", 
        required=True, 
        help="Total number of segments included in the transaction set, including ST and SE segments.",
        default=1
    )

    transaction_set_control_number = fields.Char(
        string="Transaction Set Control Number", 
        required=True, 
        help="Identifying control number that must be unique within the transaction set functional group.",
        size=9
    )

    # Section for relational fields to other tables
    edi_order_id = fields.Many2one('edi.order', string='EDI Order')
