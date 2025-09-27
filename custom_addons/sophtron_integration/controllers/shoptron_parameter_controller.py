from odoo import http
from odoo.http import request


class ConfigParameterController(http.Controller):
    @http.route('/get/system_parameter', type='json', auth='user')
    def get_system_parameter(self, param_key):
        # Fetch the system parameter value

        sophtron_url = request.env['ir.config_parameter'].sudo().get_param('sophtron_integration.sophtron_url')
        sophtron_uid = request.env['ir.config_parameter'].sudo().get_param('sophtron_integration.sophtron_uid')

        value = '{}/?job_type=aggregate&amp;user_id={}'.format(sophtron_url, sophtron_uid)
        return {'value': value}
