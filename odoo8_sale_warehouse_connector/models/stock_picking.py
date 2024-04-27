from odoo import models, fields, api, _
from datetime import datetime
import xmlrpc.client


class Picking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super(Picking, self).button_validate()
        for data in self:
            move_ids = []
            if data.picking_type_id.code == 'incoming' and data.location_id.usage =='supplier' and data.company_id.id ==3:
                connection = self.env['odoo8.connection'].search([],limit=1)
                if connection:
                    sd_uid, url, db, password = connection.get_connection_data()
                    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
                    warehouse_id = models.execute_kw(db, sd_uid, password,
                                                     'stock.warehouse', 'search',
                                                     [[['code', '=', 'MWH']]],
                                                     {'limit': 1})
                    loc_id = models.execute_kw(db, sd_uid, password,
                                                    'stock.location', 'search',
                                                    [[['name', 'like', 'Inventory loss']]],
                                                    {'limit': 1})
                    dest_id = models.execute_kw(db, sd_uid, password,
                                               'stock.location', 'search',
                                               [[['name', '=', 'MWH-Stock']]],
                                               {'limit': 1})
                    if warehouse_id:
                        picking_type_id = models.execute_kw(db, sd_uid, password,
                                                            'stock.picking.type', 'search',
                                                            [[['warehouse_id', '=', warehouse_id[0]],
                                                              ['name', 'like', 'Transfers']]],
                                                            {'limit': 1})


                        res = {
                            'origin': data.origin,
                            'move_type': 'direct',
                            'invoice_state': 'none',
                            'picking_type_id': picking_type_id[0],
                            'priority': '1'}
                        picking_id = models.execute_kw(db, sd_uid, password, 'stock.picking', 'create', [res])
                        for line in self.move_line_ids:
                            product_id = models.execute_kw(db, sd_uid, password,
                                                        'product.product', 'search',
                                                        [[['default_code', '=', line.product_id.default_code]]],
                                                        {'limit': 1})
                            if product_id:
                                move_val = {
                                    'name': 'Import',
                                    'product_id': product_id[0],
                                    'product_uom_qty': line.qty_done,
                                    'product_uos_qty': line.qty_done,
                                    'product_uom': 1,
                                    'selection': 'none',
                                    'priority': '1',
                                    #'company_id': inv.company_id.id,
                                    'date_expected': data.date_done,
                                    'date': data.date_done,
                                    'origin': data.name + '-' + data.origin,
                                    'location_id': loc_id[0],
                                    'location_dest_id': dest_id[0],
                                    'create_date': data.date_done,
                                    'picking_type_id': picking_type_id[0],
                                    'picking_id': picking_id,
                                    'state': 'done'}
                                move_id = models.execute_kw(db, sd_uid, password, 'stock.move', 'create', [move_val])
                                move_ids.append(move_id)
                            #else:

                        for move in move_ids:
                            models.execute_kw(db, sd_uid, password, 'stock.move', 'action_done', [move])
        return res
