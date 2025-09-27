# -*- coding: utf-8 -*-

{
    'name': 'Accoutning Extend',
    'version': '17.0',
    'summary': 'Accounting Extend',
    'description': """ Accoutning Extend""",
    'depends': ["om_account_accountant", "mail","base", "om_account_asset", "account",'auth_totp','base_setup',
                "snailmail_account",
                "om_recurring_payments", "om_account_asset", "product", "portal", "tms_settings", "contacts",
                "sms","web","privacy_lookup"],
    'data': [
        'security/security.xml',
        'data/rename_odoobot_data.xml',
        'demo/demo.xml',
        'security/ir.model.access.csv',
        # 'wizard/import_invoice_lines_view.xml',
        'wizard/account_move_send_views.xml',

        # 'wizard/import_setup_wizard_views.xml',
        'wizard/send_email_wizard_views.xml',
        
        "views/res_config_settings_views.xml",
        "views/account_move.xml",
        "views/account_payment.xml",
        "views/res_partner_bank.xml",
        "views/inherited_account_payment_view.xml",
        "views/menu.xml",
        "views/remove_menu.xml",
        "views/account_journal_views.xml",
        "views/assets.xml",
        "views/product_views.xml",
        "views/partner_view.xml",
        # "views/accounting_config_menu.xml"
        'demo/menu_accounting_configuration.xml',
        'views/res_users_view.xml',
        'views/report_invoice_template.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'accounting_extend/static/src/components/**/*',
            # 'accounting_extend/static/src/js/account_payment.js',
            'accounting_extend/static/src/xml/account_payment.xml',
            # 'accounting_extend/static/src/xml/list_render.xml',
            # 'accounting_extend/static/src/xml/tax_totals.xml',
            # 'accounting_extend/static/src/xml/tax_totals.css',
            "accounting_extend/static/src/css/hide_company_icon.css",

            # Change error screen
            "accounting_extend/static/src/js/record.js",
            # "accounting_extend/static/src/js/import_action.js",
        ]
    },
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "OPL-1",
}
