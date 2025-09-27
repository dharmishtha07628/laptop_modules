# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _track_get_fields(self):
        model_fields = set()
        exclude_fields = {
            'write_date', '__last_update', 'write_uid', 'create_uid', 'create_date', 'id',
            'display_name', 'activity_ids', 'activity_state', 'message_attachment_count',
            'message_ids', 'message_follower_ids', 'message_is_follower', 'message_partner_ids',
            'message_needaction', 'message_needaction_counter', 'message_has_error',
            'message_has_error_counter', 'has_message'
        }
        for name, field in self._fields.items():
            if name in exclude_fields:
                continue
            # Only track stored fields
            if getattr(field, 'store', False) is False:
                continue
            # Track relational fields too
            if field.type in ['many2one', 'many2many']:
                model_fields.add(name)
            # Simple fields
            elif field.type in ['char', 'text', 'selection', 'boolean', 'float', 'integer', 'date', 'datetime']:
                model_fields.add(name)
        return model_fields and set(self.fields_get(model_fields, attributes=()))
