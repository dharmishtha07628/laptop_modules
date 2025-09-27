# -*- coding: utf-8 -*-
from odoo import fields, api, models, _


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    payment_line_id = fields.Many2one('bill.account.payment.line', string="Payment Line", copy=False)
