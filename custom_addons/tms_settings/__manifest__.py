# -*- coding: utf-8 -*
# Part of octagotech. See LICENSE file for full copyright and licensing details.
{
    "name": "TMS Settings Dashboard",
    "version": "17.0",
    "summary": "Report Corner Dashboard",
    "description": """
       TMS Settings Dashboard
    """,
    "category": 'Dashboard',
    "license": "OEEL-1",
    # Dependency
    "depends": ['base','account', 'contacts'],

    "data": [
        "security/ir.model.access.csv",
        'views/report_corner_views.xml',
        'views/tms_settings_action_menu.xml',
        'demo/accounting_configuration_menu.xml',
    ],

    "installable": True,
    "application": True,
    "auto_install": False,
        
    'assets': {
        'web.assets_backend': [
            'tms_settings/static/src/js/tms_settings/tms_settings.xml',
            'tms_settings/static/src/js/tms_settings/tms_settings.js',
            'tms_settings/static/src/js/tms_settings/remove_specific_menu.js',
             'tms_settings/static/src/css/hide_documentation.css',
        ],
    },

}
