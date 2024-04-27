# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)
import xlsxwriter
from odoo import http
from odoo.http import content_disposition, request
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape
from odoo import http
from odoo.http import content_disposition, request
import json
from odoo.exceptions import Warning
from odoo import models, fields, api, _
import itertools,operator
import logging
_logger = logging.getLogger(__name__)
from io import StringIO
import io
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class inventory_reports_wizard(models.TransientModel):    
    _inherit = 'stock.inventory.reports'    
    

    def print_xlsx(self):
        """
            Print report either by warehouse or product-category
        """
        data_obj = self.env['report.stock_inventory_report_xls.inventory_report_by_warehouse']
        data_obj_cat = self.env['report.stock_inventory_report_xls.inventory_report_by_category']
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        datas = {
                 'form':
                        {
                            'company_id': self.company_id and [self.company_id.id] or [],
                            'warehouse_ids': [y.id for y in self.warehouse_ids],
                            'location_id': self.location_id and self.location_id.id or False,
                            'start_date': self.start_date,
                            'end_date': self.end_date,
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
            return data_obj_cat.xlsx_export(datas)
#                                 'stock_inventory_report_xls.report_inventory_report_by_category_xlsx'
#                                 ).with_context(landscape=True,discard_logo_check=True).report_action(self, data=datas)
        return data_obj.xlsx_export(datas)