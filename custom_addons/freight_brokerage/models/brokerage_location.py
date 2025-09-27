# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class BrokerageLocation(models.Model):
    _name = "brokerage.location"
    _description = "Brokerage Location"

    location_code = fields.Char(string='Location Short Code')
    name = fields.Char(string='Location Name', required=True)
    address = fields.Char(string='Address')
    city = fields.Char(string='City')
    state = fields.Char(string='State')
    zip_code = fields.Char(string='ZIP Code')
    phone = fields.Char(string='Phone')
    website = fields.Char(string='Website')
    latitude = fields.Float('Geo Latitude', digits=(10, 7))
    longitude = fields.Float('Geo Longitude', digits=(10, 7))
    scheduling_id = fields.Many2one('scheduling.edi.segment', string='Scheduling')
    location_rating = fields.Float(string='Location Rating')

    # Location Opening Hours
    mon = fields.Boolean(string='Monday', default=True)
    tue = fields.Boolean(string='Tuesday', default=True)
    wed = fields.Boolean(string='Wednesday', default=True)
    thu = fields.Boolean(string='Thursday', default=True)
    fri = fields.Boolean(string='Friday', default=True)
    sat = fields.Boolean(string='Saturday', default=True)
    sun = fields.Boolean(string='Sunday', default=True)

    opening_hours_mon = fields.Float(string='Opening Hours for Monday')
    opening_hours_tue = fields.Float(string='Opening Hours for Tuesday')
    opening_hours_wed = fields.Float(string='Opening Hours for Wednesday')
    opening_hours_thu = fields.Float(string='Opening Hours for Thursday')
    opening_hours_fri = fields.Float(string='Opening Hours for Friday')
    opening_hours_sat = fields.Float(string='Opening Hours for Saturday')
    opening_hours_sun = fields.Float(string='Opening Hours for Sunday')

    closing_hours_mon = fields.Float(string='Closing Hours for Monday')
    closing_hours_tue = fields.Float(string='Closing Hours for Tuesday')
    closing_hours_wed = fields.Float(string='Closing Hours for Wednesday')
    closing_hours_thu = fields.Float(string='Closing Hours for Thursday')
    closing_hours_fri = fields.Float(string='Closing Hours for Friday')
    closing_hours_sat = fields.Float(string='Closing Hours for Saturday')
    closing_hours_sun = fields.Float(string='Closing Hours for Sunday')

    # Relational Fields
    location_comment_ids = fields.One2many('brokerage.comment', 'brokerage_location_id', string='Comments')
    brokerage_location_contacts_ids = fields.One2many('brokerage.location.contact', 'location_id', string='Brokerage Location Contacts')

    # mon = fields.Boolean(string='Monday', default=True)
    # tue = fields.Boolean(string='Tuesday', default=True)
    # wed = fields.Boolean(string='Wednesday', default=True)
    # thu = fields.Boolean(string='Thursday', default=True)
    # fri = fields.Boolean(string='Friday', default=True)
    # sat = fields.Boolean(string='Saturday', default=True)
    # sun = fields.Boolean(string='Sunday', default=True)

    # scheduling = fields.Selection([
    #     ('appointment', 'Appointment Required'),
    #     ('eta', 'ETA Required'),
    #     ('fcfs', 'FCFS'),
    #     ('other', 'Other')
    # ], string='Scheduling', default='appointment')

    # location_type_id = fields.Many2one('brokerage.location.type', string='Location Type')
    # rate_confirmation_comment = fields.Char(string='Rate Confirmation Comments')

    # @api.constrains('phone')
    # def _validate_phone_format(self):
    #     for record in self:
    #         if record.phone and not re.match(r'^\(\d{3}\) \d{3}-\d{4}$', record.phone):
    #             raise ValidationError("Phone number must be in the format (###) ###-####")

# # -*- coding: utf-8 -*-
# # Part of Octagotech. See LICENSE file for full copyright and licensing details.

# from odoo import fields, models


# class BrokerageLocation(models.Model):
#     _name = "brokerage.location"

#     name = fields.Char(string='Location Name', required=True)
#     location_code = fields.Char(string='Location Code')
#     address = fields.Char(string='Address')
#     phone = fields.Char(string='Phone')
#     rate_confirmation_comment = fields.Char(string='Rate Confirmation Comment')
#     latitude = fields.Float('Geo Latitude', digits=(10, 7))
#     longitude = fields.Float('Geo Longitude', digits=(10, 7))
#     website = fields.Char(string='Website')
#     contacts = fields.Char(string='Contacts')
#     is_appointment_required = fields.Boolean(string='Is Appointment Required')
#     location_type_id = fields.Many2one('brokerage.location.type', string='Location Type')

#     location_opening_hours = fields.Char(string='Location Opening Hours')
#     mon = fields.Boolean(default=True)
#     tue = fields.Boolean(default=True)
#     wed = fields.Boolean(default=True)
#     thu = fields.Boolean(default=True)
#     fri = fields.Boolean(default=True)
#     sat = fields.Boolean(default=True)
#     sun = fields.Boolean(default=True)
#     # <widget name="week_days"/>

#     # TODO Points :
#     # table for location opening hours
#     # may be we can use widget for that for display weekdays
#     # location history (previously used location history) may be smart button
