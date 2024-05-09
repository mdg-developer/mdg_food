# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
import time
import logging
_logger = logging.getLogger(__name__)
from odoo.http import request


class PosSession(models.Model):
    _inherit = "pos.session"

    def _wk_get_utc_time_(self,session_date):
        if session_date:
            session_date = datetime.strptime(session_date, "%Y/%m/%d %H:%M")
            tz_name = self._context.get('tz') or self.env.user.tz
            tz = tz_name and pytz.timezone(tz_name) or pytz.UTC
            return fields.Datetime.to_string(pytz.UTC.localize(session_date))

    def get_root_categ(self, pos_categ_id):
        if pos_categ_id.parent_id:
            return self.get_root_categ(pos_categ_id.parent_id)
        else:
            return pos_categ_id

    @api.model
    def wk_session_sale_details(self):
        for self_obj in self:
            orders = self_obj.order_ids
            products_sold = {}
            total_sale = 0.0
            total_discount = 0.0  
            discount_amount = 0.0          
            total_foc_discount = 0.0
            total_refund = 0.0
            total_sale_by_categ = {}
            amount_payment_journal = {}
            amount_summary_by_journal = {}
            total_payment_amount = 0.0
            total_tax = 0.0
            order_details = []

            for order in orders:
                total_tax += order.amount_tax
                if order.is_return_order:
                    total_refund += order.amount_total
                else:
                    for line in order.lines:
                        if line.discount and line.discount >0:
                            if line.discount <100:
                                discount = (line.price_subtotal_incl*100/(100-line.discount)) - line.price_subtotal_incl
                                total_discount += discount
                                discount_amount += discount
                            else:
                                taxes= line.tax_ids_after_fiscal_position.compute_all(line.price_unit, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id)
                                total_foc_discount += taxes['total_included']
                                total_discount += taxes['total_included']
                        if line.product_id == line.order_id.config_id.discount_product_id:
                            discount_amount += abs(line.price_unit)
                            total_discount += abs(line.price_unit)
                        if(line.product_id and line.product_id.pos_categ_id):
                            pos_categ_id = self.get_root_categ(line.product_id.pos_categ_id)
                            taxes= line.tax_ids_after_fiscal_position.compute_all(line.price_unit, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id)
                            price_subtotal_incl = taxes['total_included']
                            if(total_sale_by_categ.get(pos_categ_id.name)):
                                # total_sale_by_categ[pos_categ_id.name] += line.price_unit
                                total_sale_by_categ[pos_categ_id.name] += price_subtotal_incl
                            else:
                                # total_sale_by_categ[pos_categ_id.name] = line.price_unit
                                total_sale_by_categ[pos_categ_id.name] = price_subtotal_incl

                for statement in order.payment_ids:
                    total_payment_amount += statement.amount
                    if amount_payment_journal.get(statement.payment_method_id.name):
                        amount_payment_journal[statement.payment_method_id.name][1] += statement.amount
                    else:
                        amount_payment_journal[statement.payment_method_id.name] = [statement.payment_method_id.name, statement.amount]

                    if amount_summary_by_journal.get(statement.payment_method_id.name):
                        amount_summary_by_journal[statement.payment_method_id.name][1] += statement.amount
                    else:
                        amount_summary_by_journal[statement.payment_method_id.name] = [statement.payment_method_id.name, statement.amount]

            for k, v in amount_summary_by_journal.items():
                if k == self.payment_method_ids.filtered('is_cash_count')[:1].name:
                    amount_summary_by_journal[k][1] += self.cash_register_balance_start

            total_sale = sum(total_sale_by_categ.values())
            return {
                'total_sale':self.config_id.currency_id.round(total_sale),
                'total_refund':self.config_id.currency_id.round(-1*total_refund),
                'total_discount':self.config_id.currency_id.round(total_discount),
                'discount_amount':self.config_id.currency_id.round(discount_amount),
                'total_foc_discount':self.config_id.currency_id.round(total_foc_discount),
                'total_tax':self.config_id.currency_id.round(total_tax),
                'net_sale': self.config_id.currency_id.round(total_sale - total_discount - (-1*total_refund)),
                'total_sale_by_categ':[(key,self.config_id.currency_id.round(value)) for key,value in total_sale_by_categ.items()],
                'amount_payment_journal': list(amount_payment_journal.values()),
                'amount_summary_by_journal':list(amount_summary_by_journal.values()),
                'total_payment_amount':self.config_id.currency_id.round(total_payment_amount),
                'opening_cash_amount': self.cash_register_balance_start,
                'total_summary_amount': self.config_id.currency_id.round(total_payment_amount + self.cash_register_balance_start),
            }

    @api.model
    def get_session_report_data(self, kwargs):
        session = self.browse(kwargs['session_id'])
        report_data = session.wk_session_sale_details() or {}
        report_data['session_info'] = {
            'name':session.name,
            'responsible':session.user_id.name,
            'start_date':session.start_at or '',
            'opening_balance':session.cash_register_balance_start,
            'total_balance':session.cash_register_total_entry_encoding,
        }
        statement_data = []
        for statement in session.statement_ids:
            statement_details = {
                'name':statement.journal_id.name,
                'balance_start': statement.balance_start,
                'total_trans': statement.total_entry_encoding,
                'balance_end': statement.balance_end_real,
                'difference': statement.difference,
            }
            statement_data.append(statement_details)
        return report_data


