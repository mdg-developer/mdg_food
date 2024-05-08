# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import pytz
from odoo import fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class PosConfig(models.Model):
    _inherit = 'pos.config'

    iface_session_report = fields.Boolean(string='Session Report ')

class PosOrder(models.Model):
    _inherit = 'pos.order'

    is_return_order = fields.Boolean(string='Return Order')

    def refund(self):
        res = super(PosOrder, self).refund()
        self.env['pos.order'].search([('id', '=', res['res_id'])]).is_return_order = True
        return res

class PosSession(models.Model):
    _inherit = 'pos.session'

    def get_payment_details(self):
        orders = self.env['pos.order'].search([('session_id', '=', self.id)])
        payment_ids = self.env["pos.payment"].search([('pos_order_id', 'in', orders.ids)]).ids
        if payment_ids:
            self.env.cr.execute("""
                SELECT method.name, sum(amount) total
                FROM pos_payment AS payment,
                     pos_payment_method AS method
                WHERE payment.payment_method_id = method.id
                    AND payment.id IN %s
                GROUP BY method.name
            """, (tuple(payment_ids),))
            payments = self.env.cr.dictfetchall()
        else:
            payments = []
        return payments

    def get_session_detail(self):
        order_ids = self.env['pos.order'].search([('session_id', '=', self.id)])
        discount = 0.0
        taxes = 0.0
        total_sale = 0.0
        total_gross = 0.0
        total_return = 0.0
        products_sold = {}
        for order in order_ids:
            total_sale += order.amount_total
            currency = order.session_id.currency_id
            total_gross += order.amount_total
            for line in order.lines:
                if line.product_id.pos_categ_id.name:
                    if line.product_id.pos_categ_id.name in products_sold:
                        products_sold[line.product_id.pos_categ_id.name] += line.qty
                    else:
                        products_sold.update({
                            line.product_id.pos_categ_id.name: line.qty
                        })
                else:
                    if 'undefine' in products_sold:
                        products_sold['undefine'] += line.qty
                    else:
                        products_sold.update({
                                'undefine': line.qty
                                })
                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.compute_all(line.price_unit * (1 - (line.discount or 0.0) / 100.0), currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes += tax.get('amount', 0)
                if line.discount:
                    discount += (line.price_unit - (line.price_unit * (1 - (line.discount or 0.0) / 100.0))) * line.qty
                pos_discount_module = self.env['ir.module.module'].sudo().search([('name', '=', 'pos_discount')])
                if pos_discount_module.state == 'installed':
                    if self.config_id.iface_discount and line.product_id == self.config_id.discount_product_id:
                        discount += line.price_subtotal
            if order.is_return_order:
                total_return -= order.amount_total
        return {
            'total_sale': total_sale,
            'discount': discount,
            'tax': taxes,
            'products_sold': products_sold or False,
            'total_gross': total_gross - taxes + discount + total_return,
            'total_return': total_return

        }

    def get_current_datetime(self):
        if self.env.user.tz:
            tz = pytz.timezone(self.env.user.tz)
        else:
            tz = pytz.utc
        c_time = datetime.now(tz)
        hour_tz = int(str(c_time)[-5:][:2])
        min_tz = int(str(c_time)[-5:][3:])
        sign = str(c_time)[-6][:1]
        if sign == '+':
            date_time = datetime.now() + timedelta(hours=hour_tz, minutes=min_tz)
        if sign == '-':
            date_time = datetime.now() - timedelta(hours=hour_tz, minutes=min_tz)
        return date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def get_session_open_date(self):
        return self.start_at.strftime(DEFAULT_SERVER_DATE_FORMAT)

    def get_session_open_time(self):
        return self.start_at.strftime("%I:%M %p")
