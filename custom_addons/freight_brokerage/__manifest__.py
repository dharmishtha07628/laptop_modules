# -*- coding: utf-8 -*
# Part of Octagotech. See LICENSE file for full copyright and licensing details.
{
    "name": "Freight Brokerage",
    "version": "17.0",
    "summary": "Freight Brokerage",
    "description": """
       - Freight Brokerage
    """,
    "category": 'Customization',

    # Author
    "author": "Octagotech",
    "website": "https://www.octagotech.com",
    "license": "LGPL-3",

    # Dependency
    "depends": ['sale_management'],

    "data": [
        "data/ir_sequence.xml",
        "data/edi_segment_data.xml",
        "security/ir.model.access.csv",
        "views/brokerage_order_views.xml",
        "views/brokerage_order_stop_views.xml",
        "views/res_partner_views.xml",
        "views/brokerage_location_views.xml",
        "views/brokerage_stop_details_views.xml",
    ],

    'assets': {
        'web.assets_backend': [
            '/freight_brokerage/static/src/scss/brokerage_kanban.scss',
        ],
    },

    "installable": True,
    "application": False,
    "auto_install": False
}
