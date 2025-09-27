# coding: utf-8

from odoo import fields, models



class BankCheckBookInherit(models.Model):
    # Private attributes
    _inherit = 'bank.check.book'

    current_check_number = fields.Integer(string="Current Check Number")


class IssuesBankCheckHistory(models.Model):
    # Private attributes
    _inherit = 'issued.bank.check.history'

    
    payment_id = fields.Many2one('account.payment',string="Payment")
    batch_id = fields.Many2one('account.batch.payment',string="Batch Payment")
    remittance_table_ids = fields.Many2many('bill.account.payment.line', string='Remittance Table')
    address = fields.Text(string="Remittance Address")
    company_address = fields.Text('Company Address')
    company_id = fields.Many2one('res.company')

    def re_print_check(self):
        self.ensure_one()
        partner = self.customer_id

        address_parts = [
            partner.street or "",
            partner.street2 or "",
            partner.city or "",
            (partner.state_id.name if partner.state_id else ""),
            (partner.country_id.name if partner.country_id else ""),
            partner.zip or "",
            partner.phone or ""
        ]
        full_address = ", ".join(filter(None, address_parts))  # Filters out empty strings
        wizard_id = self.env["invoice.print.bank.check.wizard"].create({
            "check_book_id": self.bank_check_book_id.id,
            "check_history_id": self.id,
            "check_number": self.check_number,
            "pay_name_line1": self.customer_id.name if self.customer_id else self.paid_to,
            "amount": self.amount,
            "remittance_table_ids": self.remittance_table_ids.ids,
            "address":full_address,
            "company_id":self.env.company.id
            # "remittance_table_ids": self.payment_id.bill_line_ids.filtered(lambda p: p.is_paid) or False,
        })
        wizard_id.amount_in_words = wizard_id.currency_id.amount_to_text(wizard_id.amount)
        return wizard_id.with_context(is_reprint=True).print_check()

    def do_cancel_check(self):
        for obj in self:
            if obj.payment_id:
                obj.payment_id.action_cancel()
            obj.state = "cancelled"

    def open_payment(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("account.action_account_payments")
        action['domain'] = [('id', '=', self.payment_id.id)]
        action['context'] = {}
        return action

    def open_batch_payment(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("account_batch_payment.action_batch_payment_out")
        action['domain'] = [('id', '=', self.batch_id.id)]
        return action

