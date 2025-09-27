from odoo.http import Response
import requests
import json
from odoo import http
from odoo.http import request

# Creating API endpoints. This endpoints will be called from js.
class PlaidController(http.Controller):
    @http.route("/create_link_token", methods=['POST'], auth="user", csrf=False) # Creating link token using API call.
    def create_link_token(self):
        client_id = request.env['ir.config_parameter'].get_param(
            'sttl_plaid_integration.plaid_client_id')
        secret = request.env['ir.config_parameter'].get_param(
            'sttl_plaid_integration.plaid_api_secret')
        environment = request.env['ir.config_parameter'].get_param(
            'sttl_plaid_integration.plaid_environment')
        if client_id and secret and environment:
            headers = {"Content-type": "application/json"}
            data = {
                "client_id": client_id,
                "secret": secret,
                "client_name": "Odoo Plaid Integration",
                "language": "en",
                "country_codes": ["US"],
                "user": {
                    "client_user_id": 'user-id'
                },
                "products": ["transactions"]
            }
            response = requests.post(f"https://{environment}.plaid.com/link/token/create",
                                        json=data, headers=headers, verify=False)

            if response.status_code == 200:
                response_data = response.json()
                response_body = json.dumps(response_data)
                return Response(response_body, status=200, content_type='application/json')
            else:
                error_message = "Failed to create link token"
                return Response(error_message, status=response.status_code, content_type='text/plain')
        else:
            error_message = "Please enter plaid client id, secret and environment"
            return Response(error_message, status=400, content_type='text/plain')
            

    @http.route("/exchange_public_token", methods=['POST'], auth="user", csrf=False)  # Exchanging public token for access token.
    def exchange_public_token(self, **params):
        client_id = request.env['ir.config_parameter'].get_param(
            'sttl_plaid_integration.plaid_client_id')
        secret = request.env['ir.config_parameter'].get_param(
            'sttl_plaid_integration.plaid_api_secret')
        environment = request.env['ir.config_parameter'].get_param(
            'sttl_plaid_integration.plaid_environment')
        data = {
            "client_id": client_id,
            "secret": secret,
            "public_token": params["public_token"]
        }
        headers = {"Content-type": "application/json"}
        response = requests.post(
            f"https://{environment}.plaid.com/item/public_token/exchange", json=data, headers=headers, verify=False)
        if response.status_code == 200:
            response_data = response.json()
            current = request.env['account.journal'].search([('id', '=', params["current"])])
            current.access_token = response_data["access_token"]
            current.status = "connected"
            response_body = json.dumps(response_data)
            self.get_accounts(current, client_id, secret, environment)
            return Response(response_body, status=200, content_type='application/json')
        else:
            error_message = "Failed to get access token. Please make sure you have configured client id, secret and environment correct."
            return Response(error_message, status=response.status_code, content_type='text/plain')

    def get_accounts(self, current, client_id, secret, environment):
        import requests
        from odoo import api, SUPERUSER_ID
        from odoo.exceptions import UserError

        data = {
            "client_id": client_id,
            "secret": secret,
            "access_token": current.access_token
        }
        headers = {"Content-type": "application/json"}

        try:
            response = requests.post(
                f"https://{environment}.plaid.com/accounts/get",
                json=data,
                headers=headers,
                verify=False
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise UserError(f"Plaid API request failed: {str(e)}")

        result = response.json()

        if "accounts" not in result:
            raise UserError(f"Plaid error: {result.get('error_message', 'Unknown error')}")

        accounts = result.get("accounts", [])
        currency_model = request.env["res.currency"]
        account_model = request.env["account.account"]
        journal_model = request.env["account.journal"]

        first = True  # Flag for the first account

        for account in accounts:
            balance = account["balances"].get("available") or account["balances"].get("current")
            currency_code = account["balances"].get("iso_currency_code")
            currency_id = currency_model.search([('name', '=', currency_code)], limit=1).id

            account_name = account["name"]
            account_code = account["account_id"][:8].upper()

            # Find or create account.account
            existing_account = account_model.search([
                ('id', '=', current.default_account_id.id),
            ], limit=1)

            if not existing_account:
                existing_account = account_model.create({
                    "name": account_name,
                    "code": account_code,
                    "account_type": "asset_cash",
                    "currency_id": currency_id or False,
                    "reconcile": True,
                    "company_id": current.company_id.id,
                })

            # First account → update current journal
            if first:
                current.write({
                    "type": "bank",
                    "currency_id": currency_id or False,
                    "bank_statements_source": 'plaid',
                    "access_token": current.access_token,
                    "account_id": account.get("account_id"),
                    "plaid_response": result,
                    "plaid_reconnect":True,
                    "plaid_status": "connected",  # ✅ journal status updated
                })
                first = False
            else:
                journal_model.create({
                    "name": account_name,
                    "type": "bank",
                    "code": account_code[:4],
                    "company_id": current.company_id.id,
                    "default_account_id": existing_account.id,
                    "currency_id": currency_id or False,
                    "bank_statements_source": 'plaid',
                    "access_token": current.access_token,
                    "account_id": account.get("account_id"),
                    "plaid_response": result,
                    "plaid_reconnect": True,
                    "plaid_status": "connected",  # ✅ new journal marked as connected
                })

        # ✅ Return a success message
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Plaid Connection Successful",
                "message": f"{len(accounts)} account(s) connected successfully.",
                "sticky": False,
                "type": "success",
                "next": {
                    "type": "ir.actions.client",
                    "tag": "reload",  # ✅ reloads the view
                },
            },
        }

    # def get_accounts(self, current, client_id, secret, environment):  # Fetching accounts using API call.
    #     data = {
    #         "client_id": client_id,
    #         "secret": secret,
    #         "access_token": current.access_token
    #     }
    #     headers = {"Content-type": "application/json"}
    #     response = requests.post(f"https://{environment}.plaid.com/accounts/get", json=data, headers=headers, verify=False)
    #     accounts = response.json()["accounts"]
    #     for account in accounts:
    #         if account["balances"]["available"]:
    #             balance = account["balances"]["available"]
    #         else:
    #             balance = account["balances"]["current"]
    #         data = {
    #             "name": account["name"],
    #             "account_type": account["subtype"],
    #             "account_subtype": account["type"],
    #             "account_id": account["account_id"],
    #             "balance": balance,
    #             "currency_id": request.env["res.currency"].search([('name', '=', account["balances"]["iso_currency_code"])]).id
    #         }
    #         plaid_account_id = request.env["plaid.account"].create(data)
    #         current.account_ids += plaid_account_id

    # def get_accounts(self, current, client_id, secret, environment):
    #     import requests
    #     from odoo import api, SUPERUSER_ID
    #
    #     data = {
    #         "client_id": client_id,
    #         "secret": secret,
    #         "access_token": current.access_token
    #     }
    #     headers = {"Content-type": "application/json"}
    #
    #     response = requests.post(
    #         f"https://{environment}.plaid.com/accounts/get",
    #         json=data,
    #         headers=headers,
    #         verify=False
    #     )
    #
    #     accounts = response.json().get("accounts", [])
    #     currency_model = request.env["res.currency"]
    #     account_model = request.env["account.account"]
    #     journal_model = request.env["account.journal"]
    #
    #     first = True  # Flag to indicate the first account
    #
    #     for account in accounts:
    #         balance = account["balances"].get("available") or account["balances"].get("current")
    #         currency_code = account["balances"].get("iso_currency_code")
    #         currency_id = currency_model.search([('name', '=', currency_code)], limit=1).id
    #
    #         account_name = account["name"]
    #         account_code = account["account_id"][:8].upper()
    #
    #         # Check if journal already exists (avoid duplicates)
    #         # existing_journal = journal_model.search([
    #         #     ('name', '=', account_name),
    #         #     ('type', '=', 'bank'),
    #         #     ('company_id', '=', current.company_id.id)
    #         # ], limit=1)
    #         existing_journal = journal_model.search([
    #             ('id', '=', current.id),
    #             ('type', '=', 'bank'),
    #             ('company_id', '=', current.company_id.id)
    #         ], limit=1)
    #
    #         # if existing_journal:
    #         #     continue  # Skip this account, already exists
    #
    #         # Check or create account.account
    #         # existing_account = account_model.search([
    #         #     ('name', '=', account_name),
    #         #     ('company_id', '=', current.company_id.id)
    #         # ], limit=1)
    #         existing_account = account_model.search([
    #             ('id', '=', current.default_account_id.id),
    #         ], limit=1)
    #
    #         if not existing_account:
    #             existing_account = account_model.create({
    #                 "name": account_name,
    #                 "code": account_code,
    #                 "account_type": "asset_cash",
    #                 "currency_id": currency_id or False,
    #                 "reconcile": True,
    #                 "company_id": current.company_id.id,
    #             })
    #
    #         # Step 3: Use current for the first, create new for the rest
    #         if first:
    #             current.write({
    #                 # "name": account_name,
    #                 "type": "bank",
    #                 # "code": account_code[:4],
    #                 # "default_account_id": existing_account.id,
    #                 "currency_id": currency_id or False,
    #                 "bank_statements_source": 'plaid',
    #                 'access_token': current.access_token,
    #                 'account_id': account.get('account_id'),
    #                 'plaid_response':account
    #             })
    #             first = False  # Mark first done
    #         else:
    #             journal_model.create({
    #                 "name": account_name,
    #                 "type": "bank",
    #                 "code": account_code[:4],
    #                 "company_id": current.company_id.id,
    #                 "default_account_id": existing_account.id,
    #                 "currency_id": currency_id or False,
    #                 "bank_statements_source": 'plaid',
    #                 'access_token': current.access_token,
    #                 'account_id': account.get('account_id'),
    #                 'plaid_response':account
    #             })
