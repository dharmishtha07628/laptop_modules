# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.
{
    "name": "Territory Access for Salespersons",
    "version": "18.0",
    "summary": "Territory Access for Salespersons",
    "description": """
       Territory Access for Salespersons
    """,
    "category": 'Customization',

    # Author
    "author": "Bahelim Munafkhan",
    "website": "https://www.4minds.com",
    "license": "LGPL-3",

    # Dependency
    "depends": ['sale_management'],

    "data": [
        "views/res_users_fields.xml",
        "views/res_users_views.xml",
        "security/ir_rule.xml",
    ],

    "installable": True,
    "application": False,
    "auto_install": False
}
