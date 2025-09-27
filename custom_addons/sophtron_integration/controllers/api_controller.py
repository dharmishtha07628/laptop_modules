from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class SophtronAPIController(http.Controller):
    
    
    @http.route('/api/sophtron/data',type='json', auth='public')
    def sophtron_widget_connection(self,**kwargs):
        _logger.info("=-=sophtron-=%s"%kwargs)
        
    
    @http.route('/api/sophtron/run', type='http', auth='user')
    def run_api(self):
        client = request.env['sophtron.api.client'].create({})
        result = client.run_api_calls()
        return request.make_response(result, headers={'Content-Type': 'text/yaml'})
