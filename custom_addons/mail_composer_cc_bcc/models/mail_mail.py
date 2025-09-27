# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models, tools

from odoo.addons.base.models.ir_mail_server import MailDeliveryException


import psycopg2

import smtplib
import ast
import base64
import datetime
import logging
import psycopg2
import smtplib
import threading
import re
import logging
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval


from odoo import _
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses

import logging
_logger = logging.getLogger(__name__)




def format_emails(partners):
    emails = [tools.formataddr((p.name or "", p.email)) for p in partners if p.email]
    return ", ".join(emails)


def format_emails_raw(partners):
    emails = [p.email for p in partners if p.email]
    return ", ".join(emails)


class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char("Bcc", help="Blind Cc message recipients")

    def _prepare_outgoing_list(self, recipients_follower_status=None):
        # First, return if we're not coming from the Mail Composer
        res = super()._prepare_outgoing_list(
            recipients_follower_status=recipients_follower_status
        )
        # is_out_of_scope = len(self.ids) > 1
        # is_from_composer = self.env.context.get("is_from_composer", False)
        #
        # if is_out_of_scope or not is_from_composer:
        #     return res

        # Prepare values for To, Cc headers
        partners_cc_bcc = self.recipient_cc_ids + self.recipient_bcc_ids
        partner_to_ids = [r.id for r in self.recipient_ids if r not in partners_cc_bcc]
        partner_to = self.env["res.partner"].browse(partner_to_ids)
        email_to = format_emails(partner_to)
        email_to_raw = format_emails_raw(partner_to)
        email_cc = format_emails(self.recipient_cc_ids)
        email_bcc = [r.email for r in self.recipient_bcc_ids if r.email]
        emails_bcc = format_emails(self.recipient_bcc_ids)  # Ensure BCC is formatted properly

        # Collect recipients (RCPT TO) and update all emails
        # with the same To, Cc headers (to be shown by email client as users expect)
        recipients = []
        for m in res:
            rcpt_to = None
            if m["email_to"]:
                rcpt_to = extract_rfc2822_addresses(m["email_to"][0])[0]

                # If the recipient is a Bcc, we had an explicit header X-Odoo-Bcc
                # - It won't be shown by the email client, but can be useful for a recipient # noqa: E501
                #   to understand why he received a given email
                # - Also note that in python3, the smtp.send_message method does not
                #   transmit the Bcc field of a Message object
                if rcpt_to in email_bcc:
                    m["headers"].update({"X-Odoo-Bcc": m["email_to"][0]})

                if not m.get('headers', {}).get("X-Odoo-Bcc", False) and self.recipient_bcc_ids:
                    m["headers"].update({"X-Odoo-Bcc": format_emails(self.recipient_bcc_ids)})
            # in the absence of self.email_to, Odoo creates one special mail for CC
            # see https://github.com/odoo/odoo/commit/46bad8f0
            elif m["email_cc"]:
                rcpt_to = extract_rfc2822_addresses(m["email_cc"][0])[0]

            if rcpt_to:
                recipients.append(rcpt_to)
            if email_to:
                 m["email_to"] = email_to
            m.update(
                {
                    "email_to_raw": email_to_raw,
                    "email_cc": email_cc,
                    "email_bcc": emails_bcc
                }
            )
#            print(f"M  --- {m}")

        self.env.context = {**self.env.context, "recipients": recipients}
        return res

    @api.model
    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None, alias_domain_id=False):
        # Call the super method
        result = super(MailMail, self)._send(auto_commit, raise_exception, smtp_session, alias_domain_id)

        # Custom logic to handle BCC
        for mail in self.exists():
            # Ensure we have recipients in BCC
            if mail.mail_message_id and mail.mail_message_id.recipient_bcc_ids:
                # Extract email addresses from recipient_bcc_ids
                email_bcc_list = mail.mail_message_id.recipient_bcc_ids.mapped('email')

                # Convert list to a comma-separated string
                mail.email_bcc = ', '.join(email_bcc_list) if email_bcc_list else ''
                self._send_bcc(mail)

        return result

    
    def _send_bcc(self, mail):
        """Custom method to handle sending BCC recipients separately."""
        IrMailServer = self.env['ir.mail_server']

        emails_from = mail.email_from
        email_bcc = mail.email_bcc

        # Ensure email_bcc is a list
        if isinstance(email_bcc, str):
            email_bcc = [email.strip() for email in email_bcc.split(',') if email.strip()]

        # ✅ Check if there is at least one recipient
        if not email_bcc:
            mail.write({'state': 'exception', 'failure_reason': "No valid BCC recipient found."})
            return

        # Fix Attachments Handling
        body_list = []
        for mail in self:
            body_list.append(mail._prepare_outgoing_body())
        body = "\n".join(body_list)

        attachments = self.mapped('attachment_ids')
        if attachments:
            if body:
                link_ids = {int(link) for link in re.findall(r'/web/(?:content|image)/([0-9]+)', body)}
                if link_ids:
                    attachments = attachments - self.env['ir.attachment'].browse(list(link_ids))
            email_attachments = [
                (a['name'], base64.b64decode(a['datas']), a['mimetype'])
                for a in attachments.sudo().read(['name', 'datas', 'mimetype']) if a['datas'] is not False
            ]
        else:
            email_attachments = []

        # Email Data
        email_data = {
            'email_to': [],  # Empty To field (since it's BCC only)
            'subject': mail.subject,
            'body': mail.body_html or "",
            'body_alternative': mail.body_html or "",
            'email_cc': [],
            'email_bcc': email_bcc,  # Only BCC
            'reply_to': mail.reply_to or emails_from,
            'attachments': email_attachments,
            'message_id': mail.message_id,
            'references': mail.references,
            'object_id': mail.res_id,
            'headers': {'Return-Path': emails_from},
        }

        # Build Email
        msg = IrMailServer.build_email(
            email_from=emails_from,
            email_to=email_data['email_to'],
            subject=email_data['subject'],
            body=email_data['body'],
            body_alternative=email_data['body_alternative'],
            email_cc=email_data['email_cc'],
            email_bcc=email_data['email_bcc'],  # ✅ Ensuring at least one recipient
            reply_to=email_data['reply_to'],
            attachments=email_data['attachments'],
            message_id=email_data['message_id'],
            references=email_data['references'],
            object_id=email_data['object_id'],
            subtype='html',
            subtype_alternative='plain',
            headers=email_data['headers'],
        )

        try:
            IrMailServer.send_email(msg, mail_server_id=mail.mail_server_id.id)
        except Exception as e:
            mail.write({'state': 'exception', 'failure_reason': str(e)})
