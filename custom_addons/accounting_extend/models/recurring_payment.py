# -*- coding: utf-8 -*-

from odoo import models

class RecurringPaymentLine(models.Model):
    _inherit = 'recurring.payment.line'

    def action_create_payment(self):
        vals = {
            'payment_type': self.recurring_payment_id.payment_type,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'date': self.date,
            'ref': self.recurring_payment_id.name,
            'partner_id': self.partner_id.id,
            'generate_from_recurring': True
        }
        payment = self.env['account.payment'].create(vals)
        if payment:
            if self.recurring_payment_id.journal_state == 'posted':
                payment.action_post()
            self.write({'state': 'done', 'payment_id': payment.id})
