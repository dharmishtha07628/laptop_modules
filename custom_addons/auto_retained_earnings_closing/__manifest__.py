{
    'name': 'Auto Retained Earnings Closing',
    'version': '1.0',
    'summary': 'Automatically close P&L and move to retained earnings on fiscal year change',
    'author': 'You',
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/retained_earnings_data.xml',
        'views/res_company_views.xml',
        'views/closing_entry_menu.xml',
        'views/acccount_move.xml',
        "wizard/retained_earnings_data.xml",
    ],
    'assets': {
       'web.assets_backend': [
           'auto_retained_earnings_closing/static/src/js/closing_entry_list.js',
           'auto_retained_earnings_closing/static/src/xml/closing_entry_list_button.xml',
       ]
    },
    'installable': True,
    'application': False,
}
