from collections import defaultdict
from datetime import timedelta
from itertools import groupby

from odoo import api, fields, models, _, Command

class PosSessionExt(models.Model):
    _inherit = 'pos.session'

    @api.model
    def _pos_ui_models_to_load(self):
        result = super(PosSessionExt, self)._pos_ui_models_to_load()
        result.append('pos.member.type')

        return result

    def _loader_params_pos_member_type(self):
        return {'search_params': {'domain': [], 'fields': ['name']}}

    def _get_pos_ui_pos_member_type(self, params):
        return self.env['pos.member.type'].search_read(**params['search_params'])

    def _loader_params_loyalty_program(self):
        return {
            'search_params': {
                'domain': [('id', 'in', self.config_id._get_program_ids().ids)],
                'fields': ['name', 'trigger', 'applies_on', 'program_type', 'date_to',
                    'limit_usage', 'max_usage', 'is_nominative', 'portal_visible', 'portal_point_name', 'trigger_product_ids','pos_member_type_id'],
            },
        }

    def _loader_params_res_partner(self):
        return {
            'search_params': {
                'domain': [],
                'fields': [
                    'name', 'street', 'city', 'state_id', 'country_id', 'vat', 'lang', 'phone', 'zip', 'mobile', 'email',
                    'barcode', 'write_date', 'property_account_position_id', 'property_product_pricelist', 'parent_name', 'birthday','pos_member_type_id'
                ],
            },
        }