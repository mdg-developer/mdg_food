from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    pos_member_type_id = fields.Many2one('pos.member.type', string='Member Type')
