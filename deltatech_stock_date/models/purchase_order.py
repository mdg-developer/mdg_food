from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        self.picking_ids.write({
            'actual_date': self.date_order,
            'date_deadline': self.date_order,
            'scheduled_date': self.date_order,
            'date_done': self.date_order
        })
        return res

    @api.onchange('date_order')
    def onchange_date_order(self):
        if self.date_order:
            self.date_planned = self.date_order
            self.date_approve = self.date_order

    def button_approve(self, force=False):
        res = super().button_approve(force=force)
        self.date_approve = self.date_order
        return res