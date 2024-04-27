from odoo import api, fields, models, _
from datetime import datetime, date, timedelta

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    warehouse_id = fields.Many2one(related='location_id.location_id', string='Warehouse', comppute='compute_warehouse', store=True, readonly=True)
    # expiry_date = fields.Datetime(string='Expiry Date', related='lot_id.life_date', readonly=False)
    expiry_date = fields.Datetime(string='Expiry Date')

    @api.onchange('lot_id')
    def onchange_lot(self):
        if self.lot_id:
            self.expiry_date = self.lot_id.life_date

    def compute_warehouse(self):
        location = self.env['stock.warehouse'].search([('view_location_id', '=', self.location_id.location_id)])
        for l in location:
            self.warehouse_id = l.id
    
    @api.model
    def _get_inventory_fields_create(self):
        """ Returns a list of fields user can edit when he want to create a quant in `inventory_mode`.
        """
        return ['product_id', 'location_id', 'lot_id', 'package_id', 'owner_id', 'inventory_quantity', 'warehouse_id', 'expiry_date']



