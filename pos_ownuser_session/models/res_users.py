from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    config_ids = fields.Many2many('pos.config',string='Point of Sale')
