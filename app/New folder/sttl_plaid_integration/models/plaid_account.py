# This model stores bank accounts fetched from plaid API.

from odoo import models, fields

class PlaidAccount(models.Model):
    _name = "plaid.account"
    _inherit = ["mail.thread"]

    name = fields.Char(string="Account Name")
    account_id = fields.Char(string="Account No")
    currency_id = fields.Many2one("res.currency")
    balance = fields.Monetary(string="Balance", store=True)
    account_type = fields.Char(string="Account Type")
    account_subtype = fields.Char(string="Account Subtype")
    bank_id = fields.Many2one("plaid.bank")
