# -*- coding: utf-8 -*-
{
    'name': "accountant_reconsile",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
        Install this module to use lvm functionality in the reconcile menu in enterprise accounting module.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '17.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sh_dynamic_list_view'],


    'assets': {'web.assets_backend':
		[
            'accountant_reconsile/static/src/xml/reconsile_button.xml',
	  ]
    },
}

