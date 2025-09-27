# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
import json


class BrokerageLocation(models.Model):
    _inherit = "brokerage.location"
    _description = "Brokerage Location"

    at_contact_google_location = fields.Char('Enter Location')

    at_contact_place_text = fields.Char('Enter location', copy=False)
    at_contact_place_text_main_string = fields.Char(
        'Enter location ', copy=False)

    @api.onchange('at_contact_place_text_main_string')
    def onchange_technical_google_text_main_string(self):
        """to save name in google field"""
        if self.at_contact_place_text_main_string:
            self.at_contact_google_location = self.at_contact_place_text_main_string

    @api.onchange('at_contact_place_text')
    def onchange_technical_google_text(self):
        """to place info to std. address fields"""
        if self.at_contact_place_text:
            google_place_dict = json.loads(self.at_contact_place_text)
            if google_place_dict:
                self.zip_code = google_place_dict.get('zip', '')
                self.address = google_place_dict.get('formatted_street',
                                                    '') or f'{google_place_dict.get("number", "")} {google_place_dict.get("street", "")}'
                # self.location_code = google_place_dict.get('country_code', '')
                # self.name = google_place_dict.get('formatted_street','') or f'{google_place_dict.get("number", "")} {google_place_dict.get("street", "")}'
                self.city = google_place_dict.get('city', '')
                self.country_id = google_place_dict.get('country', False)
                self.state_id = google_place_dict.get('state', False)
