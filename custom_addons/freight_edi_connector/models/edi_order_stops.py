# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class EDIOrderStops(models.Model):
    _name = "edi.order.stops"

    # Segment Name = S5
    stop_sequence_number = fields.Integer(
        string='Stop Sequence Number', 
        required=True, 
        help='Identifying number for specific stop and in which order the stop is to be performed.'
    )

    stop_reason_code = fields.Selection(
        [('CL', 'Complete Load'),
         ('CU', 'Complete Unload'),
         ('LD', 'Load'),
         ('PL', 'Part Load'),
         ('PU', 'Part Unload')],
        string='Stop Reason Code', 
        required=True, 
        help='Code specifying the reason for the stop.'
    )

    weight = fields.Float(
        string='Weight', 
        digits=(10, 2), 
        help='Numeric value of weight.'
    )

    weight_unit_code = fields.Char(
        string='Weight Unit Code', 
        size=1, 
        help='Code specifying the weight unit.'
    )

    number_of_units_shipped = fields.Integer(
        string='Number of Units Shipped', 
        help='Numeric value of units shipped in units for a line item or transaction set.'
    )

    unit_or_basic_for_measurement_code = fields.Char(
        string='Unit or Basic for Measurement Code', 
        size=2, 
        help='Code specifying the units in which a value is being expressed or manner in which a measurement has been taken.'
    )

    volume = fields.Float(
        string='Volume', 
        digits=(8, 2), 
        help='Value of volumetric measure.'
    )

    volume_unit_qualifier = fields.Char(
        string='Volume Unit Qualifier', 
        size=1, 
        help='Code identifying the volume unit.'
    )

    # Segment Name = L11D
    reference_identification = fields.Char(
        string='Reference Identification',
        size=30,
        help='Reference information as defined for a particular Transaction set or as specified by the reference qualifier.'
    )

    reference_indent_qualifier = fields.Selection(
        [('KD', 'Special Instructions')],
        string='Reference Identification Qualifier',
        size=3,
        help='Code qualifying the Reference Identification. Example: KD for Special Instructions.'
    )

    description = fields.Char(
        string='Description',
        size=80,
        help='A free-form description to clarify the related data elements.'
    )

    # Segment Name = PLD
    quantity_of_pallet_ship = fields.Integer(
        string='Quantity of Pallet Ship',
        required=True,
        help='Number of pallets shipped. Must be a whole number between 1 and 999.'
    )

    # Segment Name = G62D
    earliest_date_time_qualifier = fields.Selection(
        [('37', 'Ship not before date'),
         ('53', 'Deliver not before date')],
        string='Date/Time Qualifier',
        required=True,
        help='Code specifying the type of date/time.'
    )

    earliest_date = fields.Date(
        string='Date',
        help='Date in the format YYYYMMDD.'
    )

    earliest_time_qualifier = fields.Selection(
        [('I', 'Earliest Requested Pick up Time'),
         ('G', 'Earliest Requested Deliver Time')],
        string='Time Qualifier',
        help='Code specifying the report time.'
    )

    earliest_time = fields.Char(
        string='Time',
        size=8,
        help='Time in the format HHMMSSDD.'
    )

    # Segment Name = G62L
    latest_date_time_qualifier = fields.Selection(
        [('38', 'Ship not later than date'),
         ('54', 'Deliver no later than date')],
        string='Date/Time Qualifier',
        required=True,
        help='Code specifying the type of date/time.'
    )

    latest_date = fields.Date(
        string='Date',
        help='Date in the format YYYYMMDD.'
    )

    latest_time_qualifier = fields.Selection(
        [('K', 'Latest Requested Pick up Time'),
         ('L', 'Latest Requested Delivery Time')],
        string='Time Qualifier',
        help='Code specifying the report time.'
    )

    latest_time = fields.Char(
        string='Time',
        size=8,
        help='Time in the format HHMMSSDD.'
    )

    # Section for relational fields to other tables
    edi_order_id = fields.Many2one('edi.order', string='EDI Order')
    edi_stop_detail_ids = fields.One2many('edi.stop.detail', 'edi_stop_id', string='Stops Details')
    edi_location_id = fields.Many2one('edi.location', string='Location')
