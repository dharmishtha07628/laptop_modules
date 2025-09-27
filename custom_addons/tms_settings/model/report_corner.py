# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TmsSettingTag(models.Model):
    _name = 'tms.setting.tag'
    _description = 'Tags for selection records based on menu context'

    name = fields.Char(string='Name')
    tag_value = fields.Char(string='Tag Value')

    _sql_constraints = [
        ('tag_value_uniq', 'unique(tag_value)', "Tag value must be unique!"),
    ]

class TmsSettingMenu(models.Model):
    _name = 'tms.setting.menu'
    _description = 'Menu for selection records based on menu context'

    sequence = fields.Integer(default=10)
    action_id = fields.Many2one('ir.actions.act_window', string='Action')
    client_action_id = fields.Many2one('ir.actions.client', string='Client Action')
    description = fields.Char(string='Description')
    tms_setting_id = fields.Many2one('tms.setting', string='Tms Setting')


class TmsSetting(models.Model):
    _name = 'tms.setting'
    _inherit = ["mail.thread"]
    _description = 'All the required data for report dashboard'

    sequence = fields.Integer(default=10)
    name = fields.Char(string='Name', required=True)
    tag_id = fields.Many2one('tms.setting.tag', string='Setting Tag')
    description = fields.Char(string='Description')
    active = fields.Boolean(default=True)
    tms_menu_ids = fields.One2many('tms.setting.menu', 'tms_setting_id', string='Menu Ids')

    # def open_related_report(self):
    #     if self.action_id:
    #         action = self.env.ref(self.action_id.xml_id).read()[0]
    #     elif self.client_action_id:
    #         action = self.env.ref(self.client_action_id.xml_id).read()[0]
    #     return action

    @api.model
    def get_setting_data(self, tag):
        tag_id = self.env['tms.setting.tag'].search([('tag_value', '=', tag)], limit=1)
        tms_setting_ids = self.search([('tag_id', '=', tag_id.id)], order='sequence asc')
        values = {'display_name': tag_id.name}
        setting_main_menu = []
        for setting in tms_setting_ids:
            setting_sub_menu = []
            for sub in setting.tms_menu_ids:
                setting_sub_menu.append({
                    'id': sub.id,
                    'name': sub.action_id.name,
                    'xml_id': sub.action_id.xml_id,
                })

            setting_main_menu.append({
                'id': setting.id,
                'name': setting.name,
                'setting_sub_menu': setting_sub_menu,
            })

        values['setting_main_menu'] = setting_main_menu

        return values
