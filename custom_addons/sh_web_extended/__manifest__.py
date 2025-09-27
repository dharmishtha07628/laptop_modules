# -*- coding: utf-8 -*
# Part of octagotech. See LICENSE file for full copyright and licensing details.
{
    "name": "SH Web Extended",
    "version": "17.0",
    "summary": "SH Web Extended",
    "description": """
       SH Web Extended.
       * This module add following functionality.
       - make labels red color for required fields.
       - deleting from view record will redirect to respected list or kanban view.
       - add a calculator in controlpanel.
       - add chatter position by default as bottom.
    """,
    "category": 'web',

    # Author
    "author": "Octagotech pvt ltd",
    "website": "www.octagotech.com",
    "license": "LGPL-3",

    # Dependency
    "depends": ['web'],

    "data": [
        # "views/web.xml",
        # "views/res_users.xml",
    ],

    'assets': {
        'web.assets_backend': [
            'sh_web_extended/static/src/views/**/*',
            'sh_web_extended/static/src/search/**/*',
            'sh_web_extended/static/src/js/calculator_controll_panel/**/*',
        ],
    },

    "installable": True,
    "application": False,
    "auto_install": False,
}
