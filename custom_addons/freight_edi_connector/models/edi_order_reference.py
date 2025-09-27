# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class EDIOrderReference(models.Model):
    _name = "edi.order.reference"

    # Segment Name = L11
    reference_identification = fields.Char(
        string='Reference Identification',
        size=30,
        help='Reference information as defined for a particular transaction set or as specified by the reference qualifier (1-30 characters).',
    )
    reference_ident_qualifier = fields.Selection(
        selection=[
            ('IL', 'Order Number'),
            ('MI', 'Trip Mileage'),
            ('VE', 'Vendor Number'),
            ('KL', 'Contact Reference'),
            ('MB', 'Bill of Lading'),
            ('WT', 'Reference Number'),
            ('QN', 'Carrier Multi Stop (Y/N)'),
            ('SI', 'Shipper ID Number'),
            ('BM', 'Manifest # / DC BOL #'),
            ('EV', 'Trailer ID Number'),
            ('MCI', 'Manugistics Carrier ID'),
            ('CMN', 'Move Sequence Number'),
            ('CN', 'Carrier PRO Number'),
        ],
        string='Reference Ident Qualifier',
        help='Code qualifying the Reference Identification (2-3 characters).',
    )

    # Section for relational fields to other tables
    edi_order_id = fields.Many2one('edi.order', string='EDI Order')
