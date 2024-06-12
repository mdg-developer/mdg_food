from odoo import api, fields, models, tools, _

class PosConfig(models.Model):    
    _inherit = 'pos.config'
    
    stock_journal_id = fields.Many2one('account.journal', 'Stock Journal')