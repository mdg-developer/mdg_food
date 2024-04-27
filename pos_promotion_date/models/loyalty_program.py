from odoo import _, api, fields, models

class LoyaltyProgramExt(models.Model):
    _inherit = 'loyalty.program'

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')