from odoo import models

class PosSessionExt(models.Model):
    _inherit = 'pos.session'

    def _loader_params_loyalty_program(self):
        return {
            'search_params': {
                'domain': [('id', 'in', self.config_id._get_program_ids().ids)],
                'fields': ['name', 'trigger', 'applies_on', 'program_type', 'date_to', 'date_from',
                           'limit_usage', 'max_usage', 'is_nominative', 'portal_visible', 'portal_point_name',
                           'trigger_product_ids', 'pos_member_type_id'],
            },
        }