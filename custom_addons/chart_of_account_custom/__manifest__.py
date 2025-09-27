{
    'name': 'Accounting Custom Bundle',
    'version': '1.0.0',
    'summary': 'A meta-module to install all custom accounting modules.',
    'description': """
        This module is designed to automatically install all custom accounting modules.
    """,
    'author': 'dharmishthagojiya',
    'website': '',
    'category': 'Accounting',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'data/tax_data.xml',
        'data/template/account.account-generic_coa.csv',
        # 'data/template/account.tax.group-generic_coa.csv',
        # 'data/template/account.tax-generic_coa.csv',
        'data/template/account.journal-generic_coa.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'pre_init_hook': 'delete_default_chart_of_account',

}
