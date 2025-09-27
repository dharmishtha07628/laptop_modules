# This model stores banks and their corresponding accounts fetched from plaid API.

from odoo import models, fields

class PlaidBank(models.Model):
    _name = "plaid.bank"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    status = fields.Selection([ ('not_connected', 'Not connected'), ('connected', 'Connected')], default="not_connected")
    account_ids = fields.One2many("plaid.account", "bank_id", string="Accounts")
    access_token = fields.Char(readonly=True)

    def disconnect_accounts(self):
        length = len(self.account_ids) - 1
        while(length>=0):
            self.account_ids[length].unlink()
            length-=1
        self.status = "not_connected"
        self.access_token = ""
