from odoo import tools
from odoo import _, api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order'

    def _default_company_name(self):
        return self.env.company.name        

    company_name = fields.Char(string='Company Name', default=_default_company_name)
    customer_nrc = fields.Char(string="Customer NRC")
    customer_phone = fields.Char(string="Customer Phone")
    driver_id = fields.Many2one(comodel_name="res.driver",string='Driver Name', required=True)
    driver_nrc = fields.Char(string='Driver NRC', required=True)
    mobile_one = fields.Char(string='Mobile 1')
    mobile_two = fields.Char(string='Mobile 2')
    issue_date = fields.Date(string='Issue Date', required=True)
    truck_no = fields.Char(string='Truck No')
    oil_address = fields.Text(string="Oil Delivery Address")
    remark = fields.Text(string="Remark")

    @api.onchange('driver_id')
    def onchange_driver_id(self):
        if self.driver_id:
            self.driver_nrc = self.driver_id.nrc_no
            self.mobile_one = self.driver_id.phone_one
            self.mobile_two = self.driver_id.phone_two

    @api.onchange('partner_id')
    def _onchange_partner_id_warning(self):
        super()._onchange_partner_id_warning()
        self.customer_nrc = self.partner_id.x_studio_nrc
        self.customer_phone = self.partner_id.phone or self.partner_id.mobile

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._onchange_partner_id_warning()
        res.onchange_driver_id()
        return res

    def action_confirm(self):
        res = super().action_confirm()
        picking_ids = self.picking_ids
        picking_data = {'issue_date': self.issue_date,
                        'driver_id': self.driver_id.id,
                        'driver_nrc': self.driver_nrc,
                        'mobile_one': self.mobile_one,
                        'mobile_two': self.mobile_two,
                        'truck_no': self.truck_no,
                        'oil_address': self.oil_address
                                }
        picking_ids.write(picking_data)
        return True

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

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res['drum_qty'] = self.drum_qty
        return res

