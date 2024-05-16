# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Customer Note',
    'version': '1.0',
    'category': 'POS',
    'summary': 'POS Customer Note Edit',
    'description': """

This module allows you to modify POS Customer Note in the point of sale.

""",
    'depends': ['point_of_sale'
                ],
    'data': [
            'security/ir.model.access.csv',
            'wizard/customer_note_wizard.xml',
    ],

    'installable': True,
}
