# ©  2015-2020 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from collections import defaultdict

from odoo import _, api, Command, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.tools.misc import clean_context, OrderedSet, groupby
from odoo.tools.float_utils import float_round, float_is_zero


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _apply_inventory(self):
        move_vals = []
        if not self.user_has_groups('stock.group_stock_manager'):
            raise UserError(_('Only a stock manager can validate an inventory adjustment.'))
        for quant in self:
            # Create and validate a move so that the quant matches its `inventory_quantity`.
            if float_compare(quant.inventory_diff_quantity, 0, precision_rounding=quant.product_uom_id.rounding) > 0:

                move_vals.append(quant._get_inventory_move_values(quant.inventory_diff_quantity,
                                                                  quant.product_id.with_company(
                                                                      quant.company_id).property_stock_inventory,
                                                                  quant.location_id))

            else:

                move_vals.append(quant._get_inventory_move_values(-quant.inventory_diff_quantity,
                                                                  quant.location_id,
                                                                  quant.product_id.with_company(
                                                                      quant.company_id).property_stock_inventory,
                                                                  out=True))
        use_date = quant.accounting_date or fields.Date.today()
        moves = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
        moves.with_context(force_period_date=use_date)._action_done()
        self.location_id.write({'last_inventory_date': fields.Date.today()})
        date_by_location = {loc: loc._get_next_inventory_date() for loc in self.mapped('location_id')}
        for quant in self:
            quant.inventory_date = date_by_location[quant.location_id]
        self.write({'inventory_quantity': 0, 'user_id': False})
        self.write({'inventory_diff_quantity': 0})

    @api.model
    def _update_available_quantity(
            self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, in_date=None
    ):
        res = super(StockQuant, self)._update_available_quantity(
            product_id, location_id, quantity, lot_id, package_id, owner_id, in_date
        )

        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        for x in res:
            x.write({
                'date_deadline': x.picking_id.actual_date
            })
            stock_valuation_layer_id = self.env['stock.valuation.layer'].search([('stock_move_id', '=', x.id)], limit=1)
            if stock_valuation_layer_id:
                self.env.cr.execute("update stock_valuation_layer set create_date=%s where id=%s", (x.date,stock_valuation_layer_id.id,))
        return res



    def write(self, vals):
        date_fields = {"date"}
        use_date = self.env.context.get("force_period_date", False)
        if date_fields.intersection(vals):
            if not use_date:
                for move in self:
                    today = fields.Date.today()
                    if "date" in vals:
                        move.move_line_ids.write({'date': vals['date']})
            else:
                if 'date' in vals:
                    vals['date'] = use_date
                for move in self:
                    move.move_line_ids.write({'date': vals['date']})

        return super(StockMove, self).write(vals)

    def _get_price_unit(self):
        """ Returns the unit price for the move"""
        print('get_price_Unit ext')
        self.ensure_one()
        # if self._should_ignore_pol_price():
        #     return super(StockMove, self)._get_price_unit()
        price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
        line = self.purchase_line_id
        order = line.order_id
        received_qty = line.qty_received
        if self.state == 'done' and line:
            received_qty -= self.product_uom._compute_quantity(self.quantity_done, line.product_uom, rounding_method='HALF-UP')
        if line:
            precision_rounding = line.product_uom.rounding
        else:
            precision_rounding = 0.0
        if float_compare(line.qty_invoiced, received_qty, precision_rounding) > 0:
            move_layer = line.move_ids.sudo().stock_valuation_layer_ids
            invoiced_layer = line.sudo().invoice_lines.stock_valuation_layer_ids
            # value on valuation layer is in company's currency, while value on invoice line is in order's currency
            receipt_value = 0
            if move_layer:
                receipt_value += sum(move_layer.mapped(lambda l: l.currency_id._convert(
                    l.value, order.currency_id, order.company_id, l.create_date, round=False)))
            if invoiced_layer:
                receipt_value += sum(invoiced_layer.mapped(lambda l: l.currency_id._convert(
                    l.value, order.currency_id, order.company_id, l.create_date, round=False)))
            invoiced_value = 0
            invoiced_qty = 0
            for invoice_line in line.sudo().invoice_lines:
                if invoice_line.tax_ids:
                    invoiced_value += invoice_line.tax_ids.with_context(round=False).compute_all(
                        invoice_line.price_unit, currency=invoice_line.currency_id, quantity=invoice_line.quantity)['total_void']
                else:
                    invoiced_value += invoice_line.price_unit * invoice_line.quantity
                invoiced_qty += invoice_line.product_uom_id._compute_quantity(invoice_line.quantity, line.product_id.uom_id)
            # TODO currency check
            remaining_value = invoiced_value - receipt_value
            # TODO qty_received in product uom
            remaining_qty = invoiced_qty - line.product_uom._compute_quantity(received_qty, line.product_id.uom_id)
            price_unit = float_round(remaining_value / remaining_qty, precision_digits=price_unit_prec)
        else:
            # price_unit = line._get_gross_price_unit()
            price_unit = line.price_unit
        if order.currency_id != order.company_id.currency_id:
            # The date must be today, and not the date of the move since the move move is still
            # in assigned state. However, the move date is the scheduled date until move is
            # done, then date of actual move processing. See:
            # https://github.com/odoo/odoo/blob/2f789b6863407e63f90b3a2d4cc3be09815f7002/addons/stock/models/stock_move.py#L36
            price_unit = order.currency_id._convert(
                price_unit, order.company_id.currency_id, order.company_id, self.picking_id.actual_date, round=False)
        return price_unit


class StockPicking(models.Model):
    _inherit = "stock.picking"

    actual_date = fields.Datetime(
        'Actual Date',
        default=fields.Datetime.now, index=True, track_visibility='onchange',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    def action_toggle_is_locked(self):
        # se suprascrie metoda standard petnru a nu mai permite editarea
        return False

    def _action_done(self):
        super(StockPicking, self)._action_done()
        use_date = self.env.context.get("force_period_date", False)
        if use_date:
            self.write({"date": use_date, "date_done": use_date})
            # self.move_lines.write({"date": use_date})  # 'date_expected': use_date,
            self.move_line_ids.write({"date": use_date})

    def button_validate(self):
        res = super(StockPicking, self).button_validate()

        if res:
            for rec in self:
                if rec.move_ids_without_package:
                    for move in rec.move_ids_without_package:
                        move.write({
                            'date': rec.actual_date
                        })
                if rec.move_line_ids:
                    for move_line in rec.move_line_ids:
                        move_line.write({
                            'date': rec.actual_date
                        })
                rec.write({'date_done': rec.actual_date})
        return res
