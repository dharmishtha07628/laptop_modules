# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super(ResPartner,self)._get_view(view_id, view_type, **options)

        if view_type == 'form':
            for node in arch.xpath(
                "//field[@name='name']"
                "|//field[@name='vat']"
            ):
                node.attrib['widget'] = ''

        return arch, view
    
    def _bill_total(self):
        self.total_bill = 0
        if not self.ids:
            return True

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self.filtered('id'):
            # price_total is in the company currency
            all_partners_and_children[partner] = self.with_context(active_test=False).search(
                [('id', 'child_of', partner.id)]).ids
            all_partner_ids += all_partners_and_children[partner]

        domain = [
            ('partner_id', 'in', all_partner_ids),
            ('state', 'not in', ['draft', 'cancel']),
            ('move_type', 'in', ('in_invoice', 'in_refund')),
        ]
        price_totals = self.env['account.invoice.report']._read_group(domain, ['partner_id'], ['price_subtotal:sum'])
        for partner, child_ids in all_partners_and_children.items():
            partner.total_bill = sum(
                price_subtotal_sum for partner, price_subtotal_sum in price_totals if partner.id in child_ids)

    is_customer = fields.Boolean(string='Is a Customer',
                                 help="Check this box if this contact is a customer. It can be selected in sales orders.")
    is_supplier = fields.Boolean(string='Is a Vendor',
                                 help="Check this box if this contact is a vendor. It can be selected in purchase orders.")
    vendor_type = fields.Selection([('vendor', 'Vendor'), ('company', 'Company')], string="Vendor Type",
                                   default="vendor")
    vendor_acc = fields.Char(string="Vendor Acc #")
    use_partner_credit_limit = fields.Boolean(
        string='Partner Limit',
        groups='account.group_account_invoice,account.group_account_readonly',
        compute='_compute_use_partner_credit_limit', inverse='_inverse_use_partner_credit_limit', tracking=True)
    credit_limit = fields.Float(
        string='Credit Limit', help='Credit limit specific to this partner.',
        groups='account.group_account_invoice,account.group_account_readonly',
        company_dependent=True, copy=False, readonly=False, tracking=True)
    form_1099 = fields.Selection(
        [('1099-A', '1099-A'), ('1099-B', '1099-B'), ('1099-C', '1099-C'), ('1099-CAP', '1099-CAP'),
         ('1099-DIV', '1099-DIV'), ('1099-G', '1099-G'), ('1099-INT', '1099-INT'), ('1099-K', '1099-K'),
         ('1099-LS', '1099-LS'), ('1099-LTC', '1099-LTC'), ('1099-MISC', '1099-MISC'), ('1099-NEC', '1099-NEC'),
         ('1099-OID', '1099-OID'), ('1099-PATR', '1099-PATR'), ('1099-Q', '1099-Q'), ('1099-QA', '1099-QA'),
         ('1099-R', '1099-R'), ('1099-S', '1099-S'), ('1099-SA', '1099-SA'), ('1099-SB', '1099-SB'),
         ('RRB-1099', 'RRB-1099'), ('SSA-1099', 'SSA-1099')], string="Form 1099")
    federal_tax_classification = fields.Selection(
        [('individual', 'Individual'), ('sole_properietor', 'Sole Properietor'), ('c_corporation', 'C corporation'),
         ('s_corporation', 'S corporation'), ('partnership', 'Partnership'), ('trust_estate', 'Trust/estate'),
         ('llc', 'LLC'), ('other', 'other')], string="Federal Tax Classification",
        help="Check the appropriate box for federal tax classification of the entity/individual")
    llc_tax_classification = fields.Selection([('c', 'C corporation'), ('s', 'S corporation'), ('p', 'Partnership')],
                                              string="LLC Tax Classification",
                                              help="Check the “LLC” box above and, in the entry space, enter the appropriate code (C, S, or P) for the tax classification of the LLC, unless it is a disregarded entity. A disregarded entity should instead check the appropriate box for the tax classification of its owner.")
    foreign_partner = fields.Boolean(string="Any foreign partners, owners, or beneficiaries")
    other_tax_classification = fields.Char(string="Others")
    w9_att = fields.Binary(string="W9 Attachment")
    w9_attachments = fields.Many2many('ir.attachment', 'w9_partner_rel', 'w9_id', 'partner_id')
    w9_file_name = fields.Char('W9 Filename')
    last_update_w9 = fields.Datetime(string="Last Update on")
    doing_business = fields.Char(string="Doing Business")
    exemption_payee_code = fields.Char(string="Exempt payee code")
    fatca_code = fields.Char(string="FATCA Code",
                             help="Exemption from Foreign Account Tax Compliance Act (FATCA) reporting code")
    property_sale_payment_method_id = fields.Many2one('account.payment.method', string="Payment Method",
                                                      domain="[('payment_type','=','inbound')]")
    po_ref = fields.Char(string="Po Number")
    is_po_ref_req = fields.Boolean(string="Is PO Number Required ?")
    same_name_partner_id = fields.Many2one('res.partner', string='Partner with same Tax ID')
    total_bill = fields.Monetary(compute='_bill_total', string="Total Bill",
                                 groups='account.group_account_invoice,account.group_account_readonly')
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
                                                     string="Account Receivable",
                                                     domain="[('account_type', '=', 'asset_receivable'), ('deprecated', '=', False)]",
                                                     help="This account will be used instead of the default one as the receivable account for the current partner",
                                                     required=False)
    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
                                                  string="Account Payable",
                                                  domain="[('account_type', '=', 'liability_payable'), ('deprecated', '=', False)]",
                                                  help="This account will be used instead of the default one as the payable account for the current partner",
                                                  required=False)
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Supplier'), ('both', 'BOTH')],
                                    compute='update_partner_type', store=True)
    is_attachment_required = fields.Boolean(string='Is Attachment Required ?')
    require_merged_attachment = fields.Boolean(string='Required to merged attachments ?')
    revenue_code_ids = fields.One2many(
        'revenue.code', 'partner_id',
        string='Revenue Code',
    )
    expense_code_ids = fields.One2many(
        'expense.code', 'partner_id',
        string='Expense Code',
    )

    @api.constrains('is_customer', 'is_supplier')
    def _check_customer_or_vendor(self):
        for partner in self:
            if not partner.is_customer and not partner.is_supplier:
                raise ValidationError(_("A partner must be either a Customer or a Vendor. Please set at least one."))


    @api.model
    def default_get(self, fields_list):
        """
        default receivable and payble account in customer/vendor
        :param fields_list:
        :return:
        """
        defaults = super(ResPartner, self).default_get(fields_list)

        # Search for default accounts
        default_receivable_account = self.env['account.account'].search([('account_type', '=', 'asset_receivable')],
                                                                        limit=1)
        default_payable_account = self.env['account.account'].search([('account_type', '=', 'liability_payable')],
                                                                     limit=1)
        ctx = self.env.ctx = self.env.context
        
        if ctx.get('default_is_customer'):
            defaults['is_customer'] = True
        if ctx.get('default_is_vendor'):
            defaults['is_vendor'] = True

        if default_receivable_account:
            defaults['property_account_receivable_id'] = default_receivable_account.id
        if default_payable_account:
            defaults['property_account_payable_id'] = default_payable_account.id

        return defaults

    @api.depends('bank_ids')
    def _compute_duplicated_bank_account_partners_count(self):
        for partner in self:
            duplicated_accounts = partner._get_duplicated_bank_accounts()
            partner.duplicated_bank_account_partners_count = len([
                account for account in duplicated_accounts
                if account.payment_method_type != 'credit_card'
            ])

    @api.depends('is_customer', 'is_supplier')
    def update_partner_type(self):
        for rec in self:
            if rec.is_supplier and rec.is_customer:
                rec.partner_type = 'both'
            elif rec.is_supplier:
                rec.partner_type = 'supplier'
            elif rec.is_customer:
                rec.partner_type = 'customer'

    @api.onchange('name')
    def onchange_parter_name(self):
        for partner in self:
            Partner = self.with_context(active_test=False).sudo()
            partner_id = partner._origin.id
            domain = [
                ('name', '=ilike', partner.name),
                ('id', '!=', partner_id),
            ]
            if partner.company_id:
                domain += [('company_id', 'in', [False, partner.company_id.id])]

            #            if Partner.search(domain, limit=1):
            #                raise ValidationError(
            #                    _('A Customer / Vendor with the same name already exists ({})'.format(partner.name)))
            partner.same_name_partner_id = Partner.search(domain, limit=1) or False

    # @api.constrains('name')
    # def _check_name(self):
    #     partner_rec = self.env['res.partner'].search(
    #         [('name', '=', self.name), ('id', '!=', self.id)])
    #     if partner_rec:
    #         raise ValidationError(_('A Customer / Vendor with the same name already exists ({})'.format(self.name)))

    #     @api.depends('name', 'company_id', 'company_registry')
    #     def _compute_same_name_partner_id(self):
    #         for partner in self:
    #             # use _origin to deal with onchange()
    #             partner_id = partner._origin.id
    #             #active_test = False because if a partner has been deactivated you still want to raise the error,
    #             #so that you can reactivate it instead of creating a new one, which would loose its history.
    #             Partner = self.with_context(active_test=False).sudo()
    #             domain = [
    #                 ('name', '=', partner.name),
    #             ]
    #             if partner.company_id:
    #                 domain += [('company_id', 'in', [False, partner.company_id.id])]
    # #            if partner_id:
    # #                domain += [('id', '!=', partner_id), '!', ('id', 'child_of', partner_id)]
    #             # For VAT number being only one character, we will skip the check just like the regular check_vat
    #             partner.same_name_partner_id = Partner.search(domain, limit=1)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('w9_att', False):
                vals['last_update_w9'] = fields.Datetime.now()
            # Sync is_customer to customer_rank
            if vals.get('is_customer'):
                vals['customer_rank'] = 1
            # Sync is_supplier to supplier_rank
            if vals.get('is_supplier'):
                vals['supplier_rank'] = 1
        return super(ResPartner, self).create(vals_list)

    def write(self, vals):
        if vals.get('w9_att', False):
            vals['last_update_w9'] = fields.Datetime.now()
        # Sync is_customer to customer_rank
        if 'is_customer' in vals and vals['is_customer']:
            vals['customer_rank'] = 1
        # Sync is_supplier to supplier_rank
        if 'is_supplier' in vals and vals['is_supplier']:
            vals['supplier_rank'] = 1
        return super(ResPartner, self).write(vals)

    @api.onchange('vendor_type')
    def onchange_vendor_type(self):
        self.vat = False

    @api.onchange('vat', 'federal_tax_classification')
    def onchange_vat(self):
        if self.vat and self.is_supplier:
            clean_value = self.vat.replace('-', '')
            if len(clean_value) != 9:
                raise ValidationError(_("SSN / EIN must have 9 digit."))
            if self.federal_tax_classification in ['individual', 'sole_properietor']:
                self.vat = formatted_value = f"{clean_value[:3]}-{clean_value[3:5]}-{clean_value[5:9]}"
            else:
                self.vat = formatted_value = f"{clean_value[:2]}-{clean_value[2:9]}"

    # @api.constrains('bank_ids')
    # def _check_single_active_account_in_related(self):
    #     for record in self:
    #         active_accounts = record.bank_ids.filtered(lambda acc: acc.active_bank)
    #         if len(active_accounts) > 1:
    #             raise ValidationError("Only one bank account can be marked as active.")

    def action_view_vendor_bills(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_invoice_type")
        all_child = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        action['domain'] = [
            ('move_type', 'in', ('in_invoice', 'in_refund')),
            ('partner_id', 'in', all_child.ids)
        ]
        action['context'] = {'default_move_type': 'in_invoice', 'move_type': 'in_invoice', 'journal_type': 'purchase',
                             'search_default_unpaid': 1}
        return action


class RevenueCode(models.Model):
    _name = 'revenue.code'

    product_id = fields.Many2one('product.product', string='Revenue Code')
    price = fields.Float(string='Price')
    partner_id = fields.Many2one('res.partner', string='Customer')


class ExpenseCode(models.Model):
    _name = 'expense.code'

    product_id = fields.Many2one('product.product', string='Expense Code')
    price = fields.Float(string='Price')
    partner_id = fields.Many2one('res.partner', string='Vendor')
