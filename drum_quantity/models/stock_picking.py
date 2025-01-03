from odoo import tools
from odoo import _, api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _default_company_name(self):
        return self.env.company.name        

    company_name = fields.Char(string='Company Name', default=_default_company_name)
    driver_id = fields.Many2one(comodel_name="res.driver",string='Driver Name', required=False)
    driver_nrc = fields.Char(string='Driver NRC', required=False)
    mobile_one = fields.Char(string='Mobile 1')
    mobile_two = fields.Char(string='Mobile 2')
    issue_date = fields.Date(string='Issue Date', required=False)
    expire_date = fields.Date(string='Expire Date')
    truck_no = fields.Char(string='Truck No')
    oil_address = fields.Text(string="Oil Delivery Address")

    @api.onchange('driver_id')
    def onchange_driver_id(self):
        if self.driver_id:
            self.driver_nrc = self.driver_id.nrc_no
            self.mobile_one = self.driver_id.phone_one
            self.mobile_two = self.driver_id.phone_two

    def do_print_action(self):
        if self.company_name=='ECOHARMONY COMPANY LIMITED':
            return self.env.ref('drum_quantity.delivery_order_print').report_action(self)
        if self.company_name=='Zabukyaw Global Co.,Ltd.':
            return self.env.ref('drum_quantity.zbk_delivery_order_print').report_action(self)

