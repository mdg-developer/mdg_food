from odoo import tools
from odoo import _, api, fields, models

class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    def _default_company_name(self):
        return self.env.company.name        

    company_name = fields.Char(string='Company Name', default=_default_company_name)
    estimate_arrival_date = fields.Date(string='Estimate Arrival Date')
    loss_claim = fields.Selection([('yes','Yes'), ('no','No')], string="Loss Claim (Yes/No)", default='no')
    loss_percent = fields.Char(string='Loss %')
    fesc_count = fields.Integer("FESC count", compute='_compute_fesc_count')

    def _compute_fesc_count(self):
        for rec in self:
            rec.fesc_count = 0
            fesc = rec.env['res.fesc'].search([('purchase_id','=',rec.id)])
            if fesc:
                rec.fesc_count = len(fesc)

    def open_fesc(self):
        """ FESC smart button action """
        return {
            'type': 'ir.actions.act_window',
            'name': _('FESC'),
            'res_model': 'res.fesc',
            'view_type': 'list',
            'view_mode': 'list',
            'views': [[False, 'list'], [False, 'form']],
            'domain': [('purchase_id', '=', self.id)],
        }


