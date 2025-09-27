# -*- coding: utf-8 -*
# Part of octagotech. See LICENSE file for full copyright and licensing details.
{
    "name": "Advance List Filter",
    "version": "17.0",
    "summary": "Advance List Filter",
    "description": """
       Advance List Filter
    """,
    "category": 'Dashboard',
    "license": "OEEL-1",
    # Dependency
    "depends": ['web'],

    "data": [
        # "views/views.xml"
    ],

    "installable": True,
    "application": True,
    "auto_install": False,

    'assets': {
        'web.assets_backend': [
            'advance_list_filter/static/src/views/**/*',
        ],
    },

}
