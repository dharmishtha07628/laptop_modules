# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.
{
    "name": "Account Filter Buttons",
    "version": "17.0",
    "summary": "Module Summary",
    "description": """
       Account Filter Buttons.
    """,
    "category": 'Customization',

    # Author
    "author": "octagotech pvt ltd",
    "website": "www.octagotech.com",
    "license": "LGPL-3",

    # Dependency
    "depends": ['account','invoice_recurring'],
    # 'advance_list_filter', 

    "data": [
        "views/account_move_views.xml",
    ],

    'assets': {
        'web.assets_backend': [
            'account_filter_buttons/static/src/**/*',
        ],
    },

    "installable": True,
    "application": False,
    "auto_install": False
}
