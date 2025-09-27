# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class BrokerageOrderStop(models.Model):
    _name = "brokerage.order.stop"
    _description = "Brokerage Order Stops"

    # Stop Information
    stop_number = fields.Integer(string="Stop Number")
    stop_type = fields.Many2one('stop.type.edi.segment', string='Stop Type')
    driver_loading = fields.Boolean(string="Driver Loading")

    # Location Section
    location_type = fields.Char(string='Location Type')
    location_id = fields.Many2one('brokerage.location', string='Location')
    is_appointment_confirmed = fields.Boolean(string="Is Appointment Confirmed")
    # neet to write the logic for is appointment required in master location

    # Timing Section
    scheduled_earliest = fields.Datetime(string="Scheduled Earliest")
    scheduled_latest = fields.Datetime(string="Scheduled Latest")
    actual_check_in_time = fields.Datetime(string="Actual Check In Time")
    actual_check_out_time = fields.Datetime(string="Actual Check Out Time")

    # Shipment Information Section
    no_of_pallets = fields.Integer(string="Number of Pallets")
    weight = fields.Float(string="Weight")
    weight_uom_id = fields.Many2one('weight.uom.edi.segment', string='Weight Unit of Measure')
    no_of_units = fields.Integer(string="Number of Units")
    no_of_units_description_id = fields.Many2one('unit.description.edi.segment', string='No Of Units Description')
    volume = fields.Float(string="Volume")
    volume_uom_id = fields.Many2one('volume.uom.edi.segment', string='Volume Unit of Measure')

    # Relational Fields
    brokerage_order_id = fields.Many2one("brokerage.order", string="Brokerage Order")
    stop_comment_ids = fields.One2many('brokerage.comment', 'brokerage_stop_id', string='Comments')
    brokerage_order_stop_reference_ids = fields.One2many('brokerage.order.stop.reference', 'brokerage_order_stop_id', string='Stops References')
    stop_detail_ids = fields.One2many('brokerage.stop.details', 'stop_id', string='Stops Details')

    # now we are not use following fields but not remove this for reference
    # # General fields
    # name = fields.Many2one('brokerage.order.stop.number', string='Stop Number')
    # stop_type_id = fields.Many2one("brokerage.stop.type", string="Stop Type")
    # driver_loading = fields.Boolean(string='Driver Loading')
    # brokerage_order_id = fields.Many2one("brokerage.order", string="Brokerage Order")
    # stop_status = fields.Selection(selection=[
    #     ('pending', 'pending'),
    #     ('ready', 'ready')], string='Status', default='pending')

    # # location related fields.
    # location_id = fields.Many2one('brokerage.location', string='Location')
    # phone = fields.Char(string='Phone', related='location_id.phone')
    # location_opening_hours = fields.Char(string='Location Opening Hours', related="location_id.location_opening_hours")
    # address = fields.Char(string='Address', related="location_id.address")
    # rate_confirmation_comment = fields.Char(string='Rate Confirmation Comment', related="location_id.rate_confirmation_comment")
    # # is_appointment_required = fields.Boolean(string='Is Appointment Required')
    # is_appointment_confirmed = fields.Boolean(string='Is Appointment Confirmed')

    # # schedule date time fields
    # scheduled_departure = fields.Datetime(string="Scheduled Date/Time")
    # actual_departure = fields.Datetime(string="Actual Date/Time")

    # # comments and warning fields
    # hot_comment = fields.Char(string='Hot Comment', help='For display comment in stop detail card in red and bold format.')
    # billing_comment = fields.Char(string='Billing Comment', help='For display comment in the brokerage invoice.')
    # dispatch_comment = fields.Char(string='Dispatch Comment', help='For display comment in dispatch time.')
    # other_comment = fields.Char(string='Other Comment', help='Extra comment.')

    # #=== CRUD METHODS ===#
    # @api.model
    # def create(self, values_list):
    #     stops = super().create(values_list)
    #     for stop in stops:
    #         number = len(stop.brokerage_order_id.brokerage_order_stop_ids)
    #         stop.name = stop.name.create({
    #             'name': 'STOP/00' + str(number),
    #             'stop_id':  stop.brokerage_order_id.id,
    #         })
    #     return stops

    # # #=== ORM METHODS ===#
    # # @api.onchange('location_id')
    # # def _onchange_location_id(self):
    # #     if self.location_id.is_appointment_required:
    # #         self.is_appointment_required = True
