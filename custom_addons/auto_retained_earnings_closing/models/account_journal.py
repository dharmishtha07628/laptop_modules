from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_closing_journal = fields.Boolean()