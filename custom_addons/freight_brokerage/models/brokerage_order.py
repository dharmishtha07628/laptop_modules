# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BrokerageOrder(models.Model):
    _name = "brokerage.order"
    _description = "Brokerage Order"
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
    ]

    name = fields.Char('Order')
    order_source = fields.Selection(selection=[
        ('edi', 'EDI'),
        ('manual', 'Manual')], string='Order Source')
    shipment_id_number = fields.Char(string="Shipment ID Number")
    shipment_method_of_payment = fields.Char(string="Shipment Method of Payment")
    must_respond_by = fields.Datetime(string="Must Respond By")
    accepted_or_rejected = fields.Selection([('accepted', 'Accepted'), ('rejected', 'Rejected')], string="Accepted or Rejected")
    order_status = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('billed', 'Billed'),
        ('covered', 'Covered'),
        ('hold', 'Hold'),
        ('in_progress', 'In Progress'),
        ('void', 'Void'),
        ('delivered', 'Delivered'),
        ('quote', 'Quote')], string='Order Status', default='draft')
    external_reference = fields.Char(string="External Reference")
    customer_order_no = fields.Char(string="Customer Order No")

    brokerage_order_reference_ids = fields.One2many('brokerage.order.reference', 'brokerage_order_id', string='Order References')
    brokerage_order_stop_ids = fields.One2many('brokerage.order.stop', 'brokerage_order_id', string='Stop Details')
    brokerage_comment_ids = fields.One2many('brokerage.comment', 'brokerage_order_id', string='Comments')


    # # name = fields.Char('Order')
    # partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    # customer_load_no = fields.Char(string='Customer Load No')
    # customer_bol_no = fields.Char(string='Customer BOL No')
    # original_bol = fields.Many2many('ir.attachment', 'original_bol_rel', string='Original BOL')
    # signed_bol = fields.Many2many('ir.attachment', 'signed_bol_rel', string='Signed BOL')
    # planning_comment = fields.Char(string='Planning Comment')
    # # trailer_type_id = fields.Many2one('trailer.type', string='Trailer Type')

    # # Load Board Posting
    # load_board = fields.Boolean(string='Load Board')

    # load_entered_by_id = fields.Many2one('res.users', string='Load entered by', default=lambda self: self.env.uid)
    # operation_user_id = fields.Many2one('res.users', string='Operation User')
    # # sales rep : TODO:MUB
    # # entry_method = EDI or Manual  TODO:MUB

    # # Billing Tab
    # bill_customer_id = fields.Many2one('res.partner', string='Bill Customer')
    # bill_distance = fields.Float(string='Distance')
    # case_pieces_count = fields.Float(string='Case/pieces count')
    # weight = fields.Float(string='Total Weight')
    # uom_id = fields.Many2one('uom.uom', string='UOM')
    # commodity = fields.Char(string='Commodity')

    # brokerage_order_stop_ids = fields.One2many('brokerage.order.stop', 'brokerage_order_id', string='Stop Details')
    # bill_line_ids = fields.One2many('bill.line', 'brokerage_order_id', string='Bill Lines')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('brokerage.order.sequence') or _('New')
        return super().create(vals_list)
