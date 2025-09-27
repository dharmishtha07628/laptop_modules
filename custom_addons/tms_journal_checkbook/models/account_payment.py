# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    check_history_id = fields.One2many('issued.bank.check.history','payment_id',string="Check Id")
    
    def check_history_action(self):
        action = self.env.ref('tms_journal_checkbook.bank_check_history_action').sudo().read()[0]
        action['domain'] = [('id','in',self.check_history_id.ids)]
        return action

    def action_draft(self):
        res = super().action_draft()
        if self.check_history_id:
            self.check_history_id.do_cancel_check()
        return res

    def action_cancel(self):
        res = super().action_cancel()
        if self.check_history_id:
            self.check_history_id.state = 'cancelled'

    def action_post(self):
        if not self.payment_type == 'inbound':
             if not self.is_internal_transfer:
                if not 'force_post' in self._context and self.env.context.get("is_pay_bill") and self.payment_method_line_id.name.lower() == "check":
                    current_check_number = self.journal_id.bank_check_book_id.current_check_number
                    current_check_number += 1
                    while self.env['issued.bank.check.history'].search([('check_number','=',current_check_number),('bank_check_book_id','=',self.journal_id.bank_check_book_id.id)]):
                        current_check_number += 1

                    action = self.env.ref('odoo_check_management.invoice_bank_check_print_action').sudo().read()[0]
                    # here we need to write the logic for create data to display in check print wizard list view
                    check_payment_vals = []
                    vendors = self.bill_line_ids.filtered(lambda m: m.is_paid).move_id.mapped('partner_id')
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
                            "amount": sum(self.bill_line_ids.filtered(lambda m: m.move_id.partner_id == vendor and m.is_paid).mapped('payment_amount')),
                            # "payment_id": self.id,
                            "remittance_table_ids": self.bill_line_ids.filtered(lambda p: p.is_paid),
                            'address':full_address
                        })
                        check_number += 1
                    wizard_ids = self.env["invoice.print.bank.check.wizard"].create(check_payment_vals)
                    action['context'] = {
                        'default_check_book_id': self.journal_id.bank_check_book_id.id,
                        'default_check_number': current_check_number,
                        'payment_id': self.id,
                        'active_ids': wizard_ids.ids
                    }
                    action['domain'] = [('id', 'in', wizard_ids.ids)]
                    return action
        return super().action_post()
