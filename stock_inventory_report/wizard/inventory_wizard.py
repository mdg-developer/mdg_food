# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

import time
from odoo import models, api, fields, _
from odoo.exceptions import Warning
from dateutil import parser
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

import io
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')

try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class inventory_reports(models.TransientModel):
    _name = 'stock.inventory.reports'

    company_id = fields.Many2one('res.company', string='Company')
    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouse')
    location_id = fields.Many2one('stock.location', string='Location', context={'active_test': False})
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')

    product_category_id = fields.Many2one('product.category', string='Categories')
    product_id = fields.Many2one('product.product', string='Product')
    start_date = fields.Date('Beginning Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date('End Date', required=True, default=fields.Date.context_today)

    sort_order = fields.Selection([('warehouse', 'Warehouse'), ('product_category', 'Product Category')], 'Group By', required=True, default='warehouse')
    include_zero = fields.Boolean('Include Zero Movement?', help="True, if you want to see zero movements of products.\nNote: It will consider only movements done in-between dates.")
    filter_product_ids = fields.Many2many('product.product', string='Products')
    filter_product_categ_ids = fields.Many2many('product.category', string='Categories')
    display_all_products = fields.Boolean('Display Products?', help="True, if you want to display only warehouse/categories total.", default=True)
    show_purchase_uom = fields.Boolean('Show Purchase UoM', default=False)
    show_zero_amount = fields.Boolean('Show Zero Stock Move', default=False)
    show_transit_location = fields.Boolean('Show Transit Location', default=False)
    begining_qty = fields.Float('Begining Qty')

    @api.onchange('sort_order')
    def onchange_sortorder(self):
        """
        Set blank values
        """
        if self.sort_order == 'warehouse':
            self.filter_product_categ_ids = False
        elif self.sort_order == 'product_category':
            self.filter_product_ids = False
        else:
            self.filter_product_categ_ids = False
            self.filter_product_ids = False

    @api.onchange('company_id')
    def onchange_company_id(self):
        """
        Make warehouse compatible with company
        """
        warehouse_ids = self.env['stock.warehouse'].sudo().search([])
        if self.company_id:
            warehouse_ids = self.env['stock.warehouse'].sudo().search([('company_id', '=', self.company_id.id)])
        return {
                'domain':
                        {
                         'warehouse_ids': [('id', 'in', [x.id for x in warehouse_ids])]
                         },
                'value':
                        {
                        'warehouse_ids': False
                        }
                }
    
    @api.onchange('warehouse_ids', 'show_transit_location')
    def onchange_warehouse(self):
        """
        Make warehouse compatible with company
        """
        location_obj = self.env['stock.location']
        if self.show_transit_location is True:
            location_ids = location_obj.search([('usage', 'in', ('internal', 'transit'))])
            total_warehouses = self.warehouse_ids
            if total_warehouses:
                addtional_ids = []
                for warehouse in total_warehouses:
                    store_location_id = warehouse.view_location_id.id
                    addtional_ids.extend([y.id for y in location_obj.search([('location_id', 'child_of', store_location_id), ('usage', 'in', ('internal', 'transit'))])])
                location_ids = addtional_ids
            else:
                location_ids = [p.id for p in location_ids]
        else:
            location_ids = location_obj.search([('usage', '=', 'internal')])
            total_warehouses = self.warehouse_ids
            if total_warehouses:
                addtional_ids = []
                for warehouse in total_warehouses:
                    store_location_id = warehouse.view_location_id.id
                    addtional_ids.extend([y.id for y in location_obj.search([('location_id', 'child_of', store_location_id), ('usage', '=', 'internal')])])
                location_ids = addtional_ids
            else:
                location_ids = [p.id for p in location_ids]
        return {
                  'domain':
                            {
                             'location_id': [('id', 'in', location_ids)]
                             },
                  'value':
                        {
                        'location_id': False
                        }
                }
        
    @api.onchange('warehouse_id', 'show_transit_location')
    def onchange_warehouse_only(self):
        """
        Make warehouse compatible with company
        """
        location_obj = self.env['stock.location']
        location_ids = {}
        inactive_location_ids = {}
        all_location_ids = {}
        if self.warehouse_id:
            store_location_id = self.warehouse_id.view_location_id.id
            if self.show_transit_location is True:
                location_ids = location_obj.search([('location_id', 'child_of', store_location_id), ('usage', 'in', ('internal', 'transit'))])
            else:
                location_ids = location_obj.search([('location_id', 'child_of', store_location_id), ('usage', '=', 'internal')])
            
            location_ids = [p.id for p in location_ids]
            if self.show_transit_location is True:
                inactive_location_ids = location_obj.search([('location_id', 'child_of', store_location_id), ('usage', 'in', ('internal', 'transit')),('active', '=', False)])
            else:
                inactive_location_ids = location_obj.search([('location_id', 'child_of', store_location_id), ('usage', '=', 'internal'),('active', '=', False)])
            
            inactive_location_ids = [p.id for p in inactive_location_ids]
            all_location_ids = location_ids + inactive_location_ids
            
        return {
                  'domain':
                            {
                             'location_id': [('id', 'in', all_location_ids)]
                             },
                  'value':
                        {
                        'location_id': False
                        }
                }
    
    @api.onchange('product_category_id')
    def onchange_product_category(self):
        domain = {}
        if not self.product_category_id:
            domain['product_id'] = []
        else:
            domain['product_id'] = [('product_tmpl_id.categ_id', '=', self.product_category_id.id)]
        return {'domain': domain}

    def print_report(self):
        """
            Print report either by warehouse or product-category
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        datas = {
                 'form':
                        {
                            'company_id': self.company_id and [self.company_id.id] or [],
                            'warehouse_ids': [y.id for y in self.warehouse_ids],
                            'location_id': self.location_id and self.location_id.id or False,
                            'start_date': self.start_date.strftime(DF),
                            'end_date': self.end_date.strftime(DF),
                            'include_zero': self.include_zero,
                            'sort_order': self.sort_order,
                            'display_all_products': self.display_all_products,
                            'id': self.id,
                            'filter_product_ids': [p.id for p in self.filter_product_ids],
                            'filter_product_categ_ids': [p.id for p in self.filter_product_categ_ids] 
                        }
                }

        if [y.id for y in self.warehouse_ids] and (not self.company_id):
            self.warehouse_ids = []
            raise Warning(_('Please select company of those warehouses to get correct view.\nYou should remove all warehouses first from selection field.'))
        sort_by = self.sort_order or 'warehouse'
        if sort_by == 'product_category':
            return self.env.ref(
                                'stock_inventory_report.action_inventory_report_by_category'
                                ).with_context(landscape=True).report_action(self, data=datas)
        return self.env.ref(
                            'stock_inventory_report.action_inventory_report_by_warehouse'
                            ).with_context(landscape=True).report_action(self, data=datas)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

    def custom_sort(self,quant):
        return quant.product_id.name

    def _find_locations(self, warehouse):
        """
        Find warehouse stock locations and its childs.
            -All stock reports depends on stock location of warehouse.
        """
        warehouse_obj = self.env['stock.warehouse']
        location_obj = self.env['stock.location']
        store_location_id = warehouse_obj.browse(warehouse).view_location_id.id
        return [x.id for x in location_obj.search([('location_id', 'child_of', store_location_id)])]

    def print_product_ledger_report(self):
        """
            Print report either by warehouse or product-category
        """
        filename = 'Stock Ledger Report.xls'
        workbook = xlwt.Workbook()
        stylePC = xlwt.XFStyle()
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        fontP = xlwt.Font()
        fontP.bold = True
        fontP.height = 200
        stylePC.font = fontP
        stylePC.num_format_str = '@'
        stylePC.alignment = alignment
        style_title = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center;pattern: pattern solid, fore_colour aqua;")
        style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
        style = xlwt.easyxf("font:height 200; font: name Liberation Sans,color black;")
        worksheet = workbook.add_sheet('Sheet 1')
        worksheet.write_merge(0, 1, 0, 12, "Stock Ledger Report", style=style_title)
        worksheet.write_merge(2, 3, 0, 0, "From Date",style_table_header)
        worksheet.write_merge(2, 3, 2, 2, "To Date",style_table_header)
        worksheet.write_merge(2, 3, 4, 4, "Product Category", style_table_header)
        worksheet.write_merge(2, 3, 6, 6, "Product",style_table_header)
        worksheet.write_merge(2, 3, 8, 8, "Warehouse",style_table_header)
        worksheet.write_merge(2, 3, 10, 10, "Company",style_table_header)
        
        
        worksheet.write(4, 0, self.start_date.strftime('%d-%m-%Y'))
        worksheet.write(4, 2, self.end_date.strftime('%d-%m-%Y'))
        if self.product_category_id:
            worksheet.write(4, 4, self.product_category_id.name)
        # worksheet.write(4, 6, self.product_id.name)
        worksheet.write(4, 8, self.warehouse_id.name)
        worksheet.write(4, 10, self.company_id.name)

        worksheet.write_merge(2, 3, 1, 1,  style=style_table_header)
        worksheet.write(6, 0, 'Tran:Date', style_table_header)
        worksheet.write(6, 1, 'Transaction Type', style_table_header)
        worksheet.write(6, 2, 'Location ID', style_table_header)
        worksheet.write(6, 3, 'Transaction ID', style_table_header)
        worksheet.write(6, 4, 'Received Qty', style_table_header)
        worksheet.write(6, 5, 'Issue Qty', style_table_header)
        worksheet.write(6, 6, 'Balance Qty', style_table_header)
        worksheet.write(6, 7, 'Volume (Liter)', style_table_header)
        worksheet.write(6, 8, 'UoM', style_table_header)
        if self.show_purchase_uom:
            worksheet.write(6, 9, 'Received Qty', style_table_header)
            worksheet.write(6, 10, 'Issue Qty', style_table_header)
            worksheet.write(6, 11, 'Purchase UoM Balance Qty', style_table_header)
            worksheet.write(6, 12, 'Purchase UoM', style_table_header)
        
        prod_row = 7
        prod_col = 0  
        products = {}  
        count = 1
        if self.product_category_id and not self.product_id:
            products = self.env['product.product'].search([('product_tmpl_id.categ_id', '=', self.product_category_id.id), ('active', '=', True)], order="default_code")
            if products:
                for product in products:
                    prod_row, worksheet = self.print_each_product(product, worksheet, prod_row, prod_col, style, style_table_header)
        
        if self.product_category_id and self.product_id:
            worksheet.write(4, 6, self.product_id.name)
            prod_row, worksheet = self.print_each_product(self.product_id, worksheet, prod_row, prod_col, style, style_table_header)
        
        if self.product_id and not self.product_category_id:
            worksheet.write(4, 6, self.product_id.name)
            prod_row, worksheet = self.print_each_product(self.product_id, worksheet, prod_row, prod_col, style, style_table_header)
        
        # prod_row = 7
        # prod_col = 0  
        # products = {}  
        # count = 1
        # if self.product_id:
        #     worksheet.write(4, 4, self.product_id.name)
        #     prod_row, worksheet = self.print_each_product(self.product_id, worksheet, prod_row, prod_col, style, style_table_header)
        # else:
        #     # if self.location_id:
        #         #quants = self.env['stock.quant'].search([('location_id','=',self.location_id.id),('quantity','>',0)],order='product_id')
        #         #quants = quants.sort(key=self.custom_sort)
        #     products = self.env['product.product'].search([('product_tmpl_id.type','=','product'),('active','=',True)],order="default_code")
        #     if products:
        #         for product_id in products:
        #             print('Product: ' + str(product_id.name))
        #             prod_row, worksheet = self.print_each_product(product_id, worksheet, prod_row, prod_col, style, style_table_header)
            
        fp = io.BytesIO()
        workbook.save(fp)
        export_id = self.env['stock.ledger.report'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        res = {'view_mode': 'form',
               'res_id': export_id.id,
               'name': 'Stock Ledger Report',
               'res_model': 'stock.ledger.report',
               'view_type': 'form',
               'type': 'ir.actions.act_window',
               'target':'new'
                }
        return res
    
    def print_each_product(self, product_id, worksheet, prod_row, prod_col, style, style_table_header):
        sortBy = "date asc"
        if product_id:
            product=self.env['product.product'].browse(product_id.id)
            purchase_uom_id=product.product_tmpl_id.uom_po_id.id
            purchase_uom_name=product.product_tmpl_id.uom_po_id.name

            #stock move for issues
            # order=sortBy
            moves = self.env['stock.move.line'].search([
                                                      ('product_id','=',product.id),
                                                      ('state','=','done'),                                                      
                                                      ('date','>=',self.start_date.strftime('%Y-%m-%d 00:00:00')),
                                                      ('date','<=',self.end_date.strftime('%Y-%m-%d 23:59:59'))])
            print("Stock Move Lines: " + str(len(moves)))
            opening_balance = self._get_beginning_inventory_ProductLedger(self.start_date.strftime('%Y-%m-%d 00:00:00'),
                                                                          self.location_id.id, self.warehouse_id.id,
                                                                          product_id.id)
            closing_bal = self._get_closing_balance(opening_balance,moves)
            check_balance = False
            if self.show_zero_amount:
                check_balance = self.show_zero_amount
            else:
                check_balance = int(closing_bal)>0

#             if len(moves)>=1  and check_balance:
            bigger_qty=1
            worksheet.write(prod_row, 4, "Product:["+str(product_id.default_code)+"] "+str(product_id.name), style_table_header)
            prod_row = prod_row+1
            if product.product_tmpl_id.uom_id.id != purchase_uom_id:                                                                          
                    self.env.cr.execute("select floor(round(1/factor,2)) as ratio from uom_uom where active = true and id=%s", (purchase_uom_id,))
                    bigger = self.env.cr.fetchone()
                    if  bigger :
                        bigger_qty=bigger[0]
            #this below block is skipping number 0
            worksheet.write(prod_row, 3, "Opening Balance", style_table_header)
            worksheet.write(prod_row, 6, round(opening_balance,2), style_table_header)
            worksheet.write(prod_row, 7, round(opening_balance * product.volume, 2), style_table_header)
            worksheet.write(prod_row, 8, product.product_tmpl_id.uom_id.name, style_table_header)

            balance = opening_balance

            for move in moves:
                if move.product_uom_id.id != purchase_uom_id:
                        self.env.cr.execute("select floor(round(1/factor,2)) as ratio from uom_uom where active = true and id=%s", (purchase_uom_id,))
                        bigger = self.env.cr.fetchone() 
                        if  bigger :
                            bigger_qty=bigger[0]                                               
                #issuing
                if move.location_id.id==self.location_id.id:
                    prod_row = prod_row+1
                    #if move.picking_type_id.code == 'outgoing':
                    from_location = move.location_id.complete_name.replace('Physical Locations/','')
                    if move.picking_id.sudo().partner_id:
                        to_location = move.picking_id.sudo().partner_id.name
                    else:
                        to_location = move.location_dest_id.complete_name.replace('Physical Locations/','')
                    
                    txn_desc = "Transfer From "+  str(from_location) + " to " + str(to_location) 
                    if move.picking_id.sudo().origin:
                        txn_desc= txn_desc + ", TxnNo:"+ move.picking_id.sudo().origin
                        
                    balance = balance - move.qty_done
                    worksheet.write(prod_row, prod_col, move.date.strftime('%Y-%m-%d') , style)
                    worksheet.write(prod_row, prod_col+1, txn_desc , style)
                    worksheet.write(prod_row, prod_col+2, move.location_id.complete_name, style)
                    worksheet.write(prod_row, prod_col+3, move.reference, style)
                    worksheet.write(prod_row, prod_col+5, round(move.qty_done,2) , style)
                    worksheet.write(prod_row, prod_col+6, round(balance,2) , style)
                    worksheet.write(prod_row, prod_col+8, move.product_uom_id.name , style)
     
                    if self.show_purchase_uom:
                        worksheet.write(prod_row, prod_col+10,round( move.qty_done/bigger_qty,2) , style)
                        worksheet.write(prod_row, prod_col+11,  round(balance/bigger_qty,2) , style)
                        worksheet.write(prod_row, prod_col+12, purchase_uom_name, style)
                    
                if move.location_dest_id.id==self.location_id.id:
                    prod_row = prod_row+1
                    #if move.picking_type_id.code == 'incoming':
                    from_location = move.location_id.complete_name.replace('Physical Locations/','')
                    to_location = move.location_dest_id.name
                    if move.picking_id.sudo().partner_id:
                        from_location = move.picking_id.sudo().partner_id.name
                    else:
                        from_location = move.location_id.complete_name.replace('Physical Locations/','')
                        
                    txn_desc = "Transfer From "+  from_location + " to " + to_location
                    if move.picking_id.sudo().origin:
                        txn_desc= txn_desc + ", TxnNo:"+ move.picking_id.sudo().origin
                        
                    balance = balance + move.qty_done
                    worksheet.write(prod_row, prod_col, move.date.strftime('%Y-%m-%d') , style)
                    worksheet.write(prod_row, prod_col+1, txn_desc , style)
                    worksheet.write(prod_row, prod_col+2, move.location_id.complete_name, style)
                    worksheet.write(prod_row, prod_col+3, move.reference, style)
                    worksheet.write(prod_row, prod_col+4, round(move.qty_done,2) , style)
                    worksheet.write(prod_row, prod_col+6,  round(balance,2)   , style)
                    worksheet.write(prod_row, prod_col+8, move.product_uom_id.name , style)
                    


                #closing
            prod_row = prod_row+1
            worksheet.write(prod_row, 3, "Closing Balance", style_table_header)
            worksheet.write(prod_row, 6, round(balance,2), style_table_header)
            worksheet.write(prod_row, 7, round(balance * product.volume, 2), style_table_header)
            worksheet.write(prod_row, 8, product.product_tmpl_id.uom_id.name, style_table_header)
            
            if self.show_purchase_uom:
                worksheet.write(prod_row, 11, round(balance/bigger_qty,2), style_table_header)
                worksheet.write(prod_row, 12, product.product_tmpl_id.uom_po_id.name, style_table_header)

            prod_row = prod_row+2
        return prod_row,worksheet

    def _get_closing_balance(self,balance,  moves):
        for move in moves:
            if move.location_id.id == self.location_id.id:
                balance = balance - move.qty_done
            if move.location_dest_id.id == self.location_id.id:
                balance = balance + move.qty_done
        return balance

    def _get_beginning_inventory_ProductLedger(self, start_date,  location_id, warehouse_id, product_id):
        """
        Process:
            -Pass locations , start date and product_id
        Return:
            - Beginning inventory of product for exact date
        """
        if location_id:
            locations = [location_id]
        else:
            locations = self._find_locations(warehouse_id)

        self._cr.execute(''' 
                            SELECT id,coalesce(sum(qty), 0.0) AS qty
                            FROM
                                ((
                                SELECT
                                    pp.id, pp.default_code,m.date,
                                    coalesce(sum(-m.qty_done)::decimal, 0.0) as qty
                                FROM product_product pp 
                                LEFT JOIN stock_move_line m ON (m.product_id=pp.id)
                                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                                LEFT JOIN stock_location l on(m.location_id=l.id)
                                LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                                
                                WHERE m.date <  %s AND (m.location_id in %s) AND (m.location_dest_id not in %s) 
                                AND m.state='done' and pp.active=True AND pp.id = %s
                                GROUP BY  pp.id, pp.default_code,m.date
                                ) 
                                UNION ALL
                                (
                                SELECT
                                    pp.id, pp.default_code,m.date,
                                    coalesce(sum(m.qty_done)::decimal, 0.0) as qty
                                FROM product_product pp 
                                LEFT JOIN stock_move_line m ON (m.product_id=pp.id)
                                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                                LEFT JOIN stock_location l on(m.location_dest_id=l.id)    
                                LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                                
                                WHERE m.date <  %s AND (m.location_dest_id in %s) AND (m.location_id not in %s) 
                                AND m.state='done' and pp.active=True AND pp.id = %s
                                GROUP BY  pp.id,pp.default_code,m.date
                                ))
                                AS foo
                            group BY id
                            ''',(start_date, tuple(locations),tuple(locations),product_id, start_date, tuple(locations),tuple(locations),product_id))

        res = self._cr.dictfetchall()
        self.begining_qty = res and res[0].get('qty',0.0) or 0.0
        return self.begining_qty




class stock_ledger_excel_report(models.TransientModel):
    _name = "stock.ledger.report"

    excel_file = fields.Binary('Download Stock Ledger Excel Report', readonly =True)
    file_name = fields.Char('File', readonly=True)