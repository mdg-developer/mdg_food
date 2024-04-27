from collections import defaultdict
from datetime import timedelta
from itertools import groupby

from odoo import api, fields, models, _, Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare
from odoo.osv.expression import AND, OR
from odoo.service.common import exp_version
import xmlrpc.client
import logging
_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def action_pos_session_closing_control(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        orders = self.order_ids.filtered(lambda o: o.state == 'paid' or o.state == 'invoiced')
        res = super(PosSession, self).action_pos_session_closing_control(balancing_account=balancing_account,amount_to_balance=amount_to_balance,bank_payment_method_diffs=bank_payment_method_diffs)
        for session in self:

            connection = self.env['odoo8.connection'].search([], limit=1)
            if connection:
                sd_uid, url, db, password = connection.get_connection_data()
                models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

                if orders:
                    order_lines = self.env['pos.order.line'].search([('order_id','in',orders.ids)])
                    product_qty_dict = {}
                    for order_line in order_lines:
                        key = (order_line.product_id.id, order_line.product_id.default_code,order_line.price_unit)
                        if key not in product_qty_dict:
                            product_qty_dict[key] = order_line.qty
                        else:
                            product_qty_dict[key] += order_line.qty

                    so_vals = {}
                    so_vals['order_line'] = []
                    so_vals['user_id'] = sd_uid
                    so_vals['section_id']=1312
                    so_vals['delivery_id']=1312
                    so_vals['pricelist_id'] = 1
                    so_vals['origin'] = session.name
                    partner_id = models.execute_kw(db, sd_uid, password,
                                                   'res.partner', 'search',
                                                   [[['name', '=', 'Cellar 18']]],
                                                   {'limit': 1})
                    if partner_id:
                        so_vals['partner_id'] = partner_id[0]
                    else:
                        partner_id = models.execute_kw(db, sd_uid, password,
                                                       'res.partner', 'search',
                                                       [[]],
                                                       {'limit': 1})
                        so_vals['partner_id'] = partner_id[0]

                    warehouse_id = models.execute_kw(db, sd_uid, password,
                                                   'stock.warehouse', 'search',
                                                   [[['name', '=', 'Cellar 18']]],
                                                   {'limit': 1})
                    if warehouse_id:
                        _logger.info("*************Warehouse>>>>>>>>>>>>>************:%r",warehouse_id)
                        so_vals['warehouse_id'] = warehouse_id[0]
                    else:

                        warehouse_id = models.execute_kw(db, sd_uid, password,
                                                       'stock.warehouse', 'search',
                                                       [[]],
                                                       {'limit': 1})
                        so_vals['warehouse_id'] = warehouse_id[0]

                    for (product_id, default_code,price_unit), qty in product_qty_dict.items():

                        product = self.env['product.product'].browse([product_id])
                        if product:
                            product_id = models.execute_kw(db, sd_uid, password,
                                                             'product.product', 'search',
                                                             [[['default_code', '=', product.default_code]]],
                                                             {'limit': 1})
                            uom_id = models.execute_kw(db, sd_uid, password,
                                                           'product.uom', 'search',
                                                           [[['name', '=', product.uom_id.name]]],
                                                           {'limit': 1})
                            if not uom_id:
                                uom_id = [1]
                            if product_id and uom_id:
                                so_vals['order_line'].append(
                                    [0, False, {'product_uom': uom_id[0], 'product_id': product_id[0],'name':product.name,
                                                'product_uom_qty':qty,'price_unit':price_unit}])


                    sale_order_id = models.execute_kw(db, sd_uid, password, 'sale.order', 'create', [so_vals])
        return res