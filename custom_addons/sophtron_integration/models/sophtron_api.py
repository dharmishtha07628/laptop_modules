import os
import hmac
import hashlib
import base64
import requests
# import yaml
import json
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from odoo import models, api, exceptions, _, fields
import logging

_logger = logging.getLogger(__name__)


class SophtronAPIMember(models.Model):
    _name = 'sophtron.api.member'

    sophtron_id = fields.Many2one('sophtron.api.client')
    institution_id = fields.Char(string='Institution ID')
    member_id = fields.Char(string='Member ID', required=True)
    account_id = fields.Char(string='Account ID')
    account_name = fields.Char(string='Account Name')
    account_number = fields.Char(string='Account Number')
    account_type = fields.Char(string='Account Type')
    account_status = fields.Char(string='Account Status')
    account_sub_type = fields.Char(string='Account Sub Type')
    journal_ids = fields.One2many('account.journal', "sophtron_member_id", string="Journal")
    end_date = fields.Datetime(string='End Date')

    def create_journal(self):
        if not self.journal_ids:
            vals = {
                "name": "%s - %s - %s" % (self.account_name, self.account_number, self.account_type),
                "type": "bank",
                "is_credit_card": True if self.account_type == 'Credit_Card' else False,
                "sophtron_account_type": self.account_type,
                "sophtron_member_id": self.id
            }
            self.env['account.journal'].create(vals)

    def fetch_transaction_from_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sophtron.api.transactions',
            'view_mode': 'form',
            'view_id': self.env.ref('sophtron_integration.view_sophtron_api_transactions_form').id,
            'target': 'new',
            'context': {
                'default_sophtron_id': self.sophtron_id.id,
            }
        }

    def fetch_transactions(self, start_dt, end_dt):
        start_date = start_dt.strftime('%Y-%m-%d')
        end_date = end_dt.strftime('%Y-%m-%d')
        integration_key = self.sophtron_id.get_integration_key()
        transaction_url = f"v2/customers/{self.sophtron_id.customer_id}/accounts/{self.account_id}/transactions?startdate={start_date}&enddate={end_date}"
        headers = {'Authorization': self.sophtron_id.build_auth_code('get', transaction_url)}
        response = requests.get(f"{self.env.company.get_sophtron_url()}{transaction_url}", headers=headers)
        vc_data = response.json()

        for rec in vc_data:
            if rec.get('Status', False) == 'POSTED':
                _logger.info("--rec %s" % rec)

                partner = self.env['res.partner'].search([('name', '=', rec.get('merchant', False))]) if rec.get(
                    'merchant', False) else False
                vals = {
                    'ref': rec.get('Description', False),
                    'memo': rec.get('memo', False),
                    'amount': rec.get('Amount', False),
                    'journal_id': self.journal_ids[0].id,
                    'date': datetime.strptime(rec.get('PostDate', False), "%Y-%m-%dT%H:%M:%SZ") if rec.get('PostDate',
                                                                                                           False) else False,
                    'partner_id': partner.id if partner else False,
                    'transaction_external_id': rec.get('ID', False),
                    'account_id': self.journal_ids[0].default_account_id.id,
                    'transaction_external_meta_data': str(rec)
                }
                _logger.info("--vals %s" % vals)
                transaction_obj = self.env['account.bank.transaction.line'].search(
                    [('transaction_external_id', '=', rec.get('ID', False))], limit=1)
                if transaction_obj:
                    transaction_obj.write(vals)
                else:
                    transaction_obj = self.env['account.bank.transaction.line'].create(vals)

    @api.model
    def find_transactions_records(self):
        current_date = datetime.now(timezone.utc)
        records = self.search([])
        for rec in records:
            start_date = rec.end_date
            if not start_date:
                start_date = current_date - relativedelta(days=1)
            rec.fetch_transactions(start_date, current_date)
            rec.end_date = datetime.now()

    def auto_fetch_transactions(self):
        current_date = datetime.now(timezone.utc)
        yesterday_date = current_date - relativedelta(days=1)
        records = self.search([])
        for rec in records:
            rec.fetch_transactions(yesterday_date, current_date)
            rec.end_date = datetime.now()


