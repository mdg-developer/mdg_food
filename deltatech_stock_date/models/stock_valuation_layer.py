# ©  2015-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
import math
import time
import pytz
from odoo import fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta
import dateutil.parser


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"
    # _order = "date, id"
    #
    # date = fields.Datetime(related="stock_move_id.date", store=True, string="Move Date")

    # def convert_withtimezone(self, userdate):
    #     """
    #     Convert to Time-Zone with compare to UTC
    #     """
    #     user_date = datetime.strptime(userdate, DEFAULT_SERVER_DATETIME_FORMAT)
    #     print('user_date',user_date)
    #     tz_name = self.env.context.get('tz') or self.env.user.tz
    #     if tz_name:
    #         utc = pytz.timezone('UTC')
    #         context_tz = pytz.timezone(tz_name)
    #         # not need if you give default datetime into entry ;)
    #         user_datetime = user_date  # + relativedelta(hours=24.0)
    #         local_timestamp = context_tz.localize(user_datetime, is_dst=False)
    #         user_datetime = local_timestamp.astimezone(utc)
    #         return user_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    #     return user_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def _validate_accounting_entries(self):
        am_vals = []
        move_date = None
        for svl in self:
            if not svl.with_company(svl.company_id).product_id.valuation == 'real_time':
                continue
            if svl.currency_id.is_zero(svl.value):
                continue
            move = svl.stock_move_id
            if not move:
                move = svl.stock_valuation_layer_id.stock_move_id
                if move.picking_id:
                    move.date = svl.stock_valuation_layer_id.stock_move_id.picking_id.actual_date
                    move_date = svl.stock_valuation_layer_id.stock_move_id.picking_id.actual_date + timedelta(
                        minutes=390)
            else:
                if svl.stock_move_id.picking_id:
                    move.date = svl.stock_move_id.picking_id.actual_date
                    move_date = svl.stock_move_id.picking_id.actual_date + timedelta(minutes=390)


            am_vals += move.with_company(svl.company_id)._account_entry_move(svl.quantity, svl.description, svl.id, svl.value)
        # print('move_date',move_date)
        if move_date:
            for amvl in am_vals:
                amvl.update({'date': move_date})
        if am_vals:
            account_moves = self.env['account.move'].sudo().create(am_vals)
            account_moves._post()
        for svl in self:
            # Eventually reconcile together the invoice and valuation accounting entries on the stock interim accounts
            if svl.company_id.anglo_saxon_accounting:
                svl.stock_move_id._get_related_invoices()._stock_account_anglo_saxon_reconcile_valuation(product=svl.product_id)
