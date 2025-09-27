# -*- coding: utf-8 -*-

from . import model
from . import controllers
from odoo.api import Environment, SUPERUSER_ID


def post_install_hook(env):
    # env = Environment(cr, SUPERUSER_ID, {})
    sh_user_data = {"users": [(4, user_id.id) for user_id in (env['res.users'].search([]))]}
    sh_dynamic_list_view_edit_and_read = env.ref('sh_dynamic_list_view.sh_dynamic_list_view_edit_and_read')
    sh_dynamic_list_view_edit_and_read.write(sh_user_data)

    sh_dynamic_list_view_dynamic_list = env.ref('sh_dynamic_list_view.sh_dynamic_list_view_dynamic_list')
    sh_dynamic_list_view_dynamic_list.write(sh_user_data)

    sh_dynamic_list_view_advance_search = env.ref('sh_dynamic_list_view.sh_dynamic_list_view_advance_Search')
    sh_dynamic_list_view_advance_search.write(sh_user_data)


def uninstall_hook(env):
    env.cr.execute(
        '''DELETE FROM ir_config_parameter WHERE (key LIKE '%sh_serial_number%') OR (key LIKE '%sh_list_view_field_mode%') 
            OR (key LIKE '%sh_header_color_field_change%') OR (key LIKE '%sh_header_text_color_field_change%') OR (key LIKE '%sh_toggle_color_field_change%') '''
    )
