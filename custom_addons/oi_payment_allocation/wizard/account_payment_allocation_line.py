'''
Created on Oct 20, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api

class PaymentAllocationLines(models.TransientModel):
    _name = "account.payment.allocation.line"
    _description ='Payment Allocation Line'
    
    allocation_id = fields.Many2one('account.payment.allocation',  ondelete='cascade')
    type = fields.Selection([('invoice', 'Invoice'), ('payment', 'Payment'), ('other', 'Other')])
    
    move_line_id = fields.Many2one('account.move.line', required = True, ondelete = 'cascade')
   
    company_currency_id = fields.Many2one(related='move_line_id.company_currency_id')
    currency_id = fields.Many2one(related='move_line_id.currency_id')
    amount_residual = fields.Monetary(related='move_line_id.amount_residual')
    partner_id = fields.Many2one(related='move_line_id.partner_id')
    ref = fields.Char(related='move_line_id.ref', readonly = True)
    name = fields.Char(related='move_line_id.name', readonly = True)
    date_maturity = fields.Date(related='move_line_id.date_maturity', readonly = True)
    date = fields.Date(related='move_line_id.date', readonly = True)
        
    allocate = fields.Boolean()
    allocate_amount = fields.Monetary()
    
    invoice_id = fields.Many2one(related='move_line_id.move_id', readonly = True)
    payment_id = fields.Many2one(related='move_line_id.payment_id', readonly = True, string='Payment')
    move_id = fields.Many2one(related='move_line_id.move_id', readonly = True, string = 'Entry')
    balance = balance = fields.Monetary(related='move_line_id.balance', readonly = True)
    
    payment_date = fields.Date(related='payment_id.date', readonly = True, string='Payment Date')
    payment_amount = fields.Monetary(compute = '_calc_payment_amount')
    
    date_invoice = fields.Date(related='invoice_id.invoice_date', readonly = True)
    invoice_amount = fields.Monetary(compute = "_calc_invoice_amount")
    
    amount_residual_display = fields.Monetary(compute = '_calc_amount_residual_display', string='Unallocated Amount')
    
    sign = fields.Integer()
    
    @api.depends('type','allocation_id')
    def _calc_sign(self):
        for record in self:
            record.sign = (record.type in ['invoice', 'other'] and -1 or 1) * (record.move_line_id.account_id.account_type == 'liability_payable' and 1 or -1)
            
    @api.depends('sign','balance')
    def _calc_payment_amount(self):
        for record in self:
            record.payment_amount = record.balance
            
    @api.depends('sign','balance')
    def _calc_invoice_amount(self):
        for record in self:
            record.invoice_amount = record.balance
            
    
    @api.depends('amount_residual','sign')
    def _calc_amount_residual_display(self):
        for record in self:
            record.amount_residual_display = record.amount_residual
            record.allocate_amount = record.amount_residual
    
    @api.onchange('allocate','amount_residual_display')
    def _calc_allocate_amount(self):
        line_ids = self.allocation_id.invoice_line_ids + self.allocation_id.payment_line_ids + self.allocation_id.other_line_ids
        other_lines = line_ids.filtered(lambda line : line !=self and line.allocate)
        total = 0
        for line in other_lines:
            total += line.allocate_amount
        
        total = total
        
        if total < 0:
            total = abs(total)
        else:
            total = 0
        
        if not self.allocate:
            self.allocate_amount = 0
        elif total:
            self.allocate_amount = min(self.amount_residual_display, total)
        else:
            self.allocate_amount = self.amount_residual_display
                        
    @api.onchange('allocate_amount')
    def _onchange_allocate_amount(self):
        self.allocation_id._calc_balance()
                        
            