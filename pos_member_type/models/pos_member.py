from odoo import models, fields

class PosMemberType(models.Model):
    _name = 'pos.member.type'
    _description = 'POS Member Type'

    name = fields.Char('Name', required=True)
    loyalty_points = fields.Float('Loyalty Points Multiplier', required=True, default=1.0)
