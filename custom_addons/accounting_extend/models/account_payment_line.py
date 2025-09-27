# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class AccountPaymentLine(models.Model):
    _name = "bill.account.payment.line"
    _inherit = ["mail.thread"]
    _description = "Account Payment Line"
    _rec_name = "move_id"

    payment_id = fields.Many2one('account.payment', string="Payment")
    move_id = fields.Many2one('account.move', string="Bill No.")
    ref = fields.Char('ref', compute='compute_update_description', store=True)
    invoice_date = fields.Date("Bill Date", compute='compute_update_description', store=True)
    amount_total = fields.Monetary("Amount Total", compute='compute_update_description', store=True,
                                   help='BILL/Invoice Total Amount to Pay')
    previous_payment = fields.Monetary("Previous Payment", help="Bill/Invoice amount which is already Paid")
    due_amount = fields.Monetary("Due amount", compute='compute_update_description', store=True,
                                 help="Bill/Invoice Remaining Payment amount")
    is_paid = fields.Boolean(string="Paid")
    payment_amount = fields.Monetary("Payment Amount")
    reconcile_id = fields.Many2one('account.partial.reconcile')
    write_off_amt = fields.Monetary(string="Short / Over Paid")
    gl_acc = fields.Many2one('account.account', domain="[('deprecated', '=', False)]", string="GL Account")
    currency_id = fields.Many2one(related="payment_id.currency_id")
    remaining_balance = fields.Float('Remaining Balance', help="this Consider due amount - Payment amount")
    allowed_write_off = fields.Boolean('Write off')
    due_date = fields.Date( compute='compute_update_description', store=True)

    # @api.constrains('payment_amount')
    # def _check_payment_amount_constrains(self):
    #     for record in self:
    #         if record.due_amount < record.payment_amount:
    #             raise ValidationError(
    #                     _("Payment amount must be lower than due amount."))
    #         if record.payment_amount > 0 and not record.is_paid:
    #             raise ValidationError(
    #                     _("Select check box."))

    # @api.constrains('is_paid')
    # def _check_is_paid_constrains(self):
    #     for record in self:
    #         if record.is_paid and record.payment_amount <= 0:
    #             raise ValidationError(
    #                     _("Payment amount must be greater than 0."))

    @api.onchange('is_paid')
    def _onchange_is_paid(self):
        if self.is_paid and  self.env.context.get('is_paid_click'):
            self.payment_amount = self.due_amount
        elif self.env.context.get('is_paid_click'):
            self.payment_amount = 0.0
        else:
            self.payment_amount = self.payment_amount

    @api.onchange('due_amount', 'payment_amount')
    def _onchange_payment_remaining_balance(self):
        if self.payment_amount:
            self.remaining_balance = self.due_amount - self.payment_amount
            self.with_context(is_paid_from_payment=True).write({'is_paid': True})
        else:
            self.remaining_balance = 0.0

    @api.onchange('allowed_write_off')
    def set_default_gl_account(self):
        for rec in self:
            if rec.allowed_write_off:
                rec.gl_acc = rec.payment_id.company_id.write_off_account_id.id
            else:
                rec.gl_acc = False

    @api.depends('move_id.ref', 'move_id.invoice_date', 'move_id.amount_total', 'move_id.amount_residual')
    def compute_update_description(self):
        for rec in self:
            if rec.move_id:
                rec.ref = rec.move_id.ref
                rec.invoice_date = rec.move_id.invoice_date
                rec.amount_total = rec.move_id.amount_total
                rec.due_amount = rec.move_id.amount_residual
                # rec.previous_payment = rec.move_id.amount_total - rec.move_id.amount_residual
                rec.due_date = rec.move_id.invoice_date_due
            else:
                rec.ref = ''
                rec.invoice_date = False
                rec.amount_total = 0.0
                rec.due_amount = 0.0
                # rec.previous_payment = 0.0
