from odoo import tools
from odoo import _, api, fields, models

class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    def _default_company_name(self):
        return self.env.company.name        

    company_name = fields.Char(string='Company Name', default=_default_company_name)
    estimate_arrival_date = fields.Date(string='Estimate Arrival Date')
    loss_claim = fields.Selection([('yes','Yes'), ('no','No')], string="Loss Claim (Yes/No)", default='no')
    loss_percent = fields.Char(string='Loss % (0.5 Above ??)')


