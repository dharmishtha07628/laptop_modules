# -*- coding: utf-8 -*-
# Copyright (C) .

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    at_is_enable_google_api_key = fields.Boolean(
        string="Enable Google API")

    at_google_api_key = fields.Char(
        string="Key")
    
    
    at_restricted_country_ids = fields.Many2many(
        string='Restricted Countries',
        comodel_name='res.country',
    )
    

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    at_is_enable_google_api_key = fields.Boolean(
        related="company_id.at_is_enable_google_api_key",
        string="Enable Google API",
        readonly=False)

    at_google_api_key = fields.Char(
        related="company_id.at_google_api_key",
        string="Key",
        readonly=False)

    at_restricted_country_ids = fields.Many2many(
        string='Restricted Countries',
        related='company_id.at_restricted_country_ids',
        readonly=False
    )
    
