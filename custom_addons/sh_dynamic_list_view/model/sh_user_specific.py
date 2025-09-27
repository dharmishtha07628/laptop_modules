from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class UserSpecific(models.Model):
    _name = "user.specific"
    _description = 'User Specfic Information'

    model_name = fields.Char(string="Name")
    user_id = fields.Many2one('res.users', string='User')
    sh_action_id = fields.Char(string="Action Id")
    sh_table_width = fields.Float(string="table Width")
    sh_editable = fields.Boolean(string="Editable List Mode")
    fields = fields.One2many("user.fields", "fields_list", "Fields Information")

    @api.model
    def check_user_exists(self, model_name, uid, sh_action_id):
        sh_user_table_result = {'sh_fields_data': False, 'sh_table_data': False}

        user_exists = self.env['user.specific'].search([
            ('model_name', '=', model_name),
            ('sh_action_id', '=', sh_action_id),
            ('user_id', '=', uid),
        ],limit=1)

        if user_exists:
            sh_user_table_result['sh_fields_data'] = dict([(x['field_name'], x) for x in user_exists.fields.read(
                ['ShShowField', 'field_name', 'sh_invisible', 'sh_field_order', 'sh_columns_name', 'sh_width',
                 'sh_tag'])])
            sh_user_table_result['sh_table_data'] = user_exists.read(['sh_table_width', 'sh_editable'])[0]

        return sh_user_table_result

    @api.model
    def updating_data(self, model_name, fields_name, uid, sh_action_id, sh_table_width):
        view = self.env['user.specific'].search([
            ('model_name', '=', model_name),
            ('sh_action_id', '=', sh_action_id),
            ('user_id', '=', uid)
        ], limit=1)
        vals = {
            'model_name': model_name,
            'user_id': uid,
            'sh_action_id': sh_action_id,
            'sh_table_width': sh_table_width,
        }
        if not view:
            view = self.create(vals)
        else:
            view.write(vals)
            view.fields.unlink()
        for rec in fields_name:
            vals_2 = {
                'field_name': rec['fieldName'],
                'ShShowField': rec['ShShowField'],
                'sh_field_order': rec['sh_field_order'],
                'sh_invisible': rec['sh_invisible'],
                'sh_columns_name': rec['sh_Columns_name'],
                'fields_list': view.id,
                'sh_width': rec['sh_col_width']
            }
            self.env['user.fields'].create(vals_2)

    @api.model
    def restoring_to_default(self, model_name, uid, sh_action_id):
        user_exists = self.env['user.specific'].search([
            ('model_name', '=', model_name),
            ('sh_action_id', '=', sh_action_id),
            ('user_id', '=', uid)
        ], limit=1)
        if user_exists:
            user_exists.fields.unlink()
            user_exists.unlink()

    @classmethod
    def clear_caches(self):
        """ Clear the caches

        This clears the caches associated to methods decorated with
        ``tools.ormcache`` or ``tools.ormcache_multi``.
        """
        self.pool._clear_cache()


class Userfields(models.Model):
    _name = "user.fields"
    _description = 'User Specfic Fields'
    field_name = fields.Char(string="Field Name", required=True)
    ShShowField = fields.Boolean(default=True, string="Show Field in list")
    sh_field_order = fields.Integer(string="Name")
    sh_invisible = fields.Boolean(default=False, string="Show invisible columns")
    sh_tag = fields.Char(default=False, string="Tag")
    fields_list = fields.Many2one(
        'user.specific', "User Specific Fields"
    )
    sh_columns_name = fields.Char(string="Columns Name")
    sh_width = fields.Char(string="Field Width")


class ShUserStandardSpecific(models.Model):
    _name = "sh.user.standard.specific"

    _description = 'User Standards Specfic Information'

    model_name = fields.Char(string="Name")

    user_id = fields.Many2one('res.users', string='User')

    sh_table_width = fields.Integer(string="table Width")

    sh_action_id = fields.Char(string="Action Id")

    fields = fields.One2many(
        "sh.user.standard.fields", "fields_list", "Fields Information"
    )

    # Function revoked at each time list view is loaded
    @api.model
    def check_user_exists(self, model_name, uid, sh_action_id):
        user_exists = self.env['sh.user.standard.specific'].search([
            ('model_name', '=', model_name),
            ('sh_action_id', '=', sh_action_id),
            ('user_id', '=', uid)
        ], limit=1)
        if user_exists:
            self.clear_caches()
            return user_exists.fields.read(
                ['ShShowField', 'field_name', 'sh_invisible', 'sh_columns_name', 'sh_width', ]) + user_exists.read(
                ['sh_table_width'])
        else:
            return False

    @api.model
    def updating_data(self, model_name, fields_name, uid, sh_action_id, sh_table_width):
        view = self.env['sh.user.standard.specific'].search([
            ('model_name', '=', model_name),
            ('sh_action_id', '=', sh_action_id),
            ('user_id', '=', uid)
        ], limit=1)
        vals = {
            'model_name': model_name,
            'user_id': uid,
            'sh_action_id': sh_action_id,
            'sh_table_width': sh_table_width,
        }
        if not view:
            view = self.create(vals)

        else:
            view.write(vals)
            view.fields.unlink()
        for rec in fields_name:
            vals_2 = {
                'field_name': rec['fieldName'],
                'ShShowField': rec['ShShowField'],
                'sh_field_order': rec['sh_field_order'],
                'sh_invisible': rec['sh_invisible'],
                'sh_columns_name': rec['sh_Columns_name'],
                'fields_list': view.id,
                'sh_width': rec['sh_col_width']
            }
            self.env['sh.user.standard.fields'].create(vals_2)

    @api.model
    def restoring_to_default(self, model_name, uid, sh_action_id):
        user_exists = self.env['sh.user.standard.specific'].search([
            ('model_name', '=', model_name),
            ('sh_action_id', '=', sh_action_id),
            ('user_id', '=', uid)
        ], limit=1)
        if user_exists:
            user_exists.fields.unlink()
            user_exists.unlink()


