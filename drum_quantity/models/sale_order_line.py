from odoo import tools
from odoo import _, api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order'

    def _default_company_name(self):
        return self.env.company.name        

    company_name = fields.Char(string='Company Name', default=_default_company_name)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    drum_qty = fields.Float(string='Drum Qty')

    @api.onchange('drum_qty')
    def onchange_drum_qty(self):
        if self.env.company.name =='ECOHARMONY COMPANY LIMITED':
            param_id = self.env['ir.config_parameter'].search([('key','=','drum_ratio')])
            if param_id and param_id.value:
                self.product_uom_qty = self.drum_qty * int(param_id.value)
            else:
                self.product_uom_qty = 0
        else:
            self.product_uom_qty = 0

    # def _prepare_invoice_line(self, **optional_values):
    #     res = super(SaleOrderLine, self)._prepare_invoice_line()
    #     res['drum_qty'] = self.drum_qty
    #     return res

