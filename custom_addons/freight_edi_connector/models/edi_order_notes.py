# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class EDIOrderNotes(models.Model):
    _name = "edi.order.notes"

    # Segment Name = N1
    entity_identifier_code = fields.Selection(
        selection=[
            ('BT', 'Bill To'),
        ],
        string='Entity Identifier Code',
        required=True,
        help='Code identifying an organizational entity or a physical location (2 characters).'
    )
    name = fields.Char(
        string='Name',
        size=60,
        help='Free-form name (1-60 characters). Optional field.',
    )
    identification_code_structure = fields.Selection(
        selection=[
            ('92', 'Assigned by buyer'),
        ],
        string='Identification Code Structure',
        help='Code designating the system/method of code structure (1-2 characters). Optional field.',
    )
    identification_code = fields.Char(
        string='Identification Code',
        size=20,
        help='Code identifying a party or other code (2-20 characters). Optional field.',
    )

    # Segment Name = N2
    name_1 = fields.Char(
        string='Name 1',
        size=60,
        help='Free-form name (1-60 characters). Optional field.',
    )
    name_2 = fields.Char(
        string='Name 2',
        size=60,
        help='Free-form name (1-60 characters). Optional field.',
    )

    # Segment Name = N3
    address_1 = fields.Char(
        string='Address Line 1',
        size=55,
        help='Address information (1-55 characters). Optional field.',
    )
    address_2 = fields.Char(
        string='Address Line 2',
        size=55,
        help='Address information (1-55 characters). Optional field.',
    )

    # Segment Name = N4
    city_name = fields.Char(
        string='City Name',
        size=19,
        required=True,
        help='Free-form text for city name (2-19 characters). Mandatory field.',
    )
    state_province_code = fields.Char(
        string='State/Province Code',
        size=2,
        required=True,
        help='Code as defined by the appropriate government agency (2 characters). Mandatory field.',
    )
    postal_code = fields.Char(
        string='Postal Code',
        size=9,
        required=True,
        help='Code defining the international postal zone, excluding punctuation and blanks (4-9 characters). Mandatory field.',
    )

    # Section for relational fields to other tables
    edi_order_id = fields.Many2one('edi.order', string='EDI Order')
