{
    'name': 'Custom Tab Title',
    'version': '1.0',
    'summary': 'Change the browser tab title dynamically to show company name.',
    'category': 'Tools',
    'author': 'Your Name',
    'depends': ['web'],  # Depends on the web module
    'assets': {
        'web.assets_backend': [
            'custom_tab_title/static/src/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