class SophtronAPIClient(models.Model):
    _name = 'sophtron.api.client'
    _rec_name = 'customer_id'

    customer_id = fields.Char(string='User ID', required=True)
    member_id = fields.Char(string='Member ID', required=True)
    account_id = fields.Char(string='Account ID')
    sophtron_client_member_ids = fields.One2many('sophtron.api.member', 'sophtron_id')
    institution_id = fields.Char(string='Institution ID')
    journal_id = fields.Many2one('account.journal', string="Bank")
    # Class-level attribute for api_endpoints
    api_endpoints = {
        "GetInstitutionByName": 'Institution/GetInstitutionByName',
        "GetUserInstitutionsByUser": 'UserInstitution/GetUserInstitutionsByUser',
        "GetUserIntegrationKey": 'User/GetUserIntegrationKey',
        "GetJobInformationByID": 'Job/GetJobInformationByID'
    }

    @api.model
    def create_sophtron_object(self, journal_id, customer_id, member_id, sophtron_id):
        vals = {
            "customer_id": customer_id,
            "member_id": member_id,
            "journal_id": journal_id
        }
        if sophtron_id:
            sophtron = self.env['sophtron.api.client'].sudo().browse(sophtron_id)
            sophtron.write(vals)
        else:
            sophtron = self.env['sophtron.api.client'].sudo().create(vals)

        print(sophtron)
        return sophtron.fetch_accounts()

    def fetch_accounts(self):
        integration_key = self.get_integration_key()
        transaction_url = f"v2/Customers/{self.customer_id}/Members/{self.member_id}/accounts"
        headers = {'Authorization': self.build_auth_code('get', transaction_url)}
        response = requests.get(f"{self.env.company.get_sophtron_url()}{transaction_url}", json={}, headers=headers)
        vc_data = response.json()
        _logger.info("--vc_data %s" % vc_data)

        vc_data_list = []
        for data in vc_data:
            sophtron_member_id = self.env['sophtron.api.member'].search(
                [('account_id', '=', data['AccountID']), ('member_id', '=', self.member_id)])
            if not sophtron_member_id:
                vc_data_list.append(data)

        return vc_data_list

    @api.model
    def create_journal(self, account_ids, vc_data, journal_id, sophtron_id):
        get_account_data = []
        # for acc in account_ids:
        #     for data_item in vc_data:
        #         match = True
        #         if data_item['AccountNumber'] != acc['name'] or data_item['AccountID'] != acc['id']:
        #             match = False
        #         if match:
        #             get_account_data.append(data_item)
        # matched_accounts = []
        for item in account_ids:
            for acc in vc_data:
                if acc['AccountID'] == item['id'] or acc['AccountNumber'] == item['name']:
                    get_account_data.append(acc)
        # if len(get_account_data) == 0:
        #     get_account_data.append(vc_data[0])

        for acc in get_account_data:
            domain = [('sophtron_id', '=', sophtron_id), ('account_id', '=', acc.get('AccountID', False))]
            acc_object = self.env['sophtron.api.member'].search(domain, limit=1)

            vals = {
                'institution_id': acc.get('UserInstitutionID', False),
                'member_id': acc.get('MemberID', False),
                'account_id': acc.get('AccountID', False),
                'account_name': acc.get('AccountName', False),
                'account_number': acc.get('AccountNumber', False),
                'account_type': acc.get('AccountType', False),
                'account_status': acc.get('Status', False),
                'account_sub_type': acc.get('SubType', False)
            }
            if acc_object:
                acc_object.write(vals)
                acc_object.create_journal()
            else:
                sophtron = self.browse(sophtron_id)
                vals['sophtron_id'] = sophtron_id
                acc_object = self.env['sophtron.api.member'].create(vals)
                if not sophtron.journal_id.sophtron_member_id:
                    sophtron.journal_id.sophtron_member_id = acc_object.id
                    sophtron.journal_id.name = acc.get('AccountName', False)
                    # self.journal_id.type = acc.get('AccountType', False) # type is selection field and it fetching account type like Checking
                    sophtron.journal_id.code = sophtron.journal_id.code
                    sophtron.journal_id.sophtron_account_type = acc.get('AccountType', False)
                    msg = "Successfully updated the journal {} - {}!".format(sophtron.journal_id.name,
                                                                             sophtron.journal_id.id)
                    return msg
                else:
                    journal_id = acc_object.create_journal()
                    msg = "Successfully create the journal {} - {}!".format(journal_id.name, journal_id.id)
                    return msg

    def build_auth_code(self, http_method, url):
        user_id = self.env['ir.config_parameter'].sudo().get_param('sophtron_integration.sophtron_uid')
        auth_key = self.env['ir.config_parameter'].sudo().get_param('sophtron_integration.sophtron_access_key')
        auth_path = url[url.rfind('/'):].lower()
        integration_key = base64.b64decode(auth_key)
        plain_key = f"{http_method.upper()}\n{auth_path}".encode()
        b64_sig = base64.b64encode(hmac.new(integration_key, plain_key, hashlib.sha256).digest()).decode()
        return f'FIApiAUTH:{user_id}:{b64_sig}:{auth_path}'

    def post(self, url, data):
        headers = {'Authorization': self.build_auth_code('post', url)}
        response = requests.post(f"{self.env.company.get_sophtron_url()}{url}", json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_integration_key(self):
        user_id = self.env['ir.config_parameter'].sudo().get_param('sophtron_integration.sophtron_uid')
        return self.post(self.api_endpoints['GetUserIntegrationKey'], {'Id': user_id}).get(
            'IntegrationKey')

    def get_user_institutions_by_user(self):
        user_id = self.env['ir.config_parameter'].sudo().get_param('sophtron_integration.sophtron_uid')
        return self.post(self.api_endpoints['GetUserInstitutionsByUser'], {'UserID': user_id})

    def run_api_calls(self):
        user_id = self.env['ir.config_parameter'].sudo().get_param('sophtron_integration.sophtron_uid')
        auth_key = self.env['ir.config_parameter'].sudo().get_param('sophtron_integration.sophtron_access_key')
        if not user_id or not auth_key:
            raise exceptions.UserError(
                _('Missing environment variables: Ensure "SophtronApiUserId" and "SophtronApiUserSecret" are set.'))

        integration_key = self.get_integration_key()
        connections = self.get_user_institutions_by_user()

        if connections and len(connections) > 0:
            connection = next((c for c in connections if 'OwnerName' in c), connections[0])
            transaction_url = f"https://vc.sophtron-prod.com/api/vc/transactions/{self.institution_id}"
            vc_response = requests.post(transaction_url, json={"accountId": self.account_id},
                                        headers={'IntegrationKey': integration_key})
            vc_response.raise_for_status()
            vc_data = vc_response.json()
            _logger.info("--vc_data %s" % vc_data)
            # return yaml.dump(vc_data.get('credentialSubject'))
        else:
            return "Please create a UserInstitution for demo."

    def fetch_all_transactions(self):
        start_dt = "2001-01-01T00:00:00Z"
        start_date_obj = datetime.strptime(start_dt, "%Y-%m-%dT%H:%M:%SZ")
        end_dt = "2025-01-08T00:00:00Z"
        end_date_obj = datetime.strptime(end_dt, "%Y-%m-%dT%H:%M:%SZ")
        for rec in self.sophtron_client_member_ids:
            rec.fetch_transactions(start_date_obj, end_date_obj)
