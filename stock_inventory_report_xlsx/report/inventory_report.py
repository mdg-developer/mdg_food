# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)
from io import StringIO
import io
import json
import xlsxwriter
import time
import pytz
import xlwt.Style
from odoo import models, api
from datetime import datetime
import calendar
import copy
import logging
import lxml.html
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

from xlwt import easyxf

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    # TODO saas-17: remove the try/except to directly import from misc
    import xlsxwriter

from odoo import models, fields, api, _
from datetime import timedelta, datetime, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, pycompat
from babel.dates import get_quarter_names
from odoo.tools.misc import formatLang, format_date
from odoo.tools import config
from odoo.addons.web.controllers.main import clean_action
from odoo.tools.safe_eval import safe_eval
from odoo.http import controllers_per_module
_logger = logging.getLogger(__name__)
from odoo.tools import date_utils
from odoo.tools.misc import str2bool, xlsxwriter, file_open, file_path


class inventory_report(models.AbstractModel):
    _name = 'report.stock_inventory_report_xls.inventory_report_by_warehouse'
    _inherit = 'account.report'


    begining_qty = fields.Float()
    total_in = fields.Float()
    total_out = fields.Float()
    total_int = fields.Float()
    total_adj = fields.Float()
    total_begin = fields.Float()
    total_end = fields.Float()
    total_inventory = []
    value_exist = {}


    @api.model
    def get_report_values(self, docids, data=None):

        return {
            'doc_ids': self._ids,
            'docs': self,
            'data': data,
            'time': time,
            'get_warehouse_name': self.get_warehouse_name,
            'get_company': self._get_company,
            'get_product_name': self._product_name,
            'get_categ':self._get_categ,
            'get_main_categ': self._get_main_categ,
            'get_warehouse': self._get_warehouse,
            'get_lines': self._get_lines,
            'get_beginning_inventory': self._get_beginning_inventory,
            'get_ending_inventory': self._get_ending_inventory,
            'get_value_exist': self._get_value_exist,
            'total_in': self._total_in,
            'total_out': self._total_out,
            'total_int': self._total_int,
            'total_adj': self._total_adj,
            'total_vals': self._total_vals,
            'total_begin': self._total_begin,
            'total_end': self._total_end
            }
                         
    def _total_in(self):
        """
        Warehouse wise inward Qty
        """
        return self.total_in

    def _total_out(self):
        """
        Warehouse wise out Qty
        """
        return self.total_out

    def _total_int(self):
        """
        Warehouse wise internal Qty
        """
        return self.total_int

    def _total_adj(self):
        """
        Warehouse wise adjustment Qty
        """
        return self.total_adj

    def _total_begin(self):
        """
        Warehouse wise begining Qty
        """
        return self.total_begin

    def _total_end(self):
        """
        Warehouse wise ending Qty
        """
        return self.total_end

    def _total_vals(self, company_id):
        """
        Grand Total Inventory
        """
        ftotal_in = ftotal_out = ftotal_int = ftotal_adj = ftotal_begin = ftotal_end = 0.0
        for data in self.total_inventory:
            for key,value in data.items():
                if key[1] == company_id:
                    ftotal_in += value['total_in']
                    ftotal_out += value['total_out']
                    ftotal_int += value['total_int']
                    ftotal_adj += value['total_adj']
                    ftotal_begin += value['total_begin']
                    ftotal_end += value['total_end']

        return ftotal_begin, ftotal_in,ftotal_out,ftotal_int,ftotal_adj,ftotal_end 


    def _get_value_exist(self,warehouse_id, company_id):
        """
        Compute Total Values
        """
        total_in = total_out = total_int = total_adj = total_begin = 0.0

        for warehouse in self.value_exist[warehouse_id]:
            total_in  += warehouse.get('product_qty_in',0.0)
            total_out  += warehouse.get('product_qty_out',0.0)
            total_int  += warehouse.get('product_qty_internal',0.0)
            total_adj  += warehouse.get('product_qty_adjustment',0.0)
            total_begin += warehouse.get('begining_qty',0.0)

        total_in = total_in
        total_out = total_out
        total_int = total_int
        total_adj = total_adj
        total_begin = total_begin
        total_end = total_begin + total_in + total_out + total_int + total_adj
        self.total_inventory.append({
                                     (warehouse_id,company_id):{'total_in': total_in,
                                                                'total_out': total_out,
                                                                'total_int':total_int,
                                                                'total_adj':total_adj,
                                                                'total_begin':total_begin,
                                                                'total_end':total_end
                                                                }})
        return ''

    def _get_company(self, company_ids):
        res_company_pool = self.env['res.company']
        if not company_ids:
            company_ids  = [x.id for x in res_company_pool.search([])] 

        #filter to only have warehouses.
        selected_companies = []
        for company_id in company_ids:
            if self.env['stock.warehouse'].search([('company_id','=',company_id)]):
                selected_companies.append(company_id)

        return res_company_pool.browse(selected_companies).read(['name'])
    

    def get_warehouse_name(self, warehouse_ids):
        """
        Return warehouse names
            - WH A, WH B...
        """
        warehouse_obj = self.env['stock.warehouse']
        if not warehouse_ids:
            warehouse_ids = [x.id for x in warehouse_obj.search([])]
        war_detail = warehouse_obj.read(warehouse_ids,['name'])
        return ', '.join([lt['name'] or '' for lt in war_detail])

    #Added conversion with dual uom #need to check in deeply
    def _get_beginning_inventory(self, data, warehouse_id,prod_id,current_record):
        """
        Process:
            -Pass locations , start date and product_id
        Return:
            - Beginning inventory of product for exact date
        """
        location_id = data['form'] and data['form'].get('location_id') or False
        if location_id:
            locations = [location_id]
        else:
            locations = self._find_locations(warehouse_id)

        from_date = self.convert_withtimezone(data['form']['start_date']+' 00:00:00')

        self._cr.execute('''
                                SELECT product_id,(product_qty_out + product_qty_in+ product_qty_internal+ product_qty_adjustment) AS qty from(
                                SELECT pp.id AS product_id,
                                    sum((
                                        CASE WHEN spt.code in ('outgoing') AND sm.location_id in %s AND sourcel.usage !='inventory' and destl.usage !='inventory' 
                                        THEN -(sm.qty_done * pu.factor / pu2.factor)
                                        ELSE 0.0 
                                        END
                                    )) AS product_qty_out,
                                    sum((
                                        CASE WHEN spt.code in ('incoming','outgoing') AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                                        THEN (sm.qty_done * pu.factor / pu2.factor)
                                        ELSE 0.0 
                                        END
                                    )) AS product_qty_in,
                                    sum((
                                        CASE WHEN (spt.code ='internal' or spt.code is null) AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                                        THEN (sm.qty_done * pu.factor / pu2.factor)  
                                        WHEN (spt.code='internal' or spt.code is null) AND sm.location_id in %s AND sourcel.usage !='inventory' and destl.usage !='inventory' 
                                        THEN -(sm.qty_done * pu.factor / pu2.factor)
                                        ELSE 0.0 
                                        END
                                    )) AS product_qty_internal,

                                    sum((
                                        CASE WHEN sourcel.usage = 'inventory' AND sm.location_dest_id in %s 
                                        THEN  (sm.qty_done * pu.factor / pu2.factor)
                                        WHEN destl.usage ='inventory' AND sm.location_id in %s 
                                        THEN -(sm.qty_done * pu.factor / pu2.factor)
                                        ELSE 0.0 
                                        END
                                    )) AS product_qty_adjustment

                                FROM product_product pp 
                                LEFT JOIN  stock_move_line sm ON (sm.product_id = pp.id and sm.date <= %s and sm.state = 'done' and sm.location_id != sm.location_dest_id)
                                LEFT JOIN stock_picking sp ON (sm.picking_id=sp.id)
                                LEFT JOIN stock_move move ON (sm.move_id=move.id)
                                LEFT JOIN stock_picking_type spt ON (spt.id=move.picking_type_id)
                                LEFT JOIN stock_location sourcel ON (sm.location_id=sourcel.id)
                                LEFT JOIN stock_location destl ON (sm.location_dest_id=destl.id)
                                LEFT JOIN uom_uom pu ON (sm.product_uom_id=pu.id)
                                LEFT JOIN uom_uom pu2 ON (sm.product_uom_id=pu2.id)
                                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                                WHERE  sm.state='done' and pp.active=True  AND pt.type in ('product','consu') and pp.active='true' and pp.id = %s
                                GROUP BY pp.id order by pp.id
                                )AA
                                ''', (tuple(locations), tuple(locations), tuple(locations), tuple(locations), tuple(locations), tuple(locations),from_date, prod_id))

        res = self._cr.dictfetchall()
        # print(res[0].get('qty'))

        begining_qty = res and res[0].get('qty') or 0.0
        current_record.update({'begining_qty': begining_qty})
        return begining_qty

    def _get_ending_inventory(self, in_qty, out_qty,internal_qty,adjust_qty):
        """
        Process:
            -Inward, outward, internal, adjustment
        Return:
            - total of those qty
        """
        return self.begining_qty + in_qty + out_qty + internal_qty + adjust_qty

    def convert_withtimezone(self, userdate):
        """ 
        Convert to Time-Zone with compare to UTC
        """
        user_date = datetime.strptime(userdate, DEFAULT_SERVER_DATETIME_FORMAT)
        tz_name = self.env.context.get('tz') or self.env.user.tz
        if tz_name:
            utc = pytz.timezone('UTC')
            context_tz = pytz.timezone(tz_name)
            # not need if you give default datetime into entry ;)
            user_datetime = user_date  # + relativedelta(hours=24.0)
            local_timestamp = context_tz.localize(user_datetime, is_dst=False)
            user_datetime = local_timestamp.astimezone(utc)
            return user_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return user_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def location_wise_value(self, start_date, end_date, locations , include_zero=True,filter_product_ids=[]):
        """
        Complete data with location wise
            - In Qty (Inward Quantity to given location)
            - Out Qty(Outward Quantity to given location)
            - Internal Qty(Internal Movements to given location: out/in both : out must be - ,In must be + )
            - Adjustment Qty(Inventory Loss movements to given location: out/in both: out must be - ,In must be + )
        Return:
            [{},{},{}...]
        """

        self._cr.execute('''
                        SELECT pp.id AS product_id,
                            sum((
                                CASE WHEN spt.code in ('outgoing','incoming') AND sm.location_id in %s AND sourcel.usage !='inventory' and destl.usage !='inventory' 
                                THEN -(sm.qty_done * pu.factor / pu2.factor)
                                ELSE 0.0 
                                END
                            )) AS product_qty_out,
                            sum((
                                CASE WHEN spt.code in ('incoming','outgoing') AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                                THEN (sm.qty_done * pu.factor / pu2.factor)
                                ELSE 0.0 
                                END
                            )) AS product_qty_in,
                            sum((
                                CASE WHEN (spt.code ='internal' or spt.code is null) AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                                THEN (sm.qty_done * pu.factor / pu2.factor)  
                                WHEN (spt.code='internal' or spt.code is null) AND sm.location_id in %s AND sourcel.usage !='inventory' and destl.usage !='inventory' 
                                THEN -(sm.qty_done * pu.factor / pu2.factor)
                                ELSE 0.0 
                                END
                            )) AS product_qty_internal,
                        
                            sum((
                                CASE WHEN sourcel.usage = 'inventory' AND sm.location_dest_id in %s 
                                THEN  (sm.qty_done * pu.factor / pu2.factor)
                                WHEN destl.usage ='inventory' AND sm.location_id in %s 
                                THEN -(sm.qty_done * pu.factor / pu2.factor)
                                ELSE 0.0 
                                END
                            )) AS product_qty_adjustment
                        
                        FROM product_product pp 
                        LEFT JOIN  stock_move_line sm ON (sm.product_id = pp.id and sm.date >= %s and sm.date <= %s and sm.state = 'done' and sm.location_id != sm.location_dest_id)
                        LEFT JOIN stock_picking sp ON (sm.picking_id=sp.id)
                        LEFT JOIN stock_move move ON (sm.move_id=move.id)
                        LEFT JOIN stock_picking_type spt ON (spt.id=move.picking_type_id)
                        LEFT JOIN stock_location sourcel ON (sm.location_id=sourcel.id)
                        LEFT JOIN stock_location destl ON (sm.location_dest_id=destl.id)
                        LEFT JOIN uom_uom pu ON (sm.product_uom_id=pu.id)
                        LEFT JOIN uom_uom pu2 ON (sm.product_uom_id=pu2.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        WHERE  sm.state='done' and pp.active=True  AND pt.type in ('product','consu') and pp.active='true'
                        GROUP BY pp.id order by pp.id
                        ''',(tuple(locations),tuple(locations),tuple(locations),tuple(locations),tuple(locations),tuple(locations),start_date, end_date))
        print("Location",tuple(locations))
        values = self._cr.dictfetchall()

        for none_to_update in values:
            if not none_to_update.get('product_qty_out'):
                none_to_update.update({'product_qty_out':0.0})
            if not none_to_update.get('product_qty_in'):
                none_to_update.update({'product_qty_in':0.0})
        #add no transaction product
        values = self._add_no_transaction_inventory(values)
        #Removed zero values dictionary
        if not include_zero:
            values = self._remove_zero_inventory(values)
        #filter by products
        if filter_product_ids:
            values = self._remove_product_ids(values, filter_product_ids)
        return values
    def _add_no_transaction_inventory(self, values):
        final_values = []
        product_list = []
        for rm_zero in values:
            final_values.append(rm_zero)
            product_list.append(rm_zero['product_id'])
        for product in self.env['product.product'].search([('id','not in',product_list),('type','in', ['product','consu'])]):
            final_values.append({'product_id': product.id, 'product_qty_out': 0.0, 'product_qty_in': 0.0, 'product_qty_internal': 0.0, 'product_qty_adjustment': 0.0})
        return final_values

    def _remove_zero_inventory(self, values):
        final_values = []
        for rm_zero in values:
            if rm_zero['product_qty_in'] == 0.0 and rm_zero['product_qty_internal'] == 0.0 and rm_zero['product_qty_out'] == 0.0 and rm_zero['product_qty_adjustment'] == 0.0:
                pass
            else: final_values.append(rm_zero)
        return final_values

    def _remove_product_ids(self, values, filter_product_ids):
        final_values = []
        for rm_products in values:
            if rm_products['product_id'] not in filter_product_ids:
                pass
            else: final_values.append(rm_products)
        return final_values

    
    def _get_warehouse(self, warehouse):
        """
        Find warehouse name with id
        """
        return self.env['stock.warehouse'].browse(warehouse).read(['name'])[0]['name']

    def _product_name(self, product_id):
        """
        Find product name and assign to it
        """
        # product = self.env['product.product'].browse(product_id).name_get()
        product = self.env['product.product'].browse(product_id).name
        return product
        # return product and product[0] and product[0][1] or ''

    def _get_product_code(self, product_id):
        code = self.env['product.product'].browse(product_id).default_code
        return code

    def _get_categ(self, product_id ):
        """
        Find category name with id
        """
        self._cr.execute ( '''
        select pc.name from product_product pp ,product_template pt ,product_category pc
        where pp.product_tmpl_id =pt.id
        and pc.id = pt.categ_id
        and pp.id = %s
        ''', (product_id,))
        categ_name = self._cr.fetchone()[0]
        return categ_name
    def _get_main_categ(self, product_id ):
        """
        Find category name with id
        """
        self._cr.execute ( '''
        select (select name from product_category where id =pc.parent_id) as main_categ from product_product pp ,product_template pt ,product_category pc
        where pp.product_tmpl_id =pt.id
        and pc.id = pt.categ_id
        and pp.id = %s
        ''', (product_id,))
        categ_name = self._cr.fetchone()[0]
        return categ_name
    def _product_volume(self, product_id):
        volume = self.env['product.product'].browse(product_id).volume
        if volume:
            return volume
        return 0

    def find_warehouses(self,company_id):
        """
        Find all warehouses
        """
        return [x.id for x in self.env['stock.warehouse'].search([('company_id','=',company_id)])]

    def _find_locations(self, warehouse):
        """
        Find warehouse stock locations and its childs.
            -All stock reports depends on stock location of warehouse.
        """
        warehouse_obj = self.env['stock.warehouse']
        location_obj = self.env['stock.location']
        store_location_id = warehouse_obj.browse(warehouse).view_location_id.id
        return [x.id for x in location_obj.search([('location_id', 'child_of', store_location_id)])]

    def _compare_with_company(self, warehouse, company):
        """
        Company loop check ,whether it is in company of not.
        """
        company_id = self.env['stock.warehouse'].browse(warehouse).read(['company_id'])[0]['company_id']
        if company_id[0] != company:
            return False
        return True

    def _get_lines(self, data, company):
        """
        Process:
            Pass start date, end date, locations to get data from moves,
            Merge those data with locations,
        Return:
            {location : [{},{},{}...], location : [{},{},{}...],...}
        """
        start_date = self.convert_withtimezone(data['form']['start_date']+' 00:00:00')
        end_date =  \
            self.convert_withtimezone(data['form']['end_date']+' 23:59:59')

        warehouse_ids = data['form'] and data['form'].get('warehouse_ids',[]) or []
        include_zero = data['form'] and data['form'].get('include_zero') or False
        filter_product_ids = data['form'] and data['form'].get('filter_product_ids') or []
        location_id = data['form'] and data['form'].get('location_id') or False
        if not warehouse_ids:
            warehouse_ids = self.find_warehouses(company)

        final_values = {}
        for warehouse in warehouse_ids:
            #looping for only warehouses which is under current company
            if self._compare_with_company(warehouse, company[0]):
                locations = self._find_locations(warehouse)
                if location_id:
                    if (location_id in locations):
                        final_values.update({
                                             warehouse:self.location_wise_value(start_date, end_date, [location_id], include_zero,filter_product_ids)
                                             })
                else:
                    final_values.update({
                                         warehouse:self.location_wise_value(start_date, end_date, locations, include_zero,filter_product_ids)
                                         })
        self.value_exist.update(final_values)
        return final_values
    
    def get_report_name(self):
        return _('Inventory Report By Warehouse')

    def get_report_filename(self, options):
        """The name that will be used for the file when downloading pdf,xlsx,..."""
        return self.get_report_name().lower().replace(' ', '_')
    def get_header_name(self):
        return _('Inventory Report')
       
    def get_xlsx(self, options,response=None):
        output = io.BytesIO()
        get_lines=[]
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(self.get_report_name()[:31])

        # self._define_formats(workbook)
        style_result = self._define_formats(workbook)

        sheet.set_column(0, 0, 15) #  Set the first column width to 15
        y_offset = 0
        x = 0

        get_lines=self.get_report_values(self._ids, options)
        company_name = warehouse_name =warehouse_name_group ='' 
        cid=options['form']['company_id']
        #Company Parameter 
        if cid:            
            for company in self.env['res.company'].browse(cid).name_get():
                company_name += str(company[1]) + ','
            company_name = company_name[:-1]    
        else:
            company_name = 'All' 
        #Warehouse Parameter 
        warehouse_id=options['form']['warehouse_ids']
        if warehouse_id:            
            for warehouse in self.env['stock.warehouse'].browse(warehouse_id).name_get():
                warehouse_name += str(warehouse[1]) + ','
            warehouse_name = warehouse_name[:-1]    
        else:
            warehouse_name = 'All' 
        #Date Parameter   
        df = _('From') + ': '
        df += options['form']['start_date'] if options['form']['start_date'] else u''
        df += ' ' + _('To') + ': '
        df += options['form']['end_date'] if options['form']['end_date'] else u''
                
        sheet.merge_range(y_offset, 3, y_offset, 4, _('Inventory Report'),style_result['format_title'])
        y_offset += 2
        
        sheet.merge_range(y_offset, 1, y_offset, 2, _('Company'), style_result['format_header_center'])
        sheet.set_column(1, 2, 20)
        sheet.merge_range(y_offset, 3, y_offset, 4, _('Warehouse'), style_result['format_header_center'])
        sheet.set_column(3,4, 20)
        sheet.merge_range(y_offset, 5, y_offset, 6, _('Date'), style_result['format_header_center'])
        sheet.set_column(5, 6, 20)
        sheet.write(y_offset, 7, _('Sort By'), style_result['format_header_center'])
        sheet.set_column(7, 7, 20)
        y_offset += 1

        sheet.merge_range(y_offset, 1, y_offset, 2, company_name or '', style_result['format_title_data'])
        sheet.set_column(1, 2, 20)
        sheet.merge_range(y_offset, 3, y_offset, 4, warehouse_name or '', style_result['format_title_data'])
        sheet.set_column(3, 4, 20)
        sheet.merge_range(y_offset, 5, y_offset, 6, df or 'All', style_result['format_title_data'])
        sheet.set_column(5, 6, 20)
        sheet.write(y_offset, 7, options['form']['sort_order'] or '', style_result['format_title_data'])
        sheet.set_column(7, 7, 20)            
        y_offset += 2
        
        lines=self._get_lines(options,options['form']['company_id'])

        # sheet.merge_range(y_offset, 0, y_offset, 1, _('Product Code'), style_result['format_header_one'])
        sheet.write(y_offset, 0, _('Product Code'), style_result['format_header_one'])
        sheet.set_column(0, 0, 20)
        sheet.merge_range(y_offset, 1, y_offset, 2, _('Product'), style_result['format_header_one'])
        sheet.set_column(1, 2, 20)
        sheet.write(y_offset, 3,_('Main Category'), style_result['format_header_one'])
        sheet.set_column(4,4, 20)
        sheet.write(y_offset, 4,_('Sub Category'), style_result['format_header_one'])
        sheet.set_column(5,5, 20)
        sheet.write(y_offset, 5,_('Beginning'), style_result['format_header_one'])
        sheet.set_column(6, 6, 20)
        sheet.write(y_offset, 6, _('In'), style_result['format_header_one'])
        sheet.set_column(7, 7, 20)
        sheet.write(y_offset, 7, _('Out'), style_result['format_header_one'])
        sheet.set_column(8, 8, 20)
        sheet.write(y_offset, 8, _('Internal'), style_result['format_header_one'])
        sheet.set_column(9, 9, 20)
        sheet.write(y_offset, 9, _('Adjustment'), style_result['format_header_one'])
        sheet.set_column(10, 10, 20)
        sheet.write(y_offset, 10, _('Ending'), style_result['format_header_one'])
        sheet.set_column(11, 11, 20)
        y_offset += 1
        wh_vol_total = 0
        global_vol_total = 0
        total_begin=total_in=total_out= total_int=total_adj=total_end= 0
        total_wh_begin=total_wh_in=total_wh_out= total_wh_int=total_wh_adj=total_wh_end= 0
        for line_wh in lines:
            for line in lines[line_wh]:
                product_name=self._product_name(line.get('product_id'))
                product_code = self._get_product_code(line.get('product_id'))
                product_main_categ = self._get_main_categ(line.get('product_id'))
                product_categ = self._get_categ(line.get('product_id'))
                product_vol = self._product_volume(line.get('product_id'))
                begin_qty=self._get_beginning_inventory(options,line_wh,line.get('product_id'),line)
                total_begin+=begin_qty
                total_in+=line.get('product_qty_in', 0.0)
                total_out+=line.get('product_qty_out', 0.0)
                total_int+=line.get('product_qty_internal', 0.0)
                total_adj+=line.get('product_qty_adjustment', 0.0)
                ending_qty = begin_qty + line.get('product_qty_in', 0.0) + line.get('product_qty_out', 0.0)+  line.get('product_qty_internal', 0.0) + line.get('product_qty_adjustment', 0.0)
                total_end+=ending_qty
                ending_qty = begin_qty + line.get('product_qty_in', 0.0) + line.get('product_qty_out', 0.0) + line.get('product_qty_internal', 0.0) + line.get('product_qty_adjustment', 0.0)
                vol_total = ending_qty * product_vol
                wh_vol_total+= vol_total
                sheet.write(y_offset, 0, product_code or '', style_result['product_format'])
                sheet.set_column(0, 0, 20)
                sheet.merge_range(y_offset, 1, y_offset, 2, product_name or '', style_result['product_format'])
                sheet.set_column(1, 2, 20)
                sheet.write(y_offset, 3, product_main_categ or '', style_result['product_format'])
                sheet.set_column(3, 3, 20)
                sheet.write(y_offset, 4, product_categ or '', style_result['product_format'])
                sheet.set_column(4, 4, 20)
                sheet.write(y_offset,5, begin_qty or 0.0, style_result['format_border_top'])
                sheet.set_column(5, 5, 20)
                sheet.write(y_offset, 6, line.get('product_qty_in', 0.0) or 0.0, style_result['format_border_top'])
                sheet.set_column(6, 6, 20)
                sheet.write(y_offset, 7, line.get('product_qty_out', 0.0) or 0.0, style_result['format_border_top'])
                sheet.set_column(7,7, 20)
                sheet.write(y_offset, 8, line.get('product_qty_internal', 0.0) or 0.0, style_result['format_border_top'])
                sheet.set_column(8, 8, 20)
                sheet.write(y_offset, 9, line.get('product_qty_adjustment', 0.0) or 0.0, style_result['format_border_top'])
                sheet.set_column(9,9, 20)
                sheet.write(y_offset, 10, (ending_qty) or 0.0, style_result['format_border_top'])
                sheet.set_column(10, 10, 20)
                y_offset += 1
                
            if line_wh:            
                for warehouse in self.env['stock.warehouse'].browse(line_wh).name_get():
                    warehouse_name_group = str(warehouse[1]) + ','
                warehouse_name_group = warehouse_name_group[:-1]    
            else:
                warehouse_name_group = 'All' 
            self._get_value_exist(line_wh, cid[0])
            toal_val=self._total_vals(cid[0])         
            sheet.merge_range(y_offset, 0, y_offset, 4, warehouse_name_group or '', style_result['format_header_one'])
            sheet.set_column(0, 4, 20)
            sheet.write(y_offset,5,"{:0,.2f}".format(total_begin) or 0.0, style_result['format_header_one'])
            sheet.set_column(5, 5, 20)
            sheet.write(y_offset, 6,"{:0,.2f}".format(total_in) or 0.0, style_result['format_header_one'])
            sheet.set_column(6, 6, 20)
            sheet.write(y_offset, 7, "{:0,.2f}".format(total_out) or 0.0, style_result['format_header_one'])
            sheet.set_column(7,7, 20)
            sheet.write(y_offset, 8, "{:0,.2f}".format(total_int) or 0.0, style_result['format_header_one'])
            sheet.set_column(8, 8, 20)
            sheet.write(y_offset, 9, "{:0,.2f}".format(total_adj) or 0.0, style_result['format_header_one'])
            sheet.set_column(9,9, 20)
            sheet.write(y_offset, 10, "{:0,.2f}".format(total_end) or 0.0, style_result['format_header_one'])
            sheet.set_column(10, 10, 20)
            global_vol_total+=wh_vol_total
            wh_vol_total=0
            y_offset += 2
            
            total_wh_begin+=total_begin
            total_wh_in+=total_in
            total_wh_out+=total_out
            total_wh_int+=total_int
            total_wh_adj+=total_adj
            total_wh_end+=total_end
            total_begin=total_in=total_out= total_int=total_adj=total_end= 0
                              
        
        total_toal_val=self._total_vals(cid[0])
        sheet.merge_range(y_offset, 0, y_offset, 4, 'Total Inventory', style_result['format_header_one'])
        sheet.set_column(0, 4, 20)
        sheet.write(y_offset,5,"{:0,.2f}".format(total_wh_begin) or 0.0, style_result['format_header_one'])
        sheet.set_column(5, 5, 20)
        sheet.write(y_offset, 6,"{:0,.2f}".format(total_wh_in) or 0.0, style_result['format_header_one'])
        sheet.set_column(6, 6, 20)
        sheet.write(y_offset, 7, "{:0,.2f}".format(total_wh_out) or 0.0, style_result['format_header_one'])
        sheet.set_column(7,7, 20)
        sheet.write(y_offset, 8,"{:0,.2f}".format(total_wh_int) or 0.0, style_result['format_header_one'])
        sheet.set_column(8, 8, 20)
        sheet.write(y_offset, 9,"{:0,.2f}".format(total_wh_adj) or 0.0, style_result['format_header_one'])
        sheet.set_column(9,9, 20)
        sheet.write(y_offset, 10, "{:0,.2f}".format(total_wh_end) or 0.0, style_result['format_header_one'])
        sheet.set_column(10, 10, 20)
        y_offset += 1
        workbook.close()
        output.seek(0)
        return output.getvalue()

    def xlsx_export(self, datas):
        # data = self.get_report_values(self._ids, datas)
        return {
            'type': 'ir_actions_account_report_download',
            'data': {'model': 'report.stock_inventory_report_xls.inventory_report_by_warehouse',
                     'options': json.dumps(datas, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'financial_id': self.env.context.get('id'),
                     }
        }
        
    def _define_formats(self, workbook):
        """ Add cell formats to current workbook.
        Available formats:
         * format_title
         * format_header
         * format_header_right
         * format_header_italic
         * format_border_top
        """

        format_title_company = workbook.add_format({
            'bold': True,
            'align': 'center',
        })
        format_title_data = workbook.add_format({
            'border': True,
            'align': 'center',
        })
        format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 14,
        })
        format_header = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFCC',
            'border': True
        })
        format_header_right = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFCC',
            'border': True,
            'align': 'right'
        })
        format_header_center = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFCC',
            'border': True,
            'align': 'center'
        })
        format_header_italic = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFCC',
            'border': True,
            'italic': True
        })
        format_border_top = workbook.add_format({
            'border': True,
            'align': 'center'
        })
        product_format = workbook.add_format({
            'border': True,
            'align': 'left'
        })
        format_header_one = workbook.add_format({
            'align': 'center',
            'bold': True,
            'border': True,
        })

        style_result = {
            'format_title_company': format_title_company,
            'format_title_data': format_title_data,
            'format_title': format_title,
            'format_header': format_header,
            'format_header_right': format_header_right,
            'format_header_center': format_header_center,
            'format_header_italic': format_header_italic,
            'format_border_top': format_border_top,
            'product_format': product_format,
            'format_header_one': format_header_one,


        }
        return style_result

