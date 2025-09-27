# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models, api


class Company(models.Model):
    _inherit = "res.company"

    # sophtron_env = fields.Selection([('prod', 'Production'), ('staging', 'Staging')], default='prod',
    #                                 string="Environment")

    def get_sophtron_url(self):
        if self.env['ir.config_parameter'].sudo().get_param('sophtron_integration.sophtron_sophtron_env') == 'staging':
            return 'https://api.sophtron-prod.com/api/'
        else:
            return 'https://api.sophtron.com/api/'

    def get_sophtron_vc_url(self):
        if self.env['ir.config_parameter'].sudo().get_param('sophtron_integration.sophtron_sophtron_env') == 'staging':
            return 'https://vc.sophtron-prod.com/api/'
        else:
            return 'https://vc.sophtron.com/api/'
