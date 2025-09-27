# coding: utf-8

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    check_image = fields.Binary("Check Image", related="bank_id.check_image", readonly=False)
    check_height = fields.Float(string='Check Hight', related="bank_id.check_height", readonly=False)
    check_width = fields.Float(string='Check Width', related="bank_id.check_width", readonly=False)
    max_char_in_line1 = fields.Integer("Maximum Characters",
        related="bank_id.max_char_in_line1", readonly=False,
        help="Maximum characters in 'Amount in words Line1' field.\n Aplicable if Check attributes has both attributes(Amount In words Line1 & Amount In words Line2)")
    check_measure_unit = fields.Selection([
        ("cm", "CM"),
        ("in", "Inches"),
        ("mm", "MM")],
        "Measurement Unit", related="bank_id.check_measure_unit", readonly=False)
    check_attribute_line_ids = fields.One2many(related="bank_id.check_attribute_line_ids", readonly=False)

    # check book
    bank_check_book_id = fields.Many2one("bank.check.book", "Check Register")

    # Other fields
    is_visible_check_config = fields.Boolean(string='Visible Check Config', compute="_compute_is_visible_check_config",
        store=True, help="Visible Nacha Config page if '  ACH - BATCH' payment method is available in outgoing payments")

    signed_person = fields.Char(string="Signed By", copy=False)

    signed_time = fields.Datetime(string="Signed On", copy=False)

    signature = fields.Image(
        string="Signature",
        copy=False, attachment=True, max_width=800, max_height=800)

    @api.depends('outbound_payment_method_line_ids')
    def _compute_is_visible_check_config(self):
        check = self.env.ref('account_batch_payment.account_payment_method_check_out', raise_if_not_found=False)
        for rec in self:
            if check:
                rec.is_visible_check_config = True if rec.outbound_payment_method_line_ids.filtered(lambda p: p.payment_method_id.id == check.id) else False
            else:
                rec.is_visible_check_config = False

    def redirect_to_bank_check_page(self):
        self.ensure_one()
        if not self.bank_account_id or not self.bank_id:
            raise UserError(_('First you have to set bank account and bank.'))
        return self.bank_id.redirect_to_bank_check_page()

    # override create method for creating check register
    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for journal in res:
            if journal.is_visible_check_config:
                journal.bank_check_book_id = journal.bank_check_book_id.create({
                    'name': journal.name + " - " + "Check Register",
                    'bank_check_id': journal.bank_id.id,
                })
        return res

    # # override write method for creating check register if bank_check_book_id is not set in create method
    # def write(self, vals):
    #     res = super().write(vals)
    #     for journal in self:
    #         if journal.is_visible_check_config and not journal.bank_check_book_id:
    #             journal.bank_check_book_id = journal.bank_check_book_id.create({
    #                 'name': journal.name + " - " + "Check Register",
    #                 'bank_check_id': journal.bank_id.id,
    #             })
    #         else:
    #             journal.bank_check_book_id = journal.bank_check_book_id.create({
    #                 'name': journal.name + " - " + "Check Register",
    #                 'bank_check_id': journal.bank_id.id,
    #             })
    #     return res
    #
    def write(self, vals):
        res = super().write(vals)
        for journal in self:
            if  journal.bank_check_book_id:
                journal.bank_check_book_id.bank_check_id = journal.bank_id.id
        return res
