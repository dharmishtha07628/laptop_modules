# -*- coding: utf-8 -*
# Part of Octagotech. See LICENSE file for full copyright and licensing details.
{
    "name": "TMS Journal Checkbook",
    "version": "17.0",
    "summary": "TMS Journal Checkbook",
    "description": """
       TMS Journal Checkbook
    """,
    "category": 'Customization',

    # Author
    "author": "Octagotech",
    "website": "https://www.Octagotech.com",
    "license": "LGPL-3",

    # Dependency
    "depends": ['odoo_check_management', 'account_batch_payment'],

    "data": [
        "data/check_attribute_data.xml",
        "views/account_journal_views.xml",
        "views/account_batch_payment_views.xml",
        "views/account_payment_views.xml",
        "views/invoice_print_bank_check_wizard_views.xml",
        "views/bank_check_views.xml",
        "views/account_batch_payment_views.xml",
        "views/check_history_views.xml",
        "views/res_company_views.xml",
        "reports/report_action.xml",
        "reports/remittance_table_report.xml",
        "reports/check_remittance_table.xml",
    ],

    "installable": True,
    "application": False,
    "auto_install": False
}
