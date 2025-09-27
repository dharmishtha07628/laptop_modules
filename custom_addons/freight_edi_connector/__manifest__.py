# -*- coding: utf-8 -*
# Part of Octagotech. See LICENSE file for full copyright and licensing details.
{
    "name": "Freight EDI Connector",
    "version": "17.0",
    "summary": "Freight EDI Connector",
    "description": """
       Freight EDI Connector.
    """,
    "category": 'Customization',

    # Author
    "author": "Octagotech",
    "website": "https://www.Octagotech.com",
    "license": "LGPL-3",

    # Dependency
    "depends": ['freight_brokerage'],

    "data": [
        "security/ir.model.access.csv",
        "views/edi_order_views.xml",
        "views/edi_order_stops_views.xml",
        "views/edi_order_reference_views.xml",
        "views/edi_order_note_views.xml",
    ],

    "installable": True,
    "application": False,
    "auto_install": False
}
