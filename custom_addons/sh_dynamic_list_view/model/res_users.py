from odoo import models, fields, api
from odoo.http import request

class res_users(models.Model):
    _inherit = "res.users"

    sh_enable_list_view_manager = fields.Boolean('List View Manager', default=False)


    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['sh_enable_list_view_manager']

    @property
    def SELF_WRITEABLE_FIELDS(self):
            return super().SELF_WRITEABLE_FIELDS + ['sh_enable_list_view_manager']


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        info = super().session_info()
        user = request.env.user
        info["sh_enable_list_view_manager"] = user.sh_enable_list_view_manager
        return info
