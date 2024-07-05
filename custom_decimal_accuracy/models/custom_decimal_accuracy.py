from odoo import tools
from odoo import _, api, fields, models

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price of Purchase')

