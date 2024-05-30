from odoo import tools
from odoo import _, api, fields, models

class SaleReport(models.Model):
    _inherit = 'sale.report'

    drum_qty = fields.Float(string='Drum Qty')      
    
    def _select_additional_fields(self, fields):
        """Hook to return additional fields SQL specification for select part of the table query.

        :param dict fields: additional fields info provided by _query overrides (old API), prefer overriding
            _select_additional_fields instead.
        :returns: mapping field -> SQL computation of the field
        :rtype: dict
        """
        fields['drum_qty'] = ",CASE WHEN l.product_id IS NOT NULL THEN sum(l.drum_qty / u.factor * u2.factor) ELSE 0 END as drum_qty"
    
        return super()._select_additional_fields(fields)

    

