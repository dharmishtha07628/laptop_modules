'''
Created on Oct 20, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _

class PaymentAllocation(models.TransientModel):
    _name = "account.payment.allocation"
    _description ='Payment Allocation'
    
    @api.model
    def _get_payment(self):
        if self._context.get('active_model') == 'account.payment':
            return [(6,0, self._context.get('active_ids'))]
        
    @api.model
    def _get_invoice(self):
        if self._context.get('active_model') == 'account.move':
            return [(6,0, self._context.get('active_ids'))]
        
    
    partner_id = fields.Many2one('res.partner', required = True)
    account_id = fields.Many2one('account.account', required = True)
    show_child = fields.Boolean('Show parent/children')    
    
    line_ids = fields.One2many('account.payment.allocation.line', 'allocation_id')
    invoice_line_ids = fields.One2many('account.payment.allocation.line', 'allocation_id', domain = [('type', '=', 'invoice')])
    payment_line_ids = fields.One2many('account.payment.allocation.line', 'allocation_id', domain = [('type', '=', 'payment')])
    other_line_ids = fields.One2many('account.payment.allocation.line', 'allocation_id', domain = [('type', '=', 'other')])
    
    company_id = fields.Many2one('res.company', required = True, default = lambda self : self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')
    
    balance = fields.Monetary(compute ='_calc_balance')
    
    payment_ids = fields.Many2many('account.payment', default = _get_payment)
    invoice_ids = fields.Many2many('account.move', default = _get_invoice)
    
    writeoff_acc_id = fields.Many2one('account.account', string='Write off Account')
    writeoff_journal_id = fields.Many2one('account.journal', string='Write off Journal')
    writeoff_ref = fields.Char('Write off Reference')
    
    create_entry = fields.Boolean('Create Account/Partner Entry')
    entry_journal_id = fields.Many2one('account.journal', string='Account/Partner Entry Journal')
    entry_name = fields.Char('Entry Reference')
    
    @api.onchange('account_id', 'partner_id', 'show_child', 'company_id')
    def _reset_lines(self):
        if self.account_id and self.partner_id:
            for line_type in ['invoice', 'payment', 'other']:
                fname = '%s_line_ids' % line_type
                self[fname] = False
                domain = [('account_id', '=', self.account_id.id), ('reconciled', '=', False), ('company_id', '=', self.company_id.id)]
                if self.show_child:
                    partner_id = self.partner_id
                    while partner_id.parent_id:
                        partner_id = partner_id.parent_id
                    domain.append(('partner_id', 'child_of', partner_id.ids))
                else:
                    domain.append(('partner_id', '=', self.partner_id.id))            
                if line_type == 'invoice':                        
                    domain.extend([('move_id.move_type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund'])])
                elif line_type == 'payment':
                    domain.append(('payment_id', '!=', False))     
                else:
                    domain.extend([('move_id.move_type', 'not in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']), ('payment_id', '=', False)])                
                for move_line in self.env['account.move.line'].search(domain):
                    if line_type != 'payment' and move_line.move_id.state != 'posted':
                        continue
                    allocate = move_line.payment_id in self.payment_ids or move_line.move_id in self.invoice_ids                    
                    self[fname] += self[fname].new({
                        'move_line_id' : move_line.id,
                        'allocate' : allocate,
                        'type' : line_type
                        })
                    
    @api.onchange('payment_ids')         
    def _onchange_payment_ids(self):
        if self.payment_ids:
            self.account_id = self.payment_ids[0].destination_account_id
            self.partner_id = self.payment_ids[0].partner_id
            self._reset_lines()
            
    @api.onchange('invoice_ids')         
    def _onchange_invoice_ids(self):
        if self.invoice_ids:
            self.account_id = self.invoice_ids.mapped('line_ids.account_id').filtered(lambda account : account.account_type in ['asset_receivable', 'liability_payable'])[:1]
            self.partner_id = self.invoice_ids[0].partner_id
            self._reset_lines()
            
                    
    @api.depends('invoice_line_ids.allocate_amount', 'payment_line_ids.allocate_amount', 'other_line_ids.allocate_amount')
    def _calc_balance(self):
        for record in self:
            balance = 0
            for line in record.invoice_line_ids + record.payment_line_ids + record.other_line_ids:
                if line.allocate:
                    balance += line.allocate_amount
            record.balance = balance
    

    def validate(self):         
        
        if self.balance and self.writeoff_acc_id and self.writeoff_journal_id:
                        
            move_vals= {
                'journal_id' : self.writeoff_journal_id.id,
                'ref': self.writeoff_ref or _('Write-Off'),
                'date' : max(self.line_ids.mapped('move_line_id.date')),
                'line_ids' : [
                        (0,0, {
                            'account_id' : self.account_id.id,
                            'partner_id' : self.partner_id.id,
                            'debit' : -self.balance if self.balance < 0 else 0,
                            'credit' : self.balance if self.balance > 0 else 0,
                            }),
                        (0,0, {
                            'account_id' : self.writeoff_acc_id.id,
                            'partner_id' : self.partner_id.id,
                            'credit' : -self.balance if self.balance < 0 else 0,
                            'debit' : self.balance if self.balance > 0 else 0,
                            })                        
                    ]
                }
            move_id = self.env['account.move'].create(move_vals)
            move_id.post()            
            move_line_id = move_id.line_ids.filtered(lambda line : line.account_id == self.account_id)
            self.env["account.payment.allocation.line"].create({
                'allocation_id' : self.id,
                'type' : 'other',
                'move_line_id' : move_line_id.id,
                'allocate' : True,
                'allocate_amount' : abs(move_line_id.balance)
                })
        
        debit_line_ids = self.line_ids.filtered(lambda line :  line.move_line_id.debit)
        credit_line_ids = self.line_ids.filtered(lambda line :  line.move_line_id.credit)
        # if not debit_line_ids or not credit_line_ids:
        #     raise Warning('Select at least one payment & one invoice')
        #
        move_line_ids = (debit_line_ids + credit_line_ids).mapped('move_line_id')
                                    
        partner_ids = move_line_ids.mapped('partner_id')
        partner_balance = False
        if len(partner_ids) > 1 and self.create_entry:
            partner_balance = dict.fromkeys(partner_ids.ids, 0)
        
        partial_reconcile_ids = self.env["account.partial.reconcile"]
        
        for debit_line in debit_line_ids:
            for credit_line in credit_line_ids:
                amount = min (abs(debit_line.allocate_amount), abs(credit_line.allocate_amount))
                if not amount:
                    continue
                max_date = max(debit_line.move_line_id.date, credit_line.move_line_id.date)
                vals = {
                    'debit_move_id' : debit_line.move_line_id.id,
                    'credit_move_id' : credit_line.move_line_id.id,
                    'amount' : amount,                                        
                    'debit_amount_currency' : debit_line.move_line_id.company_currency_id._convert(amount, debit_line.move_line_id.currency_id, debit_line.move_line_id.company_id, max_date),
                    'credit_amount_currency' : credit_line.move_line_id.company_currency_id._convert(amount, credit_line.move_line_id.currency_id, credit_line.move_line_id.company_id, max_date)
                    
                    }

                partial_reconcile_ids += self.env["account.partial.reconcile"].create(vals)
                if partner_balance:
                    partner_balance[debit_line.move_line_id.partner_id.id] += amount
                    partner_balance[credit_line.move_line_id.partner_id.id] -= amount
                
                debit_line.allocate_amount -= amount * (debit_line.allocate_amount < 0 and -1 or 1)
                credit_line.allocate_amount -= amount * (credit_line.allocate_amount < 0 and -1 or 1)  
                        
        reconciled_move_line_ids = move_line_ids.filtered('reconciled')
        if reconciled_move_line_ids:            
            partial_reconcile_ids = partial_reconcile_ids.filtered(lambda record : record.debit_move_id in reconciled_move_line_ids or record.credit_move_id in reconciled_move_line_ids)
            self.env["account.full.reconcile"].create({
                'partial_reconcile_ids' : [(6,0, partial_reconcile_ids.ids)],
                'reconciled_line_ids' : [(6,0, reconciled_move_line_ids.ids)],
                })                                    
                
        if partner_balance:
            move_vals= {
                'journal_id' : self.entry_journal_id.id,
                'ref': self.entry_name or 'Payment Allocation',
                'date' : max(move_line_ids.mapped('date')),
                'line_ids' : []
                }
            for partner_id, balance in partner_balance.items():
                if not balance:
                    continue
                move_vals['line_ids'].append((0,0, {
                    'account_id': self.account_id.id,
                    'name' : '',
                    'partner_id' : partner_id,
                    'credit' : balance > 0 and balance or 0,
                    'debit' : balance < 0 and -balance or 0
                    }))
            move_id=self.env['account.move'].create(move_vals)
            move_id.post()
            move_id.line_ids.reconcile()
            move_line_ids +=  move_id.line_ids                              
            
        return {
            'type' : 'ir.actions.act_window_close'
            }
