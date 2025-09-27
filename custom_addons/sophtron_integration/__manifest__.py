{
    'name': 'Sophtron API Integration',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Integration with Sophtron API',
    'description': 'Custom module to integrate Sophtron API with Odoo.',
    'author': 'Jigna Savaniya',
    'depends': ['base', 'accounting_extend'],
    'data': [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/config_parameter.xml",
        "views/account_journal.xml",
        # "views/res_company.xml",
        "views/sophtron_api.xml",
        "wizard/fetch_transactions.xml"
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'sophtron_integration/static/src/**/*',
        ],
    },
}
