# -*- coding: utf-8 -*-

from odoo import models, api, _, fields


class AccountBankTransactionLine(models.Model):
    _inherit = "account.bank.transaction.line"

    merchant_name = fields.Char()

