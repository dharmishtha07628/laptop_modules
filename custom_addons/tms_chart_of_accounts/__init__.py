from . import models


from odoo import api, SUPERUSER_ID


def post_init_hook(env):

    result = []
    Account = env['account.account']
    CustomAccount = env['custom.account']

    accounts = Account.sudo().search([])
    result.append(len(accounts))
    account_dict = {}
    for rec in accounts:
        if rec.code not in account_dict:
            account_dict[rec.code] = []
        account_dict[rec.code].append(rec)

    result.append(account_dict)

    for code, recs in account_dict.items():
        sample = recs[0]
        company_ids = [r.company_id.id for r in recs]
        account_ids = [r.id for r in recs]

        # Check if already created to avoid duplicates
        existing = CustomAccount.search([('code', '=', code)], limit=1)
        if existing:
            continue

        custom_account = CustomAccount.create({
            'name': sample.name,
            'code': code,
            'default_account': True,
            'account_type': sample.account_type,
            'company_ids': [(6, 0, company_ids)],
            'account_ids': [(6, 0, account_ids)],
        })
        Account.browse(account_ids).sudo().write({
            'custom_account_id': custom_account.id
        })