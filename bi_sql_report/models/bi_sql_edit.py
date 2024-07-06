# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _

class BiSql(models.Model):
    _inherit = 'bi.sql.view'

    view_order = fields.Char(
        required=True,
        readonly=False,
        states={"ui_valid": [("readonly", True)]},
        default="tree,pivot,graph",
        help="Comma-separated text. Possible values:" ' "tree","graph" or "pivot"',
    )
