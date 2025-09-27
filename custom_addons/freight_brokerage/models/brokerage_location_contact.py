# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class BrokerageLocationContact(models.Model):
    _name = "brokerage.location.contact"
    _description = "Brokerage Location Contact"

    location_contact_type = fields.Char(string='Contact Type')
    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    references = fields.Text(string='References')
    location_id = fields.Many2one('brokerage.location', string='Brokerage Location')
