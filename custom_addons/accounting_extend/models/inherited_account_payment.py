# -*- coding: utf-8 -*-

from odoo import fields, api, Command, models, _
from odoo.exceptions import ValidationError, UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    bill_line_ids = fields.One2many('bill.account.payment.line', 'payment_id', string="Bill Details", copy=False)
    is_payment_done = fields.Boolean("Payment Done", copy=False)
    amount = fields.Monetary(currency_field='currency_id', compute='_compute_calculate_payment_amount', store=True)
    higher_amount = fields.Boolean(default=False)
    partner_payment_warning = fields.Text(
        compute='higher_amount_value_update',
        groups="account.group_account_invoice,account.group_account_readonly",
    )

    @api.onchange('amount')
    def higher_amount_value_update(self):
        for rec in self:
            total_amount = sum(line.payment_amount for line in rec.bill_line_ids)
            if rec.amount > total_amount and not rec.is_internal_transfer:
                rec.higher_amount = True
                rec.partner_payment_warning = _(
                    'Total amount Is More Than due amount : %(total_amount_extra)s',
                    total_amount_extra=(rec.amount - total_amount)
                )
            else:
                rec.partner_payment_warning = ''
                rec.higher_amount = False

    @api.depends('bill_line_ids.payment_amount')
    def _compute_calculate_payment_amount(self):
        for rec in self:
            if not rec.is_internal_transfer:
                # Calculate the total payment amount from the related lines
                total_amount = sum(line.payment_amount for line in rec.bill_line_ids)
                rec.amount = total_amount

    # @api.constrains('amount', 'bill_line_ids')
    # def _check_payment_amount_constrains(self):
    #     for record in self:
    #         if record.bill_line_ids and sum(record.bill_line_ids.mapped('payment_amount')) > record.amount:
    #             raise ValidationError(
    #                     _("Payment amount must be lower than amount."))
    #         if record.bill_line_ids and sum(record.bill_line_ids.mapped('payment_amount')) != record.amount:
    #             raise ValidationError(
    #                     _("Payment amount must be same as bill amount."))

    @api.onchange("partner_id", "payment_type")
    def onchange_partner_id(self):
        move_list = []
        if self.partner_id and self.payment_type in ['outbound']:
            move_ids = self.env['account.move'].search([
                ('partner_id', '=', self.partner_id.id),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'in_payment', 'partial']),
                ('move_type', 'in', ['in_invoice','out_refund']), ('amount_residual', '>', 0)
            ])
            # payment_id = self.env['account.payment'].search([
            #     ('partner_id', '=', self.partner_id.id),
            #     ('partner_type', '=', 'supplier')
            # ], order="id desc", limit=1)
            previous_payment = 0
            if move_ids:
                for move in move_ids:
                    payment = self.search([]).filtered(lambda line: move in line.reconciled_bill_ids)
                    if payment:
                        previous_payment = payment[0].amount
                    move_amount = move.amount_total
                    move_list.append((0, 0, {
                        'move_id': move.id,
                        'invoice_date': move.invoice_date,
                        'amount_total': move_amount,
                        'previous_payment': move.amount_total - move.amount_residual,
                        'due_amount': move.amount_residual,
                        'ref': move.ref,
                        'gl_acc': self.company_id.write_off_account_id.id
                    }))
            self.bill_line_ids = [(6, 0, [])]
            self.bill_line_ids = move_list
        elif self.partner_id and self.payment_type in ['inbound']:
            move_ids = self.env['account.move'].search([
                ('partner_id', '=', self.partner_id.id),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'in_payment', 'partial']),
                ('move_type', '=', ['out_invoice','in_refund']), ('amount_residual', '>', 0)
            ])
            # payment_id = self.env['account.payment'].search([
            #     ('partner_id', '=', self.partner_id.id),
            #     ('partner_type', '=', 'customer')
            # ], order="id desc", limit=1)
            previous_payment = 0
            if move_ids:
                for move in move_ids:
                    payment = self.search([]).filtered(lambda line: move in line.reconciled_bill_ids)
                    if payment:
                        previous_payment = payment[0].amount
                    move_amount = move.amount_total
                    move_list.append((0, 0, {
                        'move_id': move.id,
                        'invoice_date': move.invoice_date,
                        'amount_total': move_amount,
                        'previous_payment': previous_payment,
                        'due_amount': move.amount_residual,
                        'ref': move.ref,
                        'gl_acc': self.company_id.write_off_account_id.id
                    }))
            self.bill_line_ids = [(6, 0, [])]
            self.bill_line_ids = move_list

        else:
            self.bill_line_ids = [(6, 0, [])]
        default_paid_line = self.bill_line_ids.filtered(
            lambda line: line.move_id.id == self.env.context.get('default_paid_line_id'))
        if default_paid_line:
            total_amount = 0
            for line in default_paid_line:
                line.is_paid = True
                line._onchange_is_paid()
                line.payment_amount = line.due_amount
                total_amount = sum(line.due_amount for line in self.bill_line_ids.filtered(lambda line:line.is_paid))
            self.amount = total_amount

    def action_post(self):
        # inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        # for record in self:
        #     pass
            # if record.bill_line_ids and sum(record.bill_line_ids.mapped('payment_amount')) > record.amount:
            #     raise ValidationError(
            #         _("Payment amount must be lower than amount."))
            # if record.bill_line_ids and sum(record.bill_line_ids.mapped('payment_amount')) != record.amount:
            #     raise ValidationError(
            #         _("Payment amount must be same as bill amount."))
        result = super(AccountPayment, self).action_post()
        if not self.env.context.get('is_called') and not self.reversed_payment_id:
            self.validate_payment()
        un_selected_lines = self.bill_line_ids.filtered(lambda line:not line.is_paid)
        if un_selected_lines:
            un_selected_lines.unlink()
        return result

    def validate_payment(self):
        reconcile_list = []
        if self.bill_line_ids and self.destination_account_id and self.payment_type in ['outbound']:
            bill_line_ids = self.bill_line_ids.filtered(lambda r: r.is_paid)
            if not bill_line_ids:
                raise ValidationError(
                    _("Select any one bill details."))
            write_off_line_vals = []
            for line in bill_line_ids:
                if line.allowed_write_off:
                    write_off_amount_currency = line.remaining_balance
                    if self.payment_type == 'outbound':
                        write_off_amount_currency = -write_off_amount_currency

                    write_off_line_vals.append({
                        'name': _('Write-Off'),
                        'account_id': line.gl_acc.id,
                        'partner_id': self.partner_id.id,
                        'currency_id': self.currency_id.id,
                        'amount_currency': write_off_amount_currency,
                        'balance': self.currency_id._convert(
                            write_off_amount_currency, self.company_id.currency_id, line.move_id.company_id, self.date),
                    })

                # Add write-off entries to the existing payment
            if write_off_line_vals:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'ref': _('Write-Off'),
                    'date': self.date,
                    'line_ids': [Command.create(line) for line in write_off_line_vals]
                }

                # Add write-off entries to the existing move
                if self.move_id.state == 'posted':
                    self.move_id.button_draft()  # Set to draft if posted
                existing_lines = self.move_id.line_ids
                new_lines = self._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)
                existing_line_ids = {line.id for line in existing_lines}
                new_line_ids = {line.get('id') for line in new_lines if 'id' in line}

                lines_to_write = []
                for existing_line in existing_lines:
                    if existing_line.id in new_line_ids:
                        new_line_vals = next(line for line in new_lines if line.get('id') == existing_line.id)
                        lines_to_write.append((1, existing_line.id, new_line_vals))

                for new_line in new_lines:
                    if 'id' not in new_line:
                        lines_to_write.append((0, 0, new_line))

                lines_to_remove = [line.id for line in existing_lines if line.id not in new_line_ids]
                if lines_to_remove:
                    lines_to_write.extend([(2, line_id, 0) for line_id in lines_to_remove])

                self.move_id.with_context(skip_account_move_synchronization=True).write({'line_ids': lines_to_write})
                self.move_id.with_context(is_called=True).action_post()
                self.env.add_to_compute(self.env['account.move']._fields['name'], self.move_id)
            debit_line_ids = self.line_ids.filtered(lambda line: line.debit)
            credit_line_ids = self.bill_line_ids.filtered(lambda line: line.is_paid)
            move_line_ids = (
                        self.line_ids.filtered(lambda line: line.debit) + self.bill_line_ids.move_id.line_ids.filtered(
                    lambda line: line.credit))
            partial_reconcile_ids = self.env["account.partial.reconcile"]
            for debit_line in debit_line_ids:
                for credit_line in credit_line_ids:
                    credit_move_lines = credit_line.move_id.line_ids.filtered(lambda line: line.credit > 0)
                    for credit_move_line in credit_move_lines:
                        amount = min(abs(self.amount), abs(credit_line.payment_amount))
                        if credit_line.allowed_write_off:
                            amount = amount + credit_line.remaining_balance
                        if not amount:
                            continue
                        vals = {
                            'debit_move_id': debit_line.id,
                            # 'credit_move_id': credit_line.move_id.line_ids.filtered(lambda line: line.credit)[0].id,
                            'credit_move_id': credit_move_line.id,
                            'amount': amount,
                            'debit_amount_currency': amount,
                            'credit_amount_currency': amount,
                        }
                        partial_reconcile_ids += self.env["account.partial.reconcile"].create(vals)
            reconciled_move_line_ids = move_line_ids.filtered('reconciled')
            if reconciled_move_line_ids:
                partial_reconcile_ids = partial_reconcile_ids.filtered(lambda
                                                                           record: record.debit_move_id in reconciled_move_line_ids or record.credit_move_id in reconciled_move_line_ids)
                self.env["account.full.reconcile"].create({
                    'partial_reconcile_ids': [(6, 0, partial_reconcile_ids.ids)],
                    'reconciled_line_ids': [(6, 0, reconciled_move_line_ids.ids)],
                })

        elif self.bill_line_ids and self.destination_account_id and self.payment_type in ['inbound']:
            bill_line_ids = self.bill_line_ids.filtered(lambda r: r.is_paid)
            if not bill_line_ids:
                raise ValidationError(
                    _("Select any one Invoice details."))
            write_off_line_vals = []
            for line in bill_line_ids:
                if line.allowed_write_off:
                    write_off_amount_currency = line.remaining_balance
                    if self.payment_type == 'outbound':
                        write_off_amount_currency = -write_off_amount_currency

                    write_off_line_vals.append({
                        'name': _('Write-Off'),
                        'account_id': line.gl_acc.id,
                        'partner_id': self.partner_id.id,
                        'currency_id': self.currency_id.id,
                        'amount_currency': write_off_amount_currency,
                        'balance': self.currency_id._convert(
                            write_off_amount_currency, self.company_id.currency_id, line.move_id.company_id, self.date),
                    })

                # Add write-off entries to the existing payment
            if write_off_line_vals:
                move_vals = {
                    'journal_id': self.journal_id.id,
                    'ref': _('Write-Off'),
                    'date': self.date,
                    'line_ids': [Command.create(line) for line in write_off_line_vals]
                }

                # Add write-off entries to the existing move
                if self.move_id.state == 'posted':
                    self.move_id.button_draft()  # Set to draft if posted
                existing_lines = self.move_id.line_ids
                new_lines = self._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)
                existing_line_ids = {line.id for line in existing_lines}
                new_line_ids = {line.get('id') for line in new_lines if 'id' in line}

                lines_to_write = []
                for existing_line in existing_lines:
                    if existing_line.id in new_line_ids:
                        new_line_vals = next(line for line in new_lines if line.get('id') == existing_line.id)
                        lines_to_write.append((1, existing_line.id, new_line_vals))

                for new_line in new_lines:
                    if 'id' not in new_line:
                        lines_to_write.append((0, 0, new_line))

                lines_to_remove = [line.id for line in existing_lines if line.id not in new_line_ids]
                if lines_to_remove:
                    lines_to_write.extend([(2, line_id, 0) for line_id in lines_to_remove])

                self.move_id.with_context(skip_account_move_synchronization=True).write({'line_ids': lines_to_write})
                self.move_id.with_context(is_called=True).action_post()
                self.env.add_to_compute(self.env['account.move']._fields['name'], self.move_id)
            debit_line_ids = self.line_ids.filtered(lambda line: line.credit)
            credit_line_ids = self.bill_line_ids.filtered(lambda line: line.is_paid)
            move_line_ids = (
                    self.line_ids.filtered(lambda line: line.credit) + self.bill_line_ids.move_id.line_ids.filtered(
                lambda line: line.debit))
            partial_reconcile_ids = self.env["account.partial.reconcile"]
            for debit_line in debit_line_ids:
                for credit_line in credit_line_ids:
                    amount = min(abs(self.amount), abs(credit_line.payment_amount))
                    if credit_line.allowed_write_off:
                        amount = amount + credit_line.remaining_balance
                    if not amount:
                        continue
                    vals = {
                        'debit_move_id': credit_line.move_id.line_ids.filtered(lambda line: line.debit).id,
                        'credit_move_id':debit_line.id ,
                        'amount': amount,
                        'debit_amount_currency': amount,
                        'credit_amount_currency': amount,
                    }
                    partial_reconcile_ids += self.env["account.partial.reconcile"].create(vals)
            reconciled_move_line_ids = move_line_ids.filtered('reconciled')
            if reconciled_move_line_ids:
                partial_reconcile_ids = partial_reconcile_ids.filtered(lambda
                                                                           record: record.debit_move_id in reconciled_move_line_ids or record.credit_move_id in reconciled_move_line_ids)
                self.env["account.full.reconcile"].create({
                    'partial_reconcile_ids': [(6, 0, partial_reconcile_ids.ids)],
                    'reconciled_line_ids': [(6, 0, reconciled_move_line_ids.ids)],
                })

        # else:
        #     raise ValidationError(
        #         _("Bill details records not found."))
