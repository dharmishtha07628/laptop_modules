# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError, UserError


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    routing_number = fields.Char(string="Routing Number", required=False, tracking=True)
    void_check_att = fields.Binary(string="Upload Attachments", required=True, tracking=True)
    void_check_att_ids = fields.Many2many('ir.attachment', 'void_check_bank_rel', 'void_check_id', 'bank_id',
                                          string="Upload Attachments")
    # payment_method_id = fields.Many2one(
    #     string='Payment Method',
    #     comodel_name='account.payment.method',
    #     ondelete='cascade'
    # )
    payment_method_type = fields.Selection([('direct_deposit', 'Direct Deposit'), ('credit_card', 'Credit Card')],
                                           default="direct_deposit", string="Payment Method")
    authorize_signature = fields.Binary('Authorize Signature')
    # credit_card_number = fields.Char('Credit Card Number')
    acc_number = fields.Char(required=False)
    # masked_credit_card = fields.Char(string="Credit Card Number", compute='_compute_masked_credit_card')
    masked_acc_number = fields.Char(string="Account Number", compute='_compute_masked_acc_number')
    # credit_card_att = fields.Binary('Credit Card Document')
    bank_id = fields.Many2one('res.bank', string='Bank', store=True, readonly=False, tracking=True, )
    active_bank = fields.Boolean('Active', tracking=True)
    allow_out_payment = fields.Boolean(
        string="Verified",
        tracking=True,
        help='Sending fake invoices with a fraudulent account number is a common phishing practice. '
             'To protect yourself, always verify new bank account numbers, preferably by calling the vendor, as phishing '
             'usually happens when their emails are compromised. Once verified, you can activate the ability to send money.'
    )

    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state = fields.Many2one('res.country.state', 'Fed. State', domain="[('country_id', '=?', country)]")
    country = fields.Many2one('res.country')
    bank_name = fields.Char('Bank Name', store=True)


    # two create method in same model
    # @api.model
    # def create(self, vals):
    #     record = super(ResPartnerBank, self).create(vals)
    #     self._log_change_to_partner_chatter(record, 'create')
    #     return record

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('active_bank'):
                self._deactivate_other_accounts(vals.get('partner_id'))
            if vals.get('bank_name'):
                existing_bank = self.env['res.bank'].sudo().search([
                    ('name', 'ilike', vals['bank_name'])
                ], limit=1)
                if existing_bank:
                    vals['bank_id'] = existing_bank.id
                else:
                    new_bank = self.env['res.bank'].sudo().create({'name': vals['bank_name']})
                    vals['bank_id'] = new_bank.id
        record = super(ResPartnerBank, self).create(vals_list)
        self._log_change_to_partner_chatter(record, 'create')
        return record

    def write(self, vals):
        if 'active_bank' in vals and vals.get('active_bank'):
            self._deactivate_other_accounts(vals.get('partner_id'))
        return super(ResPartnerBank, self).write(vals)

    def _deactivate_other_accounts(self, partner_id):
        other_accounts = self.search([
            ('partner_id', '=', partner_id),
            ('id', '!=', self.id),
            ('active_bank', '=', True)
        ])
        if other_accounts:
            other_accounts.write({'active_bank': False})

    @api.constrains('active_bank')
    def _check_active_bank(self):
        for record in self:
            if record.active_bank:
                active_accounts = record.partner_id.bank_ids.filtered(
                    lambda line: line.id != record.id and line.active_bank)
                if active_accounts:
                    active_accounts.write({'active_bank': False})

    # def onchange(self, values: dict, field_names: list, fields_spec: dict):
    #     # Call the original onchange method and capture its result
    #     result = super().onchange(values, field_names, fields_spec)
    #     if values.get('active_bank'):
    #         other_accounts = self.search([
    #             ('partner_id', '=', self.partner_id.id),
    #             ('id', '!=', values.get('id')),
    #             ('active_bank', '=', True)
    #         ])
    #         if other_accounts:
    #             other_accounts.write({'active_bank': False})
    #     return result

    @api.onchange('active_bank', 'payment_method_type', 'allow_out_payment')
    def _change_direct_deposit_verification(self):
        for record in self:
            if record.active_bank and record.payment_method_type == 'direct_deposit':
                if not record.allow_out_payment:
                    # Set active_bank to False and raise ValidationError
                    record.active_bank = False
                    raise ValidationError("Direct Deposit accounts can only be marked as active if they are verified.")
            # if record.active_bank:
            #     active_accounts = self.partner_id.bank_ids.filtered(lambda line: line.id != record.id)
            #     if active_accounts:
            #         for acc in active_accounts:
            #             acc.write({'active_bank': False})
            # raise ValidationError("Only one bank account can be marked as active at a time.")

    # @api.depends('credit_card_number')
    # def _compute_masked_credit_card(self):
    #     for record in self:
    #         if record.credit_card_number:
    #             masked = '*' * (len(record.credit_card_number) - 4) + record.credit_card_number[-4:]
    #             record.masked_credit_card = masked
    #         else:
    #             record.masked_credit_card = False

    @api.onchange('allow_out_payment')
    def _check_one_active_account(self):
        for record in self:
            if record.allow_out_payment:
                other_active_accounts = self.search([
                    ('partner_id', '=', record.partner_id.id),
                    ('allow_out_payment', '=', True)
                ])
                if other_active_accounts:
                    raise exceptions.ValidationError("Only one active account is allowed per partner.")

    @api.onchange('bank_id')
    def _change_bank_id(self):
        for record in self:
            if record.bank_id:
                bank = self.env['res.bank'].browse(record.bank_id.id)
                if bank:
                    record.routing_number = bank.routing_number
                else:
                    record.routing_number = False  # Clear the routing number if bank not found
            else:
                record.routing_number = False  #

    @api.onchange('allow_out_payment')
    def _onchange_send_money(self):
        if self.allow_out_payment and not self.void_check_att_ids:
            raise exceptions.UserError("You must attach a document before activating this account.")
        if self.allow_out_payment:
            other_active_accounts = self.search([
                ('partner_id', '=', self.partner_id.id),
                ('allow_out_payment', '=', True)
            ])
            if other_active_accounts:
                raise exceptions.ValidationError("Only one active account is allowed per partner.")

    @api.depends('acc_number')
    def _compute_masked_acc_number(self):
        for record in self:
            if record.acc_number:
                masked = '*' * (len(record.acc_number) - 4) + record.acc_number[-4:]
                record.masked_acc_number = masked
            else:
                record.masked_acc_number = False

    def write(self, vals):
        if 'active_bank' in vals and vals.get('active_bank'):
            self._deactivate_other_accounts(vals.get('partner_id'))
            # Handle bank_name to bank_id before write
        if 'bank_name' in vals and not vals.get('bank_id'):
            bank_name = vals['bank_name']
            existing_bank = self.env['res.bank'].sudo().search([
                ('name', 'ilike', bank_name)
            ], limit=1)
            if existing_bank:
                vals['bank_id'] = existing_bank.id
            else:
                new_bank = self.env['res.bank'].sudo().create({'name': bank_name})
                vals['bank_id'] = new_bank.id
        res = super(ResPartnerBank, self).write(vals)
        if any(field in vals for field in ['active_bank', 'routing_number', 'name']):
            for record in self:
                self._log_change_to_partner_chatter(record, 'write', vals)
        return res

    def _log_change_to_partner_chatter(self, record, action, vals=None):
        if not vals:
            vals = {}
        # Log changes
        changed_fields = []
        if 'active_bank' in vals:
            changed_fields.append(f"Active: {record.active_bank} -> {vals['active_bank']}")
        if 'routing_number' in vals:
            changed_fields.append(f"Routing Number: {record.routing_number} -> {vals['routing_number']}")
        if 'acc_number' in vals:
            changed_fields.append(f"Account Number: {record.acc_number} -> {vals['acc_number']}")
        if 'allow_out_payment' in vals:
            changed_fields.append(f"Account Verified: {record.allow_out_payment} -> {vals['allow_out_payment']}")

        #
        # if changed_fields:
        #     partner_id = record.partner_id.id if record.partner_id else False
        #     if partner_id:
        #         self.env['mail.message'].create({
        #             'res_id': partner_id,
        #             'model': 'res.partner',
        #             'message_type': 'notification',
        #             'body': f"Bank Account  {action}d. Changes: {', '.join(changed_fields)}.",
        #             'author_id': self.env.user.id,
        #         })

    @api.constrains('routing_number', 'partner_id')
    def _check_unique_routing_number(self):
        for record in self:
            if record.routing_number:
                # Validate routing number format
                if not (record.routing_number.isdigit() and len(record.routing_number) == 9):
                    raise ValidationError("The Routing Number must be exactly 9 numerical digits.")
                # Check for duplicates
                duplicates = self.search([
                    ('routing_number', '=', record.routing_number),
                    ('partner_id', '=', record.partner_id.id),
                    ('id', '!=', record.id),
                ])
                if duplicates:
                    raise ValidationError("Routing number must be unique per partner.")

class ResBank(models.Model):
    _inherit = 'res.bank'

    routing_number = fields.Char(string="Routing Number", required=True, unique=True)

    @api.constrains('routing_number')
    def _check_routing_number(self):
        for record in self:
            if record.routing_number:
                if not (record.routing_number.isdigit() and len(record.routing_number) == 9):
                    raise ValidationError("The Routing Number must be exactly 9 numerical digits.")

    @api.depends('routing_number')
    def _compute_display_name(self):
        for account in self:
            account.display_name = f"{account.name} -{account.routing_number if account.routing_number else ''}"
