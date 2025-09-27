# # -*- coding: utf-8 -*-
# from odoo import fields, models


# class ResUsers(models.Model):
#     _inherit = "res.users"

#     chatter_position = fields.Selection([
#         ("auto", "Responsive"),
#         ("bottom", "Bottom"),
#         ("hidden", "Hidden"),
#         ("sided", "Side"), ], default="auto")

#     def update_chatter_position(self):
#         if self.chatter_position == 'sided':
#             self.chatter_position = 'hidden'
#         else:
#             self.chatter_position = 'sided'

#     @property
#     def SELF_READABLE_FIELDS(self):
#         return super().SELF_READABLE_FIELDS + ["chatter_position"]

#     @property
#     def SELF_WRITEABLE_FIELDS(self):
#         return super().SELF_WRITEABLE_FIELDS + ["chatter_position"]
