# -*- coding: utf-8 -*-


{
    'name': 'Web Google',
    'author': '',
    'website': '',
    'support': '',
    'category': '',
    'license': 'OPL-1',
    'summary': "",
    'description': "",
    'version': '0.0.1',
    'depends': ['base',"web"],
    'application': True,
    'data': [
        "views/partner_views.xml",
        "views/res_config_settings_views.xml",
        # "views/res_company_views.xml",
    ],
    'assets': {
        'web.assets_backend': {
            'web_google/static/src/xml/google_place_widget.xml',
            'web_google/static/src/js/at_address_auto_complete.js',
        }
    },
    'auto_install': False,
    'installable': True,
}
