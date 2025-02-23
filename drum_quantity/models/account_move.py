from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _default_company_name(self):
        return self.env.company.name        

    company_name = fields.Char(string='Company Name', default=_default_company_name)
    picking_id = fields.Many2one( comodel_name="stock.picking",string="DO Number", domain="[('partner_id', '=', partner_id)]")
    print_count = fields.Integer('Print Count', default=2)

    def invoice_print_action(self):
        return self.env.ref('drum_quantity.invoice_print').report_action(self)

    def action_post(self):
        """ Customize sequence for invoice """
        if self.move_type == 'out_invoice':
            self.name = self.env['ir.sequence'].next_by_code('invoice.sequence')
            self.payment_reference = self.name
        return super(AccountMove, self).action_post()

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    drum_qty = fields.Float(string='Drum Qty')

    @api.onchange('drum_qty')
    def onchange_drum_qty(self):
        if self.env.company.name =='ECOHARMONY COMPANY LIMITED':
            param_id = self.env['ir.config_parameter'].search([('key','=','drum_ratio')])
            if param_id and param_id.value:
                self.quantity = self.drum_qty * int(param_id.value)
            else:
                self.quantity = 0
        else:
            self.quantity = 0

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _default_company_name(self):
        return self.env.company.name  
        
    remark = fields.Char(string='Remark')
    company_name = fields.Char(string='Company Name', default=_default_company_name)

    def payment_print_action(self):
        return self.env.ref('drum_quantity.payment_print').report_action(self)