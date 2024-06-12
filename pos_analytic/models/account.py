from odoo import api, fields, models, _, tools

class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')
    
