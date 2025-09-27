# Configuration fields for plaid.
import math
from datetime import datetime, time, timedelta
import pytz
from odoo import models, fields,api


class ResConfigInherit(models.TransientModel):
    _inherit = "res.config.settings"

    # plaid_client_id = fields.Char(string="Client Id",
    #                 config_parameter="sttl_plaid_integration.plaid_client_id")
    # plaid_api_secret = fields.Char(string="Secret",
    #                                config_parameter="sttl_plaid_integration.plaid_api_secret")
    # plaid_environment = fields.Selection([('sandbox', 'Sandbox'), ('development', 'Development'), ('production', 'Production')],
    #                                      config_parameter="sttl_plaid_integration.plaid_environment")

    @staticmethod
    def _hours(_self=None):
        return [(str(h).zfill(2), str(h).zfill(2)) for h in range(24)]

    @staticmethod
    def _minutes_seconds(_self=None):
        return [(str(m).zfill(2), str(m).zfill(2)) for m in range(60)]

    plaid_auto_connect = fields.Boolean("Plaid Auto Fetch Transaction")
    plaid_email = fields.Char("Notification Email")
    # plaid_time = fields.Char(string="Plaid Time")
    plaid_time = fields.Float(string="Plaid Time", help="Time in hours (e.g., 1.5 for 1 hour 30 minutes)", default=0.0)
    """ # fields in case of selection
    plaid_hour = fields.Selection(selection=_hours, string="Hour", default="00")
    plaid_minute = fields.Selection(selection=_minutes_seconds, string="Minute", default="00")
    plaid_second = fields.Selection(selection=_minutes_seconds, string="Second", default="00") """
            
    def set_values(self):
        super().set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param("sttl_plaid_integration.plaid_auto_connect", self.plaid_auto_connect)
        ICP.set_param("sttl_plaid_integration.plaid_email", self.plaid_email or "")
        """ # fields in case of selection
        ICP.set_param("sttl_plaid_integration.plaid_hour", self.plaid_hour or "00")
        ICP.set_param("sttl_plaid_integration.plaid_minute", self.plaid_minute or "00")
        ICP.set_param("sttl_plaid_integration.plaid_second", self.plaid_second or "00") """
        ICP.set_param("sttl_plaid_integration.plaid_time", self.plaid_time or 0.0)
        # plaid_time = f"{self.plaid_hour}:{self.plaid_minute}:{self.plaid_second}"
        cron = self.env.ref("sttl_plaid_integration.ir_cron_fetch_transaction_auto", raise_if_not_found=False)
        if cron and self.plaid_time:
            # Parse "HH:MM:SS"
            h, m = map(int, str(self.plaid_time).split("."))
            target_time = time(hour=h, minute=m, second=0)

            # Use server local time
            now = datetime.now()
            nextcall = datetime.combine(now.date(), target_time)
            nextcall_utc = nextcall - timedelta(hours=5, minutes=30)

            if nextcall_utc  <= datetime.utcnow():
                nextcall_utc += timedelta(days=1)

            # Direct SQL update
            self.env.cr.execute("""
                      UPDATE ir_cron
                      SET nextcall = %s,
                          interval_number = 1,
                          interval_type = 'days'
                      WHERE id = %s
                  """, (nextcall_utc, cron.id))
    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        res.update(
            plaid_auto_connect=ICP.get_param('sttl_plaid_integration.plaid_auto_connect', default=False),
            plaid_email=ICP.get_param('sttl_plaid_integration.plaid_email', default=""),
            # plaid_hour=ICP.get_param('sttl_plaid_integration.plaid_hour', default='00'),
            # plaid_minute=ICP.get_param('sttl_plaid_integration.plaid_minute', default='00'),
            # plaid_second=ICP.get_param('sttl_plaid_integration.plaid_second', default='00'),
            plaid_time=(ICP.get_param('sttl_plaid_integration.plaid_time', default=0.0))
        )
        return res
