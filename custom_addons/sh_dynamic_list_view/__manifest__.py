# -*- coding: utf-8 -*-

{
    'name': 'List View Manager',
    'summary': """
        List View Manager
""",
    'description': """
        List View ,
        Advance Search ,    
        Dynamic List ,
        Hide/Show list view columns ,
        List View Manager , 
""",

    'sequence': 1,
    'category': 'Tools',
    'version': '0.0.2',
    'depends': ['base', 'base_setup','web'],
    'license': 'OPL-1',

    'data': [
        # 'views/sh_res_config_settings.xml',
        'views/res_users_view.xml',
        'security/ir.model.access.csv',
        'security/sh_security_groups.xml',
    ],

    'assets': {
        'web.assets_backend': [
            # datepicker lib
            # 'sh_dynamic_list_view/static/src/js/daterangepicker/moment.min.js',
            # 'sh_dynamic_list_view/static/src/js/daterangepicker/daterangepicker.js',
            # 'sh_dynamic_list_view/static/src/js/daterangepicker/daterangepicker.css',

            # Dynamic List View
            'sh_dynamic_list_view/static/src/css/sh_dynamic_list_view.scss',
            'sh_dynamic_list_view/static/src/css/sticky.scss',
            'sh_dynamic_list_view/static/lib/jquery.ui/jquery-ui.js',
            'sh_dynamic_list_view/static/lib/jquery.ui/jquery-ui.css',
            'sh_dynamic_list_view/static/src/js/lvm_render.js',
            # 'sh_dynamic_list_view/static/src/component/search_view.js',
            'sh_dynamic_list_view/static/src/js/sh_lvm_controller.js',
            # 'sh_dynamic_list_view/static/src/xml/rownumber.xml',
            # 'sh_dynamic_list_view/static/src/component/sh_advance_search.xml',
            'sh_dynamic_list_view/static/src/xml/lvm_button.xml',
            'sh_dynamic_list_view/static/src/xml/sh_lvm_button.xml',
            # 'sh_dynamic_list_view/static/src/xml/search_view.xml',
            'sh_dynamic_list_view/static/src/xml/sh_list_templates.xml',
            'sh_dynamic_list_view/static/src/xml/sh_cancel_edit_template.xml',
            'sh_dynamic_list_view/static/src/xml/props.xml',
        ],
    },

    'post_init_hook': 'post_install_hook',
    'uninstall_hook': 'uninstall_hook',
}
