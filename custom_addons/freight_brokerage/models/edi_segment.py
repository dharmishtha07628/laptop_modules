# -*- coding: utf-8 -*-
# Part of Octagotech. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ReferenceIdentificationQualifierEdiSegment(models.Model):
    _name = "reference.identification.qualifier.edi.segment"
    _description = "Master Table For Edi Segments (reference_identification_qualifier field) Code and Labels"
    _rec_name = 'edi_id'

    edi_id = fields.Char(string='EDI Id')
    label = fields.Char(string='EDI Label')


class StopTypeEdiSegment(models.Model):
    _name = "stop.type.edi.segment"
    _description = "Master Table For Edi Segments (stop_type field) Code and Labels"
    _rec_name = 'edi_id'

    edi_id = fields.Char(string='EDI Id')
    label = fields.Char(string='EDI Label')


class WeightUOMEdiSegment(models.Model):
    _name = "weight.uom.edi.segment"
    _description = "Master Table For Edi Segments (weight_uom field) Code and Labels"
    _rec_name = 'edi_id'

    edi_id = fields.Char(string='EDI Id')
    label = fields.Char(string='EDI Label')


class NoOfUnitDescriptionEdiSegment(models.Model):
    _name = "no.of.unit.description.edi.segment"
    _description = "Master Table For Edi Segments (no_of_units_description field) Code and Labels"
    _rec_name = 'edi_id'

    edi_id = fields.Char(string='EDI Id')
    label = fields.Char(string='EDI Label')


class VolumeUOMEdiSegment(models.Model):
    _name = "volume.uom.edi.segment"
    _description = "Master Table For Edi Segments (volume_uom field) Code and Labels"
    _rec_name = 'edi_id'

    edi_id = fields.Char(string='EDI Id')
    label = fields.Char(string='EDI Label')


class LocationCodeEdiSegment(models.Model):
    _name = "location.code.edi.segment"
    _description = "Master Table For Edi Segments (location_code field) Code and Labels"
    _rec_name = 'edi_id'

    edi_id = fields.Char(string='EDI Id')
    label = fields.Char(string='EDI Label')


class LocationContactTypeEdiSegment(models.Model):
    _name = "location.contact.type.edi.segment"
    _description = "Master Table For Edi Segments (location_code field) Code and Labels"
    _rec_name = 'edi_id'

    edi_id = fields.Char(string='EDI Id')
    label = fields.Char(string='EDI Label')


class UnitDescriptionEdiSegment(models.Model):
    _name = "unit.description.edi.segment"
    _description = "Master Table For Edi Segments (units_description field) Code and Labels"
    _rec_name = 'edi_id'

    edi_id = fields.Char(string='EDI Id')
    label = fields.Char(string='EDI Label')


class WeightRateChargesEdiSegment(models.Model):
    _name = "weight.rate.charges.edi.segment"
    _description = "Master Table For Edi Segments (wright_rate_charges field) Code and Labels"
    _rec_name = 'edi_id'

    edi_id = fields.Char(string='EDI Id')
    label = fields.Char(string='EDI Label')


class SchedulingEdiSegment(models.Model):
    _name = "scheduling.edi.segment"
    _description = "Master Table For Edi Segments (scheduling field) Code and Labels"
    _rec_name = 'edi_id'

    edi_id = fields.Char(string='EDI Id')
    label = fields.Char(string='EDI Label')
