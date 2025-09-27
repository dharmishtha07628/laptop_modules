import json

from odoo import http
import logging

_logger = logging.getLogger(__name__)
from odoo.http import request
from odoo.addons.web.controllers.dataset import DataSet
from lxml import etree as etree



class LvmController(DataSet, http.Controller):

    @http.route(['/web/dataset/call_kw', '/web/dataset/call_kw/<path:path>'], type='json', auth="user")
    def call_kw(self, model, method, args, kwargs, path=None):
        call_kw_result = super(LvmController, self).call_kw(model, method, args, kwargs, path)
        if method == "get_views" and call_kw_result.get('views').get('list'):
            sh_list_view_id = call_kw_result["views"]["list"].get("id")

            self.sh_prepare_lvm_list_data(call_kw_result, model, sh_list_view_id)
        return call_kw_result

    def sh_prepare_lvm_list_data(self, original_list_data, model, sh_list_view_id):
        list_view_data = original_list_data.get('views').get('list')

        if sh_list_view_id:
            list_view_data['sh_lvm_user_data'] = self.sh_fetch_lvm_data(model, sh_list_view_id)

            if list_view_data['sh_lvm_user_data']['sh_lvm_user_table_result']['sh_fields_data']:
                self.sh_process_arch(list_view_data, original_list_data.get('models')[model])
        else:
            user_mode_data = request.env['user.mode'].check_user_mode(model, request.env.user.id, False)
            user_mode_data['sh_can_advanced_search'] = False
            user_mode_data['sh_can_edit'] = False
            user_mode_data['sh_can_duplicate'] = False
            user_mode_data['sh_dynamic_list_show'] = False
            sh_lvm_user_data = {
                'sh_lvm_user_mode_data': user_mode_data
            }
            list_view_data['sh_lvm_user_data'] = sh_lvm_user_data

    def sh_fetch_lvm_data(self, model, sh_view_id=False):
        sh_lvm_user_data = {}
        user_mode_model = request.env['user.mode']
        user_specific_model = request.env['user.specific']

        user_mode_data = user_mode_model.check_user_mode(model, request.env.user.id, sh_view_id)
        sh_user_table_result = user_specific_model.check_user_exists(model, request.env.user.id, sh_view_id)

        sh_lvm_user_data['sh_lvm_user_table_result'] = sh_user_table_result
        sh_lvm_user_data['sh_lvm_user_mode_data'] = user_mode_data
        sh_lvm_user_data['ShViewID'] = sh_view_id
        return sh_lvm_user_data

    @http.route('/sh_lvm_control/user_lvm_data', type='json', auth="user")
    def sh_fetch_lvm_data_controller(self, model, sh_view_id=False):
        return self.sh_fetch_lvm_data(model, sh_view_id)

    @http.route('/sh_lvm_control/update_list_view_data', type='json', auth="user")
    def update_list_view_data(self, sh_table_data, sh_fields_data, sh_fetch_options):
        for sh_table in sh_table_data:
            request.env['user.specific'].browse(sh_table.get('id')).write(sh_table)

        for sh_field in sh_fields_data:
            request.env['user.fields'].browse(sh_field.get('id')).write(sh_field)

        if sh_fetch_options:
            return self.sh_generate_arch_view(sh_fetch_options.get('sh_context'),sh_fetch_options.get('sh_model'), sh_fetch_options.get('sh_view_id'),sh_fetch_options.get('sh_search_id'))

    @http.route('/sh_lvm_control/sh_generate_arch_view', type='json', auth="user")
    def sh_generate_arch_view(self, sh_context, sh_model, sh_view_id, sh_search_id):
        sh_view_data = request.env[sh_model].with_context(sh_context).get_views([(sh_view_id, 'list'),(sh_search_id,'search')],{})
        self.sh_prepare_lvm_list_data(sh_view_data, sh_model, sh_view_id)
        return sh_view_data

    @http.route('/sh_lvm_control/create_list_view_data', type='json', auth="user")
    def create_list_view_data(self, sh_context,sh_model, sh_editable, sh_view_id, sh_table_width_per, sh_fields_data,sh_search_id):
        list_view_record = request.env['user.specific'].create({
            'model_name': sh_model,
            'user_id': request.env.uid,
            'sh_action_id': sh_view_id,
            'sh_table_width': sh_table_width_per,
            'sh_editable': sh_editable,
        })

        for rec in sh_fields_data.values():
            rec.update({"fields_list": list_view_record.id})
            request.env['user.fields'].create(rec)

        return self.sh_generate_arch_view(sh_context,sh_model, sh_view_id,sh_search_id)
        # Removing Fields that are not in view anymore

    def check_fields(self, table_id, fields_list, sh_field_list):
        for r_field in filter(lambda x: x not in [x for x in fields_list.keys()], [x['field_name'] for x in sh_field_list.values()]):
            field_rec = sh_field_list.pop(r_field)
            request.env['user.fields'].browse(field_rec.get('id', 0)).sudo().unlink()

        for field in filter(lambda x: not sh_field_list.get(x, False), fields_list.keys()):
            sh_field_list[field] = val = {
                "sh_columns_name": fields_list[field]['string'],
                "ShShowField": False,
                "field_name": field,
                "sh_width": 0,
                "sh_field_order": len(sh_field_list)
            }
            val.update({'fields_list': table_id})
            rec_id = request.env['user.fields'].create(val)
            sh_field_list[field]['id'] = rec_id.id

    def sh_process_arch(self, list_view_data, fields_list):
        # We make default fields as readonly in List View
        sh_default_field_list = ["id", "create_uid", "create_date", "write_uid", "write_date", "__last_update"]
        fields = {};
        # Rejected Field List (This field wont be shown in dropdown menu)
        sh_reject_field_list = ["activity_exception_decoration"]

        parser = etree.XMLParser(remove_comments=True)
        node = etree.fromstring(list_view_data['arch'], parser=parser)
        sh_node_dict = {}
        for sh_node in range(len(node.getchildren())):
            if node.getchildren()[sh_node].tag == 'button':
                sh_node_dict.update({sh_node: node.getchildren()[sh_node]})

        sh_field_list = list_view_data['sh_lvm_user_data']['sh_lvm_user_table_result']['sh_fields_data']
        LvmController.check_fields(self,
                                   list_view_data['sh_lvm_user_data']['sh_lvm_user_table_result']['sh_table_data'][
                                       'id'], fields_list, sh_field_list)

        # Checking if user allowed to edit/read table
        if list_view_data['sh_lvm_user_data']['sh_lvm_user_mode_data']['sh_can_edit']:
            if list_view_data['sh_lvm_user_data']['sh_lvm_user_table_result']['sh_table_data']['sh_editable']:
                node.set('editable', 'top')
            elif node.get("editable"):
                node.attrib.pop("editable")

        if list_view_data['sh_lvm_user_data']['sh_lvm_user_mode_data']['sh_can_duplicate']:
            if list_view_data['sh_lvm_user_data']['sh_lvm_user_table_result']['sh_table_data']['sh_editable']:
                node.set('editable', 'top')
            elif node.get("editable"):
                node.attrib.pop("editable")

        sh_has_dynamic_list_access = request.env.user.has_group(
            'sh_dynamic_list_view.sh_dynamic_list_view_dynamic_list')
        if sh_has_dynamic_list_access:
        # Setting all fields to invisible
            for field_node in node.getchildren():
                field_node.set('invisible', '1')
                field_node.set("optional","hide")
                if field_node.get('modifiers') and field_node.tag == 'field':
                    modifiers = json.loads(field_node.get('modifiers'))
                    # if not modifiers.get('column_invisible'):
                    #     modifiers.update({'column_invisible': True})
                    #     field_node.set('modifiers', json.dumps(modifiers))
                if field_node.get("name") in sh_field_list and field_node.tag == 'field':
                    if field_node.get("name") and not sh_field_list[field_node.get("name")]['ShShowField'] and field_node.tag != "field":
                        node.remove(field_node)
                elif field_node.get("name") and field_node.tag == 'field':
                    sh_field_list[field_node.get("name")] = val = {
                        "sh_columns_name": field_node.attrib['name'],
                        "ShShowField": False,
                        "field_name": field_node.get("name"),
                        "sh_width": 0,
                        "sh_field_order": len(sh_field_list)
                    }
                    for i in field_node:
                        if node.getchildren[i].tag != "button":
                            rec_id = request.env['user.fields'].create(val)
                            sh_field_list[field_node.get("name")]['id'] = rec_id.id

            # Only showing selected fields to visible
            for field_name in [x['field_name'] for x in sh_field_list.values() if x['ShShowField']]:
                if list(filter(lambda x: x.get('name') == field_name, node.getchildren())):
                    for field_node in list(filter(lambda x: x.get('name') == field_name, node.getchildren())):
                        field_node.set('invisible', '0')
                        field_node.set('string', sh_field_list[field_name]['sh_columns_name'])

                        # if field_node.get('modifiers'):
                        #     modifiers = json.loads(field_node.get('modifiers'))
                        #     if modifiers.get('column_invisible'):
                        #         modifiers.update({'column_invisible': False})
                        #         field_node.set('modifiers', json.dumps(modifiers))

                        if field_node.get('optional'):
                            field_node.attrib.pop('optional')
                        if (field_node.attrib.get('widget') != 'image'):
                            field_node.attrib['width'] = sh_field_list[field_name]['sh_width']

                else:
                    field_node = etree.Element('field', attrib={'name': field_name, 'invisible': '0',
                                                                'string': sh_field_list[field_name]['sh_columns_name']})
                    if(field_node.attrib.get('widget')!='image'):
                        field_node.attrib['width'] = sh_field_list[field_name]['sh_width']
                    node.append(field_node)
                    fields[field_name]= fields_list[field_name]
                    list_view_data['fields']=fields

        sorted_node_fields = sorted([x for x in node.getchildren() if x.get('name') and x.tag == 'field'], key=lambda x:sh_field_list[x.get('name')]['sh_field_order'])

        # for field_node in node.getchildren():
        #     node.remove(field_node)
        for sh_node in node.getchildren():
            if sh_node.tag == 'button':
                node.remove(sh_node)

        for field_node in sorted_node_fields:
            # Updating Default fields to readonly.
            if field_node.get("name") in sh_default_field_list:
                if field_node.get('modifiers'):
                    modifiers = json.loads(field_node.get('modifiers'))
                    modifiers["readonly"] = True
                    field_node.set('modifiers', json.dumps(modifiers))
                else:
                    field_node.set('modifiers', json.dumps({"readonly": True}))

            if field_node.get("name") not in sh_reject_field_list:
                node.append(field_node)
        for sh_node in sh_node_dict:
            node.insert(sh_node,sh_node_dict.get(sh_node))

        list_view_data['arch'] = etree.tostring(node, pretty_print=True, encoding='unicode')

    @http.route('/sh_lvm_control/sh_reset_list_view_data', type='json', auth="user")
    def sh_reset_list_view_data(self, sh_context,sh_model, sh_view_id, sh_lvm_table_id, sh_search_view_id):
        sh_lvm_user_specific = request.env['user.specific'].browse(sh_lvm_table_id)
        sh_lvm_user_specific.fields.sudo().unlink()
        sh_lvm_user_specific.sudo().unlink()


        sh_view_data = request.env[sh_model].with_context(sh_context).get_views([(sh_view_id, 'list'),(sh_search_view_id, 'search')])
        self.sh_prepare_lvm_list_data(sh_view_data, sh_model, sh_view_id)
        return sh_view_data
