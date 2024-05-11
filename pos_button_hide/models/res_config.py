from odoo import fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    hide_info_button = fields.Boolean("Hide Info Button")
    hide_info_product = fields.Boolean("Hide Info Product")


