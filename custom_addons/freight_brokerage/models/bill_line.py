# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class BillLine(models.Model):
    _name = "bill.line"

    rate_method = fields.Selection(selection=[
        ('distance', 'Distance'),
        ('flat', 'Flat'),
        ('weight', 'Weight'),
        ('other', 'Other')], string='Rate Method')
    revenue_product_id = fields.Many2one('product.product', string='Revenue Code')
    memo = fields.Char(string='Memo')
    qty = fields.Float(string='Quantity')
    rate = fields.Float(string='Rate')
    total = fields.Float(string='Total', compute="_compute_total", store=True)
    brokerage_order_id = fields.Many2one('brokerage.order', string='Brokerage Order')

    @api.depends('rate', 'qty')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.rate * rec.qty
