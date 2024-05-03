from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    birthday = fields.Date(string='Birthday')
    barcode = fields.Char(string='Member ID')