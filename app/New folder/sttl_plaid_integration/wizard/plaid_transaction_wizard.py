# It fetches transactions from plaid using API call and stores it in acocunting bank statements.

import logging
from odoo import models, fields, api,_
import requests
import datetime
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)

class PlaidTransaction(models.TransientModel):
    _name = "plaid.transaction.wizard"

    bank_id = fields.Many2one("plaid.bank")
    account_ids = fields.Many2many("account.journal",  default=lambda self: self._default_bank_accounts() , required=True)


    def auto_fetch_transaction(self):
        plaid_auto_connect = self.env['ir.config_parameter'].get_param(
            'sttl_plaid_integration.plaid_auto_connect')
        if plaid_auto_connect:
            self.with_context(from_cron=True).fetch_transactions()

    @api.model
    def _default_bank_accounts(self):
        if self.env.context.get('current_journal'):
            return self.env['account.journal'].browse(self.env.context.get('current_journal'))
        return self.env['account.journal'].search([('type', '=', 'bank')]).ids

    def fetch_transactions(self):
        client_id = self.env['ir.config_parameter'].get_param(
            'sttl_plaid_integration.plaid_client_id')
        secret = self.env['ir.config_parameter'].get_param(
            'sttl_plaid_integration.plaid_api_secret')
        environment = self.env['ir.config_parameter'].get_param(
            'sttl_plaid_integration.plaid_environment')
        email = self.env['ir.config_parameter'].get_param(
            'sttl_plaid_integration.plaid_email')
        accounts = []
        if client_id and secret and environment:
            # for account in self.account_ids:
            #     accounts.append(account["account_id"])
            # data = {
            #     "client_id": client_id,
            #     "secret": secret,
            #     "access_token": self.bank_id.access_token,
            #     "options":{
            #         "account_ids": accounts
            #     },
            #     "start_date": str(self.from_date),
            #     "end_date": str(self.to_date),
            # }
            journals = []
            if self.env.context.get('from_cron'):
                if not auto_connect:
                    _logger.info("Plaid auto connect disabled in settings.")
                    return
                journals = self.env['account.journal'].search(
                    [('type', '=', 'bank'), ('plaid_status', '=', 'connected')])
            journal_accounts_map = {}

            # Step 1: Group account_ids by journal
            account_list = self.account_ids or journals
            for account in account_list:

                if account not in journal_accounts_map:
                    journal_accounts_map[account] = {
                        'access_token': account.access_token,
                        'account_ids': []
                    }
                journal_accounts_map[account]['account_ids'].append(account.account_id)

            # Step 2: Build data payload per journal
            for journal, info in journal_accounts_map.items():
                try:
                    data = {
                        "client_id": client_id,
                        "secret": secret,
                        "access_token": info['access_token'],
                        "options": {
                            "account_ids": info['account_ids']
                        },
                        "start_date": journal.start_date.isoformat() if journal.start_date else None,
                        "end_date": journal.end_date.isoformat() if journal.end_date else None,
                    }
                    headers = {"Content-type": "application/json"}
                    response = requests.post(f"https://{environment}.plaid.com/transactions/get", json=data,
                                             headers=headers, verify=False)
                    if response.status_code == 200:
                        transactions = response.json()["transactions"]
                        accounts = response.json().get('accounts', [])
                    else:
                        # raise AccessError(f"Error in fetching transactions {response.json()}")
                        error_data = response.json() if response.text else {}
                        error_message = error_data.get("error_message") or _("Error in fetching transactions")
                        template = self.env.ref('sttl_plaid_integration.mail_template_plaid_reconnect',
                                                raise_if_not_found=False)
                        if template and email:
                            template.sudo().with_context(
                                email_to=email,
                                error_message=str(error_message),
                                journal_name=journal.name,
                            ).send_mail(journal.id, force_send=True)
                        return {
                            "type": "ir.actions.client",
                            "tag": "display_notification",
                            "params": {
                                "type": "warning",
                                "message": error_message,
                                "next": {"type": "ir.actions.act_window_close"},
                            },
                        }

                    statement_data = {
                        "name": "Plaid/" + str(datetime.date.today()),
                        "date": datetime.date.today(),
                        "journal_id": self.env["account.journal"].search([('type', '=', 'bank')], limit=1).id,

                    }

                    for account in accounts:
                        external_account_id = account.get("account_id")
                        balance = account.get("balances", {}).get("current", 0.0)

                        # Search for a matching journal using the external Plaid account_id
                        journal = self.env["account.journal"].search([
                            ('type', '=', 'bank'),
                            ('account_id', '=', external_account_id)
                        ], limit=1)

                        if journal:
                            journal.plaid_balance = balance
                            _logger.info(f"✅ Updated journal '{journal.name}' (ID {journal.id}) balance to {balance}")
                        else:
                            _logger.warning(f"⚠️ No journal found for account_id: {external_account_id}")


                    statement_id = self.env["account.bank.statement"].create(statement_data)
                    transactions_data_list = []
                    for transaction in transactions:
                        partner_id = self.env["res.partner"].search([("name", "=", transaction["name"])]).id
                        if partner_id:
                            partner = partner_id
                        else:
                            partner = False
                        # Extract balance if account is found
                        journal = self.env["account.journal"].search(
                            [('type', '=', 'bank'), ('account_id', '=', transaction.get('account_id'))], limit=1)
                        existing_transaction = self.env['account.bank.transaction.line'].search([
                            ('transaction_external_id', '=', transaction.get('transaction_id'))
                        ], limit=1)

                        if not existing_transaction:
                            transaction_data = {
                                    # "statement_id": statement_id.id,
                                    "currency_id": self.env["res.currency"].search(
                                        [('name', '=', transaction["iso_currency_code"])]).id,
                                    # "move_id": journal_id.id,
                                    "partner_id": partner,
                                    "memo": transaction.get("name") or '',
                                    "ref": transaction.get("name") or '',
                                    "amount": -transaction.get("amount") or '',
                                    "date": transaction.get("date") or '',
                                    "journal_id": journal.id,
                                    "account_id": journal.default_account_id.id,
                                    "transaction_external_id": transaction.get('transaction_id'),
                                    "transaction_external_meta_data":transaction.get('payment_meta'),
                                    "merchant_name": transaction.get('merchant_name')
                                }
                            transactions_data_list.append(transaction_data)
                except Exception as e:
                    template = self.env.ref('sttl_plaid_integration.mail_template_plaid_reconnect',
                                            raise_if_not_found=False)
                    if template and email:
                        template.sudo().with_context(
                            email_to=email,
                            error_message=str(e),
                            journal_name=journal.name,
                        ).send_mail(journal.id, force_send=True)
                    _logger.error("Error in fetching transactions for %s: %s", journal.name, str(e))
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'type': 'warning',
                            'message': _("Error in fetching transactions : %s",
                                         e),
                            'next': {'type': 'ir.actions.act_window_close'},
                        }
                    }
                transaction_id = self.env["account.bank.transaction.line"].create(transactions_data_list)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'success',
                        'message': _("Transactions fetch successfully"),
                        'next': {'type': 'ir.actions.act_window_close'},
                    }
                }

        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': ("Please enter plaid client id, secret and environment"),
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
