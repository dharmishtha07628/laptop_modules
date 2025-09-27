# -*- coding: utf-8 -*-
{
    'name': "account_lvm",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
        Install this module to use dynamic list view functionality in  account, purchase, stock and expense module.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '17.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sh_dynamic_list_view','account','purchase','hr_expense','stock'],

    'assets': {'web.assets_backend':
		[
			'account_lvm/static/src/js/account_lvm_render.js',
			'account_lvm/static/src/xml/account_lvm_button.xml',
			'account_lvm/static/src/xml/account_row.xml',
			'account_lvm/static/src/xml/account_search_view.xml',
	  ]
    },
}