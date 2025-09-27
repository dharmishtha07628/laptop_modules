# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.addons.web.controllers.action import Action


class CustomAction(Action):
    @http.route()
    def load(self, action_id, additional_context=None):
        value = super().load(action_id=action_id, additional_context=additional_context)
        if value['type'] == 'ir.actions.act_window' and value['res_model'] not in ['ir.module.module']:
            view_types = [view[1] for view in value['views']]
            # Check if both 'kanban' and 'list' are available
            if 'kanban' in view_types and 'list' in view_types:
                # Remove the 'kanban' view
                value['views'] = [view for view in value['views'] if view[1] not in ('kanban', 'activity')]
        return value
