# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BrokerageComment(models.Model):
    _name = "brokerage.comment"
    _description = "Brokerage Comment"

    comment_type = fields.Selection(
        selection=[
            ('hot', 'Hot'),
            ('billing', 'Billing'),
            ('dispatch', 'Dispatch'),
            ('other', 'Other')
        ], string='Comment Type')
    comment_description = fields.Char(string='Comment Description')
    brokerage_order_id = fields.Many2one("brokerage.order", string="Brokerage Order")
    brokerage_stop_id = fields.Many2one("brokerage.order.stop", string="Brokerage Order Stop")
    brokerage_location_id = fields.Many2one("brokerage.location", string="Brokerage Location")
