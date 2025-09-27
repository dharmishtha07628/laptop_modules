# -*- coding: utf-8 -*-
{
    "name": "Odoo Plaid Integration",
    "version": "17.0.1.0",
    "author": "",
    "category": "accounting",
    "website": "",
    "description": """
	This module provides you functionality to integrate Plaid with Odoo.
        Fetch Bank accounts, Transactions of those accounts from Plaid to Odoo.
        """,
    "summary": """
    	This module provides you functionality to integrate Plaid with Odoo.
        Fetch Bank accounts, Transactions of those accounts from Plaid to Odoo.
    """,
    "depends": ["account", "om_account_accountant", "web", "tms_account_reconcile"],
    "data": [
        "data/plaid_mail_template.xml",
        "data/configuration_parameter.xml",
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "views/res_config.xml",
        "views/invoicing_menu.xml",
        "views/plaid_account_views.xml",
        "views/plaid_bank.xml",
        'views/account_bank_statement.xml',
        "wizard/plaid_transaction_wizard.xml",
        "views/account_journal_views.xml",
        "views/account_bank_transaction_line_views.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "sttl_plaid_integration/static/src/js/plaid.js",
            "sttl_plaid_integration/static/src/js/journal_kanban_button.js",
            "https://cdn.plaid.com/link/v2/stable/link-initialize.js",
            'sttl_plaid_integration/static/src/xml/journal_list_button.xml',
        ],
    },
    "price": 0,
    "currency": "USD",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "images": ["static/description/banner.png"]
}
