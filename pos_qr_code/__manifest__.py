# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Point Of Sale Slip',
    'author': 'Odoo S.A',
    'category': 'Point Of sale Slip',
    'description': """
Point Of Sale Slip
    """,
    'license': 'LGPL-3',
    'depends': [
        'l10n_gcc_pos',
        'l10n_sa',
        'point_of_sale',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_qr_code/static/src/js/main.js',
            'pos_qr_code/static/src/js/pos_slip.js',
            'pos_qr_code/static/src/xml/OrderReceipt.xml',
        ]
    },
    'auto_install': True,
}
