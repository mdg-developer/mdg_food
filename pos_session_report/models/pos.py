# -*- coding: utf-8 -*-

import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class pos_config(models.Model):
    _inherit = 'pos.config' 

    allow_session_receipt = fields.Boolean('Allow Session Receipt', default=True)

class ReportSaleDetails(models.AbstractModel):

    _inherit = 'report.point_of_sale.report_saledetails'



    @api.model
    def get_pos_sale_details(self, date_start=False, date_stop=False, wvconfig_id=False):
        """ Serialise the orders of the day information

        params: date_start, date_stop string representing the datetime of order
        """
        wv_session_id = self.env['pos.session'].search([('config_id','=',wvconfig_id),('state','=','opened')])

        today = fields.Datetime.from_string(fields.Date.context_today(self))
        if date_start:
            date_start = fields.Datetime.from_string(date_start)
        else:
            # start by default today 00:00:00
            date_start = today

        if date_stop:
            # set time to 23:59:59
            date_stop = fields.Datetime.from_string(date_stop)
        else:
            # stop by default today 23:59:59
            date_stop = today + timedelta(days=1, seconds=-1)

        # avoid a date_stop smaller than date_start
        date_stop = max(date_stop, date_start)

        date_start = fields.Datetime.to_string(date_start)
        date_stop = fields.Datetime.to_string(date_stop)

        orders = self.env['pos.order'].search([
            ('state', 'in', ['paid','invoiced']),
            ('session_id', 'in', wv_session_id.ids)])

        user_currency = self.env.user.company_id.currency_id

        total = 0.0
        products_sold = {}
        taxes = {}
        payments = {}
        for order in orders:
            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id.compute(order.amount_total, user_currency)
            else:
                total += order.amount_total
            currency = order.session_id.currency_id

            for line in order.lines:
                key = (line.product_id, line.price_unit, line.discount)
                products_sold.setdefault(key, 0.0)
                products_sold[key] += line.qty

                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.compute_all(line.price_unit * (1-(line.discount or 0.0)/100.0), currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes.setdefault(tax['id'], {'name': tax['name'], 'total':0.0})
                        taxes[tax['id']]['total'] += tax['amount']

            for i in order.payment_ids:
                payments.setdefault(i.payment_method_id.id, {'name': i.payment_method_id.name, 'total':0.0})
                payments[i.payment_method_id.id]['total'] += i.amount


        return {
            'pos_name': wv_session_id[0].config_id.name,
            'cashier_name': wv_session_id[0].user_id.name,
            'session_start': wv_session_id[0].start_at,
            'session_end': fields.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'total_paid': user_currency.round(total),
            'payments': list(payments.values()),
            # 'company_name': self.env.user.company_id.name,
            'company_name': self.env.company.name,
            'taxes': list(taxes.values()),
            'products': sorted([{
                'product_id': product.id,
                'product_name': product.name,
                'code': product.default_code,
                'quantity': qty,
                'price_unit': price_unit,
                'discount': discount,
                'uom': product.uom_id.name
            } for (product, price_unit, discount), qty in products_sold.items()], key=lambda l: l['product_name'])
        }

