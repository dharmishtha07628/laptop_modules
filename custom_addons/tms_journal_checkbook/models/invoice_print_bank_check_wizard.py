# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class InvoicePrintBankCheckWizard(models.TransientModel):
    _inherit = 'invoice.print.bank.check.wizard'

    check_number = fields.Integer(string='Check Number', default=1)
    remittance_table_ids = fields.Many2many('bill.account.payment.line', string='Remittance Table')
    address = fields.Text(string="Remittance Address")
    company_id = fields.Many2one('res.company')

    def print_check(self):
        if self.env.context.get("is_reprint"):
            return self.env.ref(
                'odoo_check_management.bank_check_leaf_print_report'
            ).report_action(self)
        if self.env['issued.bank.check.history'].search(
                [('check_number', '=', self.check_number), ('bank_check_book_id', '=', self.check_book_id.id)]):
            raise UserError(
                _("Check number %s is already issued. Please try another check number." % self.check_number))
        vals = {
            "check_number": self.check_number,
            "bank_check_book_id": self.check_book_id.id,
            "address":self.address,
            "remittance_table_ids": self.remittance_table_ids.ids,
            "company_id":self.env.company.id
        }
        self.company_id = self.env.company
        self.check_history_id = self.env["issued.bank.check.history"].create(vals).id
        self.check_book_id.current_check_number = self.check_number
        result = super().print_check()
        self.amount_in_words = self.currency_id.amount_to_text(self.amount)
        self.pay_name_line1 = self.check_history_id.customer_id.name
        partner = self.check_history_id.customer_id
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
        self.address = full_address


        print("--", self._context)
        if self._context.get('payment_id', False):
            payment_id = self.env['account.payment'].browse(self._context.get('payment_id', False))
            self.check_history_id.payment_id = self._context.get('payment_id', False)
            payment_id.with_context(force_post=1).action_post()
            self.check_history_id.batch_id = payment_id.batch_ref_id
        if self.env.context.get('created_from_batch'):
            batch_id = self.env.context.get('active_id')
            batch_record = self.env['account.batch.payment'].browse(batch_id)
            batch_record.with_context(force_post=1).confirm()
            current_check_payment = self.env['account.payment'].search(
                [('batch_ref_id', '=', batch_record.id), ('partner_id', '=', self.partner_id.id)], limit=1)
            self.check_history_id.payment_id = current_check_payment.id
            self.check_history_id.batch_id = batch_record.id
            print(batch_record)
        return result

    def print_all_checks(self):
        # Get all the records in the wizard view
        # records = self.search([])
        for rec in self:
            rec.print_check()
        return self.env.ref(
            'odoo_check_management.bank_check_leaf_print_report'
        ).report_action(self)
