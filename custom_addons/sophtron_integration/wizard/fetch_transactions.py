from odoo import models, fields
import logging
import requests
from datetime import datetime, timezone

_logger = logging.getLogger(__name__)


class SophtronAPITransactions(models.TransientModel):
    _name = 'sophtron.api.transactions'

    sophtron_id = fields.Many2one('sophtron.api.client')
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    journal_id = fields.Many2one('account.journal')

    def button_fetch_transactions(self):
        context = self.env.context
        model = context.get('active_model')
        m_id = context.get('active_id')
        model_id = self.env[model].browse(m_id)

        if model == 'account.journal':
            self.journal_id.sophtron_member_id.fetch_transactions(self.start_date, self.end_date)
        else:
            model_id.fetch_transactions(self.start_date, self.end_date)
            model_id.end_date = self.end_date
