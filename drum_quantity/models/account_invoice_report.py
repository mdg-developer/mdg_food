
from odoo import _, api, fields, models

class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    drum_qty = fields.Float(string='Drum Qty')

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", line.drum_qty as drum_qty"

    

