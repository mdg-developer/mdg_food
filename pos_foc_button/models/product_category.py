
from odoo import api, fields, models, _, Command


class ProductCategory(models.Model):
    _inherit = "product.category"

    property_account_foc_categ = fields.Many2one(
        'account.account', string="Product FOC Account",
        company_dependent=True,
        help="This account will be used to value price difference between purchase price and accounting cost.")