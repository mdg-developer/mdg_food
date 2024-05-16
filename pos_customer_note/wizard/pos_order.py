from odoo import api, fields, models, SUPERUSER_ID, _


class CustomerNoteEdit(models.TransientModel):
    _name = "customer.note.wizard"

    order_id = fields.Many2one('pos.order', string='POS Order')
    sale_order_line_id = fields.Many2one('pos.order.line', string='Order Lines',domain="[('order_id','=',order_id)]")
    edit_note = fields.Char(string='Edit Customer Note')

    @api.onchange('sale_order_line_id')
    def _onchange_customer_note(self):
        if self.sale_order_line_id:
            self.edit_note = self.sale_order_line_id.customer_note
        else:
            self.edit_note = False

    def edit_confirm(self):
        self.sale_order_line_id.customer_note = self.edit_note


class PosOrder(models.Model):
    _inherit = "pos.order"

    def edit_form(self):
        view_id = self.env.ref('pos_customer_note.customer_note_edit_wizard').id
        return {
            'name': _('Edit Customer Note'),
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'customer.note.wizard',
            'context': {'default_order_id': self.id},
            'type': 'ir.actions.act_window',
            'target': 'new',
            'views': [[view_id, 'form']],
        }
