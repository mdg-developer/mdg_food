from odoo import models, fields, api, _
from datetime import datetime
import xmlrpc.client


class ProductTemplate(models.Model):
    _inherit = "product.template"
    odoo8_product_tmp_id = fields.Integer(default=0,
                              help='The priority of the job, as an integer: 0 means higher priority, 10 means lower priority.')
    sync_flg = fields.Boolean("Sync Check",default=False)

    def sync_odoo8_dms(self):
        connection = self.env['odoo8.connection'].search([], limit=1)
        if connection:
            sd_uid, url, db, password = connection.get_connection_data()
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            for product in self:
                pp_id = self.env['product.product'].search([('product_tmpl_id','=',product.id)])
                value = {
                    'default_code':product.default_code,
                    'name':product.name,
                    'short_name':product.name,
                    'sale_ok':product.sale_ok,
                    'purchase_ok':product.purchase_ok,
                    'list_price':product.list_price,
                    'type':product.detailed_type,
                    'uom_id':1,
                    'report_uom_id':1,
                    'odoo15_tmpl_id':product.id,
                    'odoo15_pp_id':pp_id.id or False,
                    'standard_price':product.standard_price,
                    #'categ_id':
                }
                product_id = models.execute_kw(db, sd_uid, password, 'product.template', 'create', [value])
                product.write({'sync_flg':True})
                #move_ids.append(move_id)