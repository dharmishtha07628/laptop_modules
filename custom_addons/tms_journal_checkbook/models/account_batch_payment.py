# -*- coding: utf-8 -*-

from odoo import fields, api, Command, models, _
from odoo.exceptions import ValidationError, UserError


class AccountBatchPayment(models.Model):
    _inherit = "account.batch.payment"

    check_ids = fields.One2many('issued.bank.check.history', 'batch_id', string="Check")

    def check_history_action(self):
        action = self.env.ref('tms_journal_checkbook.bank_check_history_action').sudo().read()[0]
        action['domain'] = [('id', 'in', self.check_ids.ids)]
        return action

    def confirm(self):
        if not self.batch_type  == 'inbound':
            if not 'force_post' in self._context and self.payment_method_id.code == 'CHECK' and not self.env.context.get(
                    'created_from_batch'):
                if not self.reversed_batch:
                    current_check_number = self.journal_id.bank_check_book_id.current_check_number
                    current_check_number += 1
                    while self.env['issued.bank.check.history'].search([('check_number', '=', current_check_number), (
                            'bank_check_book_id', '=', self.journal_id.bank_check_book_id.id)]):
                        current_check_number += 1
                    action = self.env.ref('odoo_check_management.invoice_bank_check_print_action').sudo().read()[0]
                    check_payment_vals = []
                    vendors = self.line_ids.filtered(lambda m: m.is_paid).move_id.mapped('partner_id')
                    check_number = current_check_number
                    for vendor in vendors:
                        address_parts = [
                            vendor.street or "",
                            vendor.street2 or "",
                            vendor.city or "",
                            (vendor.state_id.name if vendor.state_id else ""),
                            (vendor.country_id.name if vendor.country_id else ""),
                            vendor.zip or "",
                            vendor.phone or ""
                        ]
                        full_address = ", ".join(filter(None, address_parts))  # Filters out empty strings
                        check_payment_vals.append({
                            'partner_id': vendor.id,
                            "check_book_id": self.journal_id.bank_check_book_id.id,
                            "check_number": check_number,
                            "amount": sum(
                                self.line_ids.filtered(lambda m: m.move_id.partner_id == vendor and m.is_paid).mapped(
                                    'amount')),
                            "address":full_address
                            # "payment_id": self.id,
                        })
                        check_number += 1
                    wizard_ids = self.env["invoice.print.bank.check.wizard"].create(check_payment_vals)
                    action['context'] = {
                        'default_check_book_id': self.journal_id.bank_check_book_id.id,
                        'default_check_number': current_check_number,
                        # 'payment_id': self.id,
                        'active_ids': wizard_ids.ids,
                        'created_from_batch': True
                    }
                    action['domain'] = [('id', 'in', wizard_ids.ids)]
                    return action
        return super().confirm()

    def redu_cancel(self):
        res = super().redu_cancel()
        for check_id in self.check_ids:
            check_id.state = "cancelled"
        return res

    def revered_entry(self):
        res = super().revered_entry()
        for check_id in self.check_ids:
            check_id.state = "cancelled"
        return res


