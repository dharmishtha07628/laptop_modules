# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class EDILocation(models.Model):
    _name = "edi.location"

    # Segment Name = N1D
    entity_identifier_code = fields.Selection(
        [('ST', 'Ship To'),
         ('SF', 'Ship From'),
         ('SH', 'Shipper'),
         ('CN', 'Consignee')],
        string='Entity Identifier Code',
        required=True,
        help='Code identifying an organizational entity or a physical location.'
    )

    name = fields.Char(
        string='Name',
        size=60,
        help='Free-form name of the entity.'
    )

    identification_code_qualifier = fields.Selection(
        [('92', 'Assigned by buyer')],
        string='Identification Code Qualifier',
        required=True,
        help='Code designating the system/method of code structure.'
    )

    identification_code = fields.Char(
        string='Identification Code',
        required=True,
        size=20,
        help='Code identifying a party or other code.'
    )

    # Segment Name = N3D
    address_line_1 = fields.Char(
        string='Address Line 1',
        size=55,
        help='First line of address information.'
    )

    address_line_2 = fields.Char(
        string='Address Line 2',
        size=55,
        help='Second line of address information.'
    )

    # Segment Name = N4D
    city_name = fields.Char(
        string='City Name',
        required=True,
        size=19,
        help='Free-form text for the city name.'
    )

    state_province_code = fields.Char(
        string='State/Province Code',
        required=True,
        size=2,
        help='Code as defined by the appropriate government agency.'
    )

    postal_code = fields.Char(
        string='Postal Code',
        required=True,
        size=9,
        help='Code defining the international postal zone, excluding punctuation and blanks.'
    )

    # Section for relational fields to other tables
    contact_ids = fields.One2many('edi.contact', 'edi_location_id', string='Contacts')
