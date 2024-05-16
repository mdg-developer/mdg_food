from odoo import api, fields, models, tools, SUPERUSER_ID, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.website_id:
            self.write({"date_order": fields.Datetime.now()})
        return res