class WkPosDetails(models.TransientModel):
    _name = 'wk.pos.details.wizard'

    def _wk_get_utc_time_(self,session_date):
        if session_date:
            session_date = datetime.strptime(session_date, "%Y/%m/%d %H:%M")
            tz_name = self._context.get('tz') or self.env.user.tz
            tz = tz_name and pytz.timezone(tz_name) or pytz.UTC
            return fields.Datetime.to_string(pytz.UTC.localize(session_date))
    
    def get_root_categ(self, pos_categ_id):
        if pos_categ_id.parent_id:
            return self.get_root_categ(pos_categ_id.parent_id)
        else:
            return pos_categ_id

    @api.model
    def get_report_data(self, kwargs):
        record = self.create(kwargs)
        result = record.get_pos_details()
        return result

    def get_pos_details(self):
        self.ensure_one()
        if self.start_date and self.config_id:
            orders = self.env['pos.order'].search([('config_id', '=', self.config_id.id), ('create_date', '>=', self.start_date), ('create_date', '<', self.end_date)])
            statements = self.env['account.bank.statement']
            products_sold = {}
            total_sale = 0.0
            total_discount = 0.0  
            discount_amount = 0.0          
            total_foc_discount = 0.0
            total_refund = 0.0
            total_sale_by_categ = {}
            amount_payment_journal = {}
            amount_summary_by_journal = {}
            total_payment_amount = 0.0
            total_tax = 0.0
            order_details = []
            session = set()
            opening = 0.0
            journal = ''

            for order in orders:
                total_tax += order.amount_tax
                if order.is_return_order:
                    total_refund += order.amount_total
                else:
                    for line in order.lines:
                        if line.discount and line.discount >0:
                            if line.discount <100:
                                discount = (line.price_subtotal_incl*100/(100-line.discount)) - line.price_subtotal_incl
                                total_discount += discount
                                discount_amount += discount
                            else:
                                taxes= line.tax_ids_after_fiscal_position.compute_all(line.price_unit, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id)
                                total_foc_discount += taxes['total_included']
                                total_discount += taxes['total_included']
                        if line.product_id == line.order_id.config_id.discount_product_id:
                            discount_amount += abs(line.price_unit)
                            total_discount += abs(line.price_unit)
                        if(line.product_id and line.product_id.pos_categ_id):
                            pos_categ_id = self.get_root_categ(line.product_id.pos_categ_id)
                            if(total_sale_by_categ.get(pos_categ_id.name)):
                                # total_sale_by_categ[pos_categ_id.name] += line.price_subtotal_incl
                                total_sale_by_categ[pos_categ_id.name] += line.price_unit * line.qty
                            else:
                                # total_sale_by_categ[pos_categ_id.name] = line.price_subtotal_incl
                                total_sale_by_categ[pos_categ_id.name] = line.price_unit * line.qty

                for statement in order.payment_ids:
                    total_payment_amount += statement.amount
                    if(amount_payment_journal.get(statement.payment_method_id.name)):
                        amount_payment_journal[statement.payment_method_id.name][1] += statement.amount
                    else:
                        amount_payment_journal[statement.payment_method_id.name] = [statement.payment_method_id.name, statement.amount]

                    if (amount_summary_by_journal.get(statement.payment_method_id.name)):
                        amount_summary_by_journal[statement.payment_method_id.name][1] += statement.amount
                    else:
                        amount_summary_by_journal[statement.payment_method_id.name] = [statement.payment_method_id.name, statement.amount]

                session.add(order.session_id.id)

            for statement in statements.search([('id', 'in', list(session))]):
                opening += statement.balance_start
            if orders:
                journal = orders.session_id.payment_method_ids.filtered('is_cash_count')[:1].name
            for k, v in amount_summary_by_journal.items():
                if k == journal:
                    amount_summary_by_journal[k][1] += opening

            total_sale = sum(total_sale_by_categ.values())
            return {
                'total_sale':self.config_id.currency_id.round(total_sale),
                'total_refund':self.config_id.currency_id.round(-1*total_refund),
                'total_discount':self.config_id.currency_id.round(total_discount),
                'discount_amount':self.config_id.currency_id.round(discount_amount),
                'total_foc_discount':self.config_id.currency_id.round(total_foc_discount),
                'total_tax':self.config_id.currency_id.round(total_tax),
                'net_sale': self.config_id.currency_id.round(total_sale - total_discount - (-1*total_refund)),
                'total_sale_by_categ':[(key,self.config_id.currency_id.round(value)) for key,value in total_sale_by_categ.items()],
                'amount_payment_journal': list(amount_payment_journal.values()),
                'amount_summary_by_journal':list(amount_summary_by_journal.values()),
                'total_payment_amount': self.config_id.currency_id.round(total_payment_amount),
                'opening_cash_amount': opening,
                'total_summary_amount': self.config_id.currency_id.round(total_payment_amount + opening),
            }

    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True, default=fields.Datetime.now)
    config_id = fields.Many2one('pos.config', 'POS Config')


class PosConfig(models.Model):
    _inherit = 'pos.config'

    wk_report_print_type = fields.Selection([('posbox', 'POSBOX(Xml Session Report)'),
                                        ('ticket', 'Pos Ticket (Session Receipt)'),
                                        ('pdf','Browser Based (Pdf Report)')
                                        ], default='ticket', required=True, string='Session Report Print Type')

    @api.constrains('wk_report_print_type','iface_print_via_proxy')
    def check_wk_report_print_type(self):
        self.ensure_one()
        if (self.wk_report_print_type == 'posbox'):
            if(self.iface_print_via_proxy == False):
                raise ValidationError("You can not print Xml Session Report unless you configure the Receipt Printer settings under Hardware Proxy/PosBox!!!")
