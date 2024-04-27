from collections import defaultdict
from datetime import timedelta
from itertools import groupby

from odoo import api, fields, models, _, Command

class PosSession(models.Model):
    _inherit = 'pos.session'

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