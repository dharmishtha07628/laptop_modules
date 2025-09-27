# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

import logging
_logger = logging.getLogger(__name__)

# 2 :  imports of odoo [Imports of odoo]

import odoo
from odoo import api, fields, models, _  # alphabetically ordered
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class BankCheck(models.Model):
    # Private attributes
    _inherit = 'res.bank'

    # Fields declaration
    check_image = fields.Binary("Check Image")
    check_attribute_line_ids = fields.One2many("bank.check.attribute.line",
                                                "bank_check_id",
                                                "Check Attributes")
    check_height = fields.Float(string='Check Hight',
                                 default=93,
                                 required=True)
    check_width = fields.Float(string='Check Width',
                                default=203,
                                required=True)
    max_char_in_line1 = fields.Integer(
        "Maximum Characters",
        help="Maximum characters in 'Amount in words Line1' field.\n Aplicable if Check attributes has both attributes(Amount In words Line1 & Amount In words Line2)"
    )
    check_measure_unit = fields.Selection([("cm", "CM"),
                                            ("in", "Inches"),
                                            ("mm", "MM")],
                                           "Measurement Unit",
                                           default="mm",
                                           required=True)

    def redirect_to_bank_check_page(self):
        self.ensure_one()
        if not self.check_attribute_line_ids:
            raise UserError(
                _('First you have to set bank Check attributes. '
                  'Then you will be able to configure attribute(s) values'))
        return {
            'type': 'ir.actions.act_url',
            'target': '_blank',
            'url': "/bank/check/%s" % self.id,
        }


class BankCheckAttributeLine(models.Model):
    # Private attributes
    _name = 'bank.check.attribute.line'
    _description = 'Check Attribute Line'

    name = fields.Many2one("bank.check.attribute",
                           string='Name',
                           required=True)
    bank_check_id = fields.Many2one("res.bank",
                                     string='Bank Check')
    font_size = fields.Integer(string='Font Size', default=20)
    font_family = fields.Char(string='Font Family')
    letter_spacing = fields.Integer(string='Letter Spacing', default=0)
    top_displacement = fields.Integer(string='Top displacement')
    left_displacement = fields.Integer(string='Left displacement')
    bottom_displacement = fields.Integer(string='Bottom displacement')
    right_displacement = fields.Integer(string='Right displacement')
    height = fields.Integer(string='Height')
    width = fields.Integer(string='Width')

    def reset_values(self):
        for obj in self:
            obj.write({
                "top_displacement": 0,
                "left_displacement": 0,
                "bottom_displacement": 0,
                "right_displacement": 0,
                "height": 0,
                "width": 0,
            })

    @api.onchange("name")
    def onchange_name(self):
        if self.name and self.name.attribute == "check_date" and not self.letter_spacing:
            self.letter_spacing = 12


class BankCheckAttribute(models.Model):
    # Private attributes
    _name = 'bank.check.attribute'
    _description = 'Bank Check Attribute'

    name = fields.Char(string='Name', required=True)
    attribute = fields.Selection(
        [('check_date', "Date"), ('pay_line1', "Pay Line 1"),
         ('pay_line2', "Pay Line 2"),
         ('amount_line_1', "Amount Line 1 (in words)"),
         ('amount_line_2', "Amount Line 2 (in words)"),
         ('amount_box', "Amount Box"), ('account_number', "Account Number"),
         ('address','Remittance Address'),
         ('ac_pay', "A/C Pay Label")],
        required=True)
    demo_data = fields.Char("Demo Data For Preview")
    demo_data_date = fields.Date("Demo Date For Preview",
                                 default=fields.Date.today())
    date_format = fields.Selection([("ddMMyyyy", "DD MM YYYY"),
                                    ("MMddyyyy", "MM DD YYYY")],
                                   "Date Format",
                                   default="ddMMyyyy")


class BankCheckBook(models.Model):
    # Private attributes
    _name = 'bank.check.book'
    _description = 'Check Attribute Book'

    name = fields.Char("Name", required=True)
    active = fields.Boolean("Active", default=True)
    bank_check_id = fields.Many2one("res.bank",
                                     "Bank Check",
                                     )
    # domain="[('check_image', '!=', False)]"
    check_book_leaves = fields.Integer("Leaves Count",
                                        required=True,
                                        default=20)
    initial_check_number = fields.Integer("Initial Check Number")
    last_check_number = fields.Integer("Last Check Number")
    account_number = fields.Char(
        "Account Number",
        help="This account number will print on check if check bank has account number attribute."
    )
    issued_check_history_ids = fields.One2many("issued.bank.check.history",
                                                "bank_check_book_id",
                                                "Issue Check History")
    # currency_id = fields.Many2one("res.currency", "Currency")

    # def set_check_book_number(self):
    #     for rec in self:
    #         if rec.check_book_leaves and rec.initial_check_number:
    #             rec.last_check_number = rec.initial_check_number + rec.check_book_leaves - 1

    # def create_check_leaves(self):
    #     for rec in self:
    #         if rec.check_book_leaves and rec.initial_check_number and rec.last_check_number:
