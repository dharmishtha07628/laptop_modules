from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    allowed_state_ids = fields.Many2many(
        'res.country.state',
        string='Allowed States',
        help="States this salesperson is allowed to access"
    )
