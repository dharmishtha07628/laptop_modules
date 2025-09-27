# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import format_date, formatLang


class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    generate_from_recurring = fields.Boolean()
    is_recurring_payment = fields.Boolean('Is Recurring Payment', default=False)
    template_id = fields.Many2one('account.recurring.template', 'Recurring Template',
                                  domain=[('state', '=', 'done')])
    date_begin = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    recurring_payment_count = fields.Integer(compute='_recurring_count', string='Recurring Payment')
    recurring_payment_id = fields.Many2one('recurring.payment', string="Recurring Payment")
    rc_attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='self_account_payment_ir_attachments_rel',
        string='Documents')
    related_payment_id = fields.Many2one(
        'account.payment', readonly=True,
        string='Related Payment',
    )

    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer', 'destination_journal_id')
    def _compute_destination_account_id(self):
        self.destination_account_id = False
        for pay in self:
            if pay.is_internal_transfer:
                pay.destination_account_id = pay.destination_journal_id.company_id.transfer_account_id
                pay.destination_account_id = pay.destination_journal_id.default_account_id
            elif pay.partner_type == 'customer':
                # Receive money from invoice or send money to refund it.
                if pay.partner_id:
                    pay.destination_account_id = pay.partner_id.with_company(
                        pay.company_id).property_account_receivable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        *self.env['account.account']._check_company_domain(pay.company_id),
                        ('account_type', '=', 'asset_receivable'),
                        ('deprecated', '=', False),
                    ], limit=1)
            elif pay.partner_type == 'supplier':
                # Send money to pay a bill or receive money to refund it.
                if pay.partner_id:
                    pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_payable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        *self.env['account.account']._check_company_domain(pay.company_id),
                        ('account_type', '=', 'liability_payable'),
                        ('deprecated', '=', False),
                    ], limit=1)

    # def action_draft(self):
    #     if self.related_payment_id and self.related_payment_id.move_id:
    #         self.related_payment_id.move_id.button_draft()
    #         self.related_payment_id.unlink()
    #     return super().action_draft()

    def validate_journal_entries(self):
        for payment in self:
            if payment.paired_internal_transfer_payment_id:
                paired_payment = payment.paired_internal_transfer_payment_id
                if paired_payment.state != 'draft':
                    paired_payment.action_draft()

    def _create_paired_internal_transfer_payment(self):
        ''' Create paired internal transfer payments ensuring a valid journal entry. '''
        # super(AccountPayment, self)._create_paired_internal_transfer_payment()

        for payment in self:
            if payment.paired_internal_transfer_payment_id :
                # Ensure only one outstanding payments/receipts account
                transfer_account = self.company_id.transfer_account_id
                if not transfer_account:
                    raise UserError(_("Transfer account is not defined in company settings."))

                # Validate journal entries
                self.validate_journal_entries()

                # Get the transfer line
                transfer_line = payment.line_ids.filtered(
                    lambda line: line.account_id == transfer_account)

                # Handle the paired payment
                paired_payment = payment.paired_internal_transfer_payment_id
                if paired_payment:
                    if paired_payment.state != 'draft':
                        paired_payment.action_draft()

                    if not paired_payment.line_ids.filtered(lambda l: l.account_id == transfer_account):
                        raise UserError(
                            _("Paired payment must include exactly one outstanding payments/receipts account."))

                    outstanding_account_lines = paired_payment.line_ids.filtered(
                        lambda l: l.account_id == transfer_account)
                    if len(outstanding_account_lines) != 1:
                        raise UserError(
                            _("Paired payment journal entry must have exactly one outstanding payments/receipts account."))

                    paired_payment.unlink()
            elif not self.env.context.get('already_done'):
                    transfer_account = self.company_id.transfer_account_id
                    transfer_line = payment.line_ids.filtered(
                    lambda line: line.account_id == transfer_account)
                    if transfer_line:
                        if transfer_line.reconciled:
                            transfer_line.reconcile()
                        transfer_line.write({
                            'account_id': payment.destination_journal_id.default_account_id.id
                        })
                    payment.action_draft()
                    payment.with_context(already_done=True).action_post()

    def _recurring_count(self):
        for rec in self:
            recurring_payment = self.env['recurring.payment'].search_count(
                [('id', '=', self.recurring_payment_id.id), ('template_id', '=', self.template_id.id)])
            rec.recurring_payment_count = recurring_payment or 0

    def button_open_recurring_payment(self):
        ''' Redirect the user to this payment journal.
        :return:    An action on account.move.
        '''
        self.ensure_one()
        return {
            'name': _("Recurring Payment"),
            'type': 'ir.actions.act_window',
            'res_model': 'recurring.payment',
            'context': {'create': False},
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.recurring_payment_id.ids)],
        }

    def confirm_recurring_payment(self):
        self.ensure_one()
        vals = {
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'amount': self.amount,
            'journal_id': self.journal_id.id,
            'payment_type': self.payment_type,
            'state': self.state,
            'date_begin': self.date_begin,
            'date_end': self.date_end,
            'template_id': self.template_id.id
        }
        recurring_payment = self.env['recurring.payment'].create(vals)
        self.recurring_payment_id = recurring_payment.id
        recurring_payment.action_done()

    def _get_aml_default_display_name_list(self):
        # this  method is override odoo default for the change label internal transfer to "transfer from"
        """ Hook allowing custom values when constructing the default label to set on the journal items.

        :return: A list of terms to concatenate all together. E.g.
            [
                ('label', "Vendor Reimbursement"),
                ('sep', ' '),
                ('amount', "$ 1,555.00"),
                ('sep', ' - '),
                ('date', "05/14/2020"),
            ]
        """
        self.ensure_one()
        display_map = self._get_aml_default_display_map()
        values = [
            ('label', _("Transfer From") if self.is_internal_transfer else display_map[(self.payment_type, self.partner_type)]),
            ('sep', ' '),
            ('amount', formatLang(self.env, self.amount, currency_obj=self.currency_id)),
        ]
        if self.partner_id:
            values += [
                ('sep', ' - '),
                ('partner', self.partner_id.display_name),
            ]
        values += [
            ('sep', ' - '),
            ('date', format_date(self.env, fields.Date.to_string(self.date))),
        ]
        return values

    def _get_liquidity_aml_display_name_list(self):
        # this method is override to update the label for internal transfer
        """ Hook allowing custom values when constructing the label to set on the liquidity line.

        :return: A list of terms to concatenate all together. E.g.
            [('reference', "INV/2018/0001")]
        """
        self.ensure_one()
        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                if self.is_internal_transfer:
                    amount = formatLang(self.env, self.amount, currency_obj=self.currency_id)
                    date_str = format_date(self.env, fields.Date.to_string(self.date))
                    # For internal transfers, we use the amount and date with below label
                    return [('transfer_to', _('Transfer To %s - %s' % (amount, date_str)))]
                return [('transfer_to', _('Transfer to %s', self.journal_id.name))]
            else:  # payment.payment_type == 'outbound':
                return [('transfer_from', _('Transfer from %s', self.journal_id.name))]
        elif self.payment_reference:
            return [('reference', self.payment_reference)]
        else:
            return self._get_aml_default_display_name_list()


    def new(self, values=None, origin=None, ref=None):
        payment = super().new(values, origin, ref)
        if self._context.get('default_is_internal_transfer'):
            values.update({'is_internal_transfer': True})
        return payment

    @api.depends('partner_id', 'journal_id', 'destination_journal_id')
    def _compute_is_internal_transfer(self):
        for payment in self:
            is_internal_transfer = payment.is_internal_transfer
            payment.is_internal_transfer = payment.partner_id \
                                           and payment.partner_id == payment.journal_id.company_id.partner_id \
                                           and payment.destination_journal_id
            if is_internal_transfer:
                payment.is_internal_transfer = is_internal_transfer


