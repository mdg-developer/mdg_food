from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from uuid import uuid4

class LoyaltyProgramExt(models.Model):
    _inherit = 'loyalty.program'

    pos_member_type_id = fields.Many2one('pos.member.type', string='Member Type')