# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    discount_price = fields.Float(string="Discount Price", default=0.0)
    global_discount_line = fields.Boolean()
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer / Vendor',
        compute='_compute_partner_id', inverse='_inverse_partner_id', store=True, readonly=False, precompute=True,
        ondelete='restrict',
    )
    name = fields.Char(
        string='Memo',
        compute='_compute_name', store=True, readonly=False, precompute=True,
        tracking=True,
    )

    # Do not depend on `move_id.partner_id`, the inverse is taking care of that
    def _compute_partner_id(self):
        for line in self:
            line.partner_id = line.move_id.partner_id.commercial_partner_id

    @api.onchange('partner_id')
    def _inverse_partner_id(self):
        self._conditional_add_to_compute('account_id', lambda line: (
                line.display_type == 'payment_term'  # recompute based on settings
        ))

    @api.onchange('discount_price')
    def _onchange_discount_price(self):
        """
            Approach to computing the percentage of discount based on the discounted price
        """
        for rec in self:
            if rec.discount_price <= (rec.quantity * rec.price_unit):
                if rec.discount_price == 0.00:
                    rec.update({
                        'discount': 0.00
                    })
                else:
                    rec.update({
                        'discount': (rec.discount_price * 100) / (rec.quantity * rec.price_unit)
                    })
            elif (rec.discount_price > rec.price_subtotal):
                raise ValidationError(_(
                    "Discounted amount must be less than '%(amount)s'.",
                    amount=rec.quantity * rec.price_unit
                ))

    @api.onchange('discount')
    def _onchange_discount(self):
        for rec in self:
            rec.update({
                'discount_price': (rec.quantity * rec.price_unit * rec.discount) / 100
            })

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Invoice Lines'),
            'template': '/accounting_extend/static/Sample-XLS-File/revenue_code_invoice_line.xls'
        }]

    # elif self.move_type == 'in_invoice':
    #     return [{
    #         'label': _('Import Template for Expense Lines'),
    #         'template': '/accounting_extend/static/Sample-XLS-File/expense_code_invoice_line.xlsx'
    #     }]

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         context = self.env.context
    #         invoice = self.env['account.move'].browse(context.get('move_id'))
    #         if vals.get('revenue_product_id'):
    #             product_id = self.env['product.product'].browse(vals.get('revenue_product_id'))
    #         else:
    #             product_id = self.env['product.product'].browse(vals.get('product_id'))
    #
    #         account_id = self.env['account.account'].browse(vals.get('account_id'))
    #         if product_id:
    #             product = product_id.id
    #         else:
    #             product = False
    #
    #         if not account_id and not product:
    #             if context.get('default_move_type') == 'in_invoice':
    #                 account = product.property_account_expense_id
    #             if self.env.context.get('default_move_type') == 'out_invoice':
    #                 account = product.property_account_income_id
    #         if not account_id and not vals.get('account_id'):
    #             raise ValidationError("Account is required for importing lines")
    #         elif not account_id and vals.get('account_id'):
    #             raise ValidationError(_('"%s" Account not found in the system') % account_id.rsplit(' ')[0])
    #
    #         line_values = [{
    #             'account_id': account_id.id,
    #             'product_id': product_id.id,
    #             'revenue_product_id': product_id.id,
    #             'name': vals.get('name'),
    #             'quantity': vals.get('quantity'),
    #             'move_id': invoice.id,
    #             # 'product_uom_id': uom_record.id,
    #             'price_unit': vals.get('price_unit'),
    #             # 'discount': values.get('disc'),
    #             'analytic_distribution': self.get_analytic_data(vals.get('analytic_distribution'))
    #         }]
    #         invoice.write({'invoice_line_ids': [(0, 0, line_values)]})
    #         # invoice.invoice_line_ids = [(4, [line_values])]
    #         return super(AccountMoveLine, self).create(line_values)

    @api.model_create_multi
    def create(self, vals_list):
        move_id = self.env.context.get("parent_id", False)
        if move_id:
            for vals in vals_list:
                vals['move_id'] = move_id
                vals['analytic_distribution'] = self.get_analytic_data(vals.get('analytic_distribution'))
                product_id = vals.get('revenue_product_id') or vals.get('product_id')
                vals['product_id'] = product_id
        return super(AccountMoveLine, self).create(vals_list)

    def get_analytic_data(self, data):
        lines = {}
        if data:
            # data = data
            analytic_plan = self.env['account.analytic.plan'].search(
                [('default_applicability', '!=', 'unavailable')])
            for key, value in data.items():
                names = key.split(",")
                id_list = []
                for index in range(0, len(analytic_plan)):
                    if index < len(names):
                        analytic_id = self.env['account.analytic.account'].search(
                            [('name', '=', names[index].strip())],
                            limit=1)
                        id_list.append(str(analytic_id.id))
                    else:
                        id_list.append("")
                if id_list:
                    id_str = ",".join(id_list)
                    lines.update({id_str: value})
        return lines
