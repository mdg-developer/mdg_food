from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    backdate = fields.Datetime(string='Back Date', readonly=True, required=True,
                               states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                               default=fields.Datetime.now)

    @api.onchange('backdate')
    def onchange_backdate(self):
        if self.backdate:
            self.date_order = self.backdate

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.picking_ids.write({
            'actual_date': self.backdate,
            'date_deadline': self.backdate,
            'scheduled_date': self.backdate,
            'date_done': self.backdate
        })

    def _prepare_confirmation_values(self):
        """ Prepare the sales order confirmation values.

        Note: self can contain multiple records.

        :return: Sales Order confirmation values
        :rtype: dict
        """
        return {
            'state': 'sale',
            # 'date_order': fields.Datetime.now()
        }


