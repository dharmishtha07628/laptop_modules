from odoo import api, SUPERUSER_ID
from odoo.exceptions import UserError



def delete_default_chart_of_account(env):
    # Fetch all accounts created by the specific module using the external ID pattern
    account_model = env['account.account']

    # Search for all accounts that have an external ID associated with the provided module name
    accounts = account_model.search([
        ('id', 'in', env['ir.model.data'].search([
            ('module', '=', 'account'),
            ('model', '=', 'account.account')
        ]).mapped('res_id'))
    ])

    # Check if any accounts are found for deletion
    if not accounts:
        return "No accounts found associated with the 'account' module."
    else:
        env.cr.execute(' DELETE FROM account_journal')
        env.cr.execute(' DELETE FROM account_account ')
    return f"Deleted {len(accounts)} accounts associated with module '{account_model}'."

from . import models