class ShUserStandardFields(models.Model):
    _name = "sh.user.standard.fields"
    _description = 'User Specific Standard fields'
    field_name = fields.Char(string="Field Name", required=True)
    ShShowField = fields.Boolean(default=True, string="Show Field in list")
    sh_field_order = fields.Integer(string="Name")
    sh_invisible = fields.Boolean(default=False, string="Show invisible columns")
    fields_list = fields.Many2one(
        'sh.user.standard.specific', "User Specific Fields"
    )
    sh_columns_name = fields.Char(string="Columns Name")
    sh_width = fields.Char(string="Field Width")


class UserMode(models.Model):
    _name = "user.mode"
    model_name = fields.Char(string="Name")
    _description = 'User Mode'
    user_id = fields.Many2one('res.users', string='User')

    sh_action_id = fields.Char(string="Action Id")

    editable = fields.Char(string="Define user editable mode")

    @api.model
    def check_user_mode(self, sh_model_name, uid, sh_action_id):
        sh_list_view_data = {
            'sh_can_edit': self.env.user.has_group('sh_dynamic_list_view.sh_dynamic_list_view_edit_and_read'),
            'sh_dynamic_list_show': self.env.user.has_group('sh_dynamic_list_view.sh_dynamic_list_view_dynamic_list'),
            'sh_can_advanced_search': self.env.user.has_group(
                'sh_dynamic_list_view.sh_dynamic_list_view_advance_Search'),
            'sh_can_duplicate': self.env.user.has_group('sh_dynamic_list_view.sh_dynamic_list_view_duplicate'),
            'currency_id': self.env.user.company_id.currency_id.id,
        }
        user_exists = self.env['user.mode'].search([
            ('model_name', '=', sh_model_name),
            ('sh_action_id', '=', sh_action_id),
            ('user_id', '=', uid)
        ], limit=1)
        if user_exists:
            sh_list_view_data['list_view_data'] = user_exists.read(['editable'])
        else:
            sh_list_view_data['list_view_data'] = False
        return sh_list_view_data

    @api.model
    def updating_mode(self, sh_model_name, uid, mode, sh_action_id):
        view = self.env['user.mode'].search([
            ('model_name', '=', sh_model_name),
            ('sh_action_id', '=', sh_action_id),
            ('user_id', '=', uid)
        ], limit=1)
        vals = {
            'model_name': sh_model_name,
            'user_id': uid,
            'editable': mode,
            'sh_action_id': sh_action_id,
        }
        if not view:
            self.clear_caches()
            self.create(vals)

        else:
            self.clear_caches()
            view.write(vals)

    @api.model
    def sh_get_autocomplete_values(self, model, field, type, value, sh_one2many_relation):
        if sh_one2many_relation:
            relation_name = self.env[sh_one2many_relation]._rec_name
            ids = self.env[model].search([(relation_name, 'ilike', value)], limit=10).ids
            return self.env[model].search([(field, 'in', ids)]).mapped(field + ".name")
        else:
            if type == "json":
                return value
            return self.env[model].search_read([(field, 'ilike', value)], [field])


class ShHttp(models.AbstractModel):
    _inherit = 'ir.http'

    # Set Config parameter value to the session.
    def session_info(self):
        rec = super(ShHttp, self).session_info()
        rec['sh_toggle_color'] = self.env['ir.config_parameter'].sudo().get_param('sh_toggle_color_field_change')
        rec['sh_header_color'] = self.env['ir.config_parameter'].sudo().get_param('sh_header_color_field_change')
        rec['sh_header_text_color'] = \
            self.env['ir.config_parameter'].sudo().get_param('sh_header_text_color_field_change')
        rec['sh_serial_number'] = self.env['ir.config_parameter'].sudo().get_param('sh_serial_number')
        rec['sh_can_advanced_search'] = \
            self.env.user.has_group('sh_dynamic_list_view.sh_dynamic_list_view_advance_Search')
        rec['sh_dynamic_list_show'] = \
            self.env.user.has_group('sh_dynamic_list_view.sh_dynamic_list_view_dynamic_list')
        return rec


class ShResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_toggle_color_field_change = fields.Char(string='Toggle Color',
                                               config_parameter='sh_toggle_color_field_change')

    sh_header_color_field_change = fields.Char(string='LVM Header Color',
                                               config_parameter='sh_header_color_field_change', default="#85639E")
    sh_header_text_color_field_change = fields.Char(string='Header Text Color', default="#ffffff",
                                                    config_parameter='sh_header_text_color_field_change')

    sh_serial_number = fields.Boolean(string="Serial Number", config_parameter='sh_serial_number')


class ShPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    @api.model
    def name_get(self):

        """ Return the categories' display name, including their direct
            parent by default.

            If ``context['partner_category_display']`` is ``'short'``, the short
            version of the category name (without the direct parent) is used.
            The default is the long version.
        """
        if self._context.get('partner_category_display') == 'short':
            return super(ShPartnerCategory, self).name_get()

        res = []
        for category in self:
            names = []
            current = category
            if current.name:
                while current:
                    names.append(current.name)
                    current = current.parent_id
                res.append((category.id, ' / '.join(reversed(names))))
        return res
