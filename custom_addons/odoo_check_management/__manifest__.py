# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
    "name": "Odoo Dynamic Bank Check Print",
    "summary": """This module allows you to set various attributes of bank check dynamically, so you can print bank check in a easy manner.""",
    "category": "Accounting",
    "version": "1.0.0",
    "sequence": 1,
    "author": "Webkul Software Pvt. Ltd.",
    "license": "Other proprietary",
    "website": "https://store.webkul.com/Odoo-Dynamic-Bank-Cheque-Print.html",
    "description": """Dynamic check,
Dynamic check,
Bank check print,
Check dynamic,
Bank check,
Check dynamic,
Check printing,
Bank check,
Dynamic print check,
Check payment,
Payment check,
Check print,
Check print,
Check writing,
Partner check print""",
    "live_test_url": "http://odoodemo.webkul.com/?module=odoo_check_management",
    "depends": [
        'account',
        # 'website',
        "tms_settings",

    ],
    "data": [
        'security/ir.model.access.csv',
        'data/check_attribute_data.xml',
        'wizard/invoice_print_check_transient_views.xml',
        'views/account_invoice_inherit_view.xml',
        'views/bank_check_views.xml',
        'views/website_template_view.xml',
        'views/check_report.xml',
        'demo/menu_accounting_configuration.xml',
    ],
    "assets": {
        'web.assets_frontend': [
            '/odoo_check_management/static/src/js/jquery_Jcrop.js',
            '/odoo_check_management/static/src/js/bank_check.js',
        ]
    },
    "images": ['static/description/Banner.png'],
    "application": True,
    "installable": True,
    "auto_install": False,
    "price": 99,
    "currency": "USD",
    "pre_init_hook": "pre_init_check",
}
