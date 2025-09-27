# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo 17 Budget Management',
    'author': 'Odoo Mates, Odoo SA',
    'category': 'Accounting',
    'version': '17.0.1.0',
    'description': """Use budgets to compare actual with expected revenues and costs""",
    'summary': 'Odoo 17 Budget Management',
    'sequence': 10,
    'website': 'https://www.odoomates.tech',
    'depends': ['account', 'web',
                'base_setup'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'security/account_budget_security.xml',
        'wizard/import_budget_lines_view.xml',
        'views/account_analytic_account_views.xml',
        'views/account_budget_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'om_account_budget/static/src/**/*',
        ]
    },
    "images": ['static/description/banner.gif'],
    'demo': ['data/account_budget_demo.xml'],
}
