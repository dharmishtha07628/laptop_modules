# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class EDIContact(models.Model):
    _name = "edi.contact"

    contact_function_code = fields.Selection(
        [
            ('RE', 'Receiving Contact'),
            ('SD', 'Shipping Department'),
            ('SH', 'Shipper Contact'),
            ('ZZ', 'Mutually Defined'),
        ],
        string='Contact Function Code',
        required=True,
        help='Code identifying the duty or responsibility of the person or group named.'
    )

    name = fields.Char(
        string='Name',
        required=True,
        size=60,
        help='Free-form name.'
    )

    communication_number_qualifier = fields.Selection(
        [
            ('TE', 'Telephone'),
            ('EM', 'Email Address'),
        ],
        string='Communication Number Qualifier',
        help='Code identifying the type of communication number.'
    )

    communication_number = fields.Char(
        string='Communication Number',
        size=80,
        help='Complete communication number including country or area code, or email address.'
    )

    contact_inquiry_reference = fields.Char(
        string='Contact Inquiry Reference',
        size=20,
        help='Additional reference number or description to clarify a contact number.'
    )

    # Section for relational fields to other tables
    edi_location_id = fields.Many2one('edi.location', string='Location')
