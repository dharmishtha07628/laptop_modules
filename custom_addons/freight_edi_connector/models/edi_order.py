# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EDIOrder(models.Model):
    _name = "edi.order"
    _description = "EDI Order"
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
    ]

    '''
    EDI data tables are based on perticular segments
    so here we are manage all the fields in perticular segments.
    for check the official website if any query regarding table structure : https://www.stedi.com/edi/x12/
    '''

    # Segment Name = ST
    transaction_set_identifier_code = fields.Selection(
        selection=[('204', 'Motor Carrier Load Tender')],
        string='Transaction Set Identifier Code',
        required=True,
        help='Code uniquely identifying a transaction set (3 characters).'
    )
    transaction_set_control_number = fields.Char(
        string='Transaction Set Control Number',
        required=True,
        size=9,
        help='Identifying control number that must be unique within the transaction set functional group, assigned by the originator for a transaction set (4-9 characters).'
    )
    # implementation_convention_reference = fields.Char(string='Implementation Convention Reference') may be we use this later 

    # Segment Name = B2
    standard_carrier_alpha_code = fields.Char(
        string='Standard Carrier Alpha Code',
        required=True,
        size=4,
        help='Standard Carrier Alpha Code (2-4 characters).'
    )
    shipment_identification_number = fields.Char(
        string='Shipment Identification Number',
        required=True,
        size=30,
        help='Identification number assigned to the shipment by the shipper that uniquely identifies the shipment from origin to ultimate destination (1-30 characters).'
    )
    shipment_method_of_payment = fields.Selection(
        selection=[
            ('CC', 'Collect'),
            ('PP', 'Prepaid (by seller)'),
            ('TP', 'Third Party Pay'),
        ],
        string='Shipment Method of Payment',
        required=True,
        help='Code identifying payment terms for transportation charges.'
    )

    # Segment Name = B2A
    transaction_set_purpose_code = fields.Selection(
        selection=[
            ('00', 'Original'),
            ('01', 'Cancellation'),
            ('18', 'Reissue'),
        ],
        string='Transaction Set Purpose Code',
        required=True,
        help='Code identifying the purpose of the transaction set (2 characters).'
    )
    application_type = fields.Selection(
        selection=[
            ('LT', 'Load Tender'),
        ],
        string='Application Type',
        help='Code identifying the application (optional field).'
    )    

    # Segment Name = G62H
    date_time_qualifier = fields.Selection(
        selection=[
            ('64', 'Must respond by'),
        ],
        string='Date/Time Qualifier',
        required=True,
        help='Code specifying the type of date/time (2 characters).'
    )
    date = fields.Date(
        string='Date',
        help='Date in the format YYYYMMDD. Optional field.',
    )
    time_qualifier = fields.Selection(
        selection=[
            ('1', 'Must respond by'),
        ],
        string='Time Qualifier',
        help='Code specifying the report time (1-2 characters). Optional field.',
    )
    time = fields.Char(
        string='Time',
        size=8,
        help='Time in the format HHMMSSDD. Optional field.',
    )

    # Section for relational fields to other tables
    edi_order_reference_ids = fields.One2many('edi.order.reference', 'edi_order_id', string='Order References')
    edi_order_note_ids = fields.One2many('edi.order.notes', 'edi_order_id', string='Order Notes')
    edi_order_stop_ids = fields.One2many('edi.order.stops', 'edi_order_id', string='Order Stops')
    edi_order_summary_ids = fields.One2many('edi.order.stops', 'edi_order_id', string='Order Stops')
