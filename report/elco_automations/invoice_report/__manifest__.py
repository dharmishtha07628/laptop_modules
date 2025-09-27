{
    'name': 'Custom Invoice Report',
    'version': '1.0',
    'summary': 'Custom invoice report for enhanced printing',
    'description': """
        This module provides a custom invoice report for accounting purposes.
    """,
    'category': 'Accounting',
    'author': '',
    'website': 'https://www.example.com',
    'depends': ['account'],
    'data': [
        'report/report_invoice_action.xml',
        'report/invoice_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