#                 i = rec.initial_check_number
#                 for i in range(rec.initial_check_number, rec.last_check_number + 1, 1):
#                     vals = {
#                         "check_number": i,
#                         "bank_check_book_id": rec.id
#                     }
#                     self.env["issued.bank.check.history"].create(vals)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(BankCheckBook, self).create(vals_list)
        # res.set_check_book_number()
        # res.create_check_leaves()
        return res

    # @api.onchange("check_book_leaves", "initial_check_number")
    # def on_change_initial_check_number(self):
    #     self.set_check_book_number()

    # def btn_create_check_leaves(self):
    #     self.ensure_one()
    #     if not self.check_book_leaves:
    #         raise UserError(_("Please fill check book leaves count first."))
    #     if not self.initial_check_number:
    #         raise UserError(_("Please fill staring check number first."))
    #     self.create_check_leaves()


class IssuesBankCheckHistory(models.Model):
    # Private attributes
    _name = 'issued.bank.check.history'
    _description = 'Issued bank check'
    _rec_name = "check_number"

    state = fields.Selection([('blank', 'Blank'),
                              ('printed', 'Printed'),
                              ('cancelled', 'Cancelled')],
                             "State",
                             default="blank")
    check_number = fields.Integer("Check Number", required=True)
    customer_id = fields.Many2one("res.partner", "Customer")
    issue_date = fields.Date("Date")
    amount = fields.Float("Amount")
    currency_id = fields.Many2one("res.currency", "Currency")
    issued = fields.Boolean("Check Issued")
    bank_check_book_id = fields.Many2one("bank.check.book",
                                          "Check Register",
                                          required=True)
    is_ac_pay = fields.Boolean("A/C Pay Check")
    cancelled = fields.Boolean("Check Cancelled")
    paid_to = fields.Char("Paid To")

    @api.constrains('check_number', 'bank_check_book_id')
    def _check_check_number_for_bank(self):
        for record in self:
            already_exist = self.search([
                ('check_number', '=', record.check_number),
                ('bank_check_book_id', '=', record.bank_check_book_id.id),
            ])
            if len(already_exist) > 1:
                raise ValidationError(
                    _("Check number %s is not valid. It has been already used. "
                      "Please use different Check number.") % record.check_number)

    # def name_get(self):
    #     result = []
    #     for record in self:
    #         result.append((record.id, record.bank_check_book_id.name + " " + str(record.check_number)))
    #     return result

    # @api.onchange("check_number")
    # def on_change_check_number(self):
    #     if self.check_number and self.bank_check_book_id and self.check_number not in range(
    #             self.bank_check_book_id.initial_check_number,
    #             self.bank_check_book_id.last_check_number + 1, 1):
    #         raise UserError(
    #             _("Invalid check number. check number should be in range %s to %s (including last number)."
    #               ) % (self.bank_check_book_id.initial_check_number,
    #                    self.bank_check_book_id.last_check_number))

    # @api.model_create_multi
    # def create(self, vals_list):
    #     self.on_change_check_number()
    #     res = super(IssuesBankcheckHistory, self).create(vals_list)
    #     return res

    # @api.model
    # def write(self, vals):
    #     for rec in self:
    #         rec.on_change_check_number()
    #     res = super(IssuesBankcheckHistory, self).write(vals)
    #     return res

    def print_check(self):
        self.ensure_one()
        if self.issued:
            raise UserError(
                _("Check has been already printed with Check number %s" % self.check_number))
        # if not self.customer_id or not self.issue_date or self.amount <= 0:
        #     raise UserError(_("One of the field is missing may be Customer, Date or Amount."))
        wizard_id = self.env["invoice.print.bank.check.wizard"].create({
            "partner_id": self.customer_id.id,
            "check_book_id": self.bank_check_book_id.id,
            "check_history_id": self.id,
            "pay_name_line1": self.customer_id.name if self.customer_id else self.paid_to,
            "amount": self.amount,
        })
        wizard_id.amount_in_words = wizard_id.currency_id.amount_to_text(wizard_id.amount)
        return {
            'name': _("Print Check"),
            'view_mode': 'form',
            'view_id': False,
            'res_model': "invoice.print.bank.check.wizard",
            'res_id': wizard_id.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }

    def do_cancel_check(self):
        for obj in self:
            obj.state = "cancelled"


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _prepare_html(self, html, report_model=False):
        bodies, res_ids, header, footer, specific_paperformat_args = super(
            IrActionsReport, self)._prepare_html(html, report_model=False)
        for rec in self:
            if rec.model == "res.bank" and bodies:
                bodies = [
                    bytes(bodies[0].replace(
                        b'class="container"', b'class="" style="margin:0px"').replace(
                            b'class="article o_report_layout_clean"', b'class=""'))
                ]
        return bodies, res_ids, header, footer, specific_paperformat_args
