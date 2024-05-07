# -*- coding: utf-8 -*-

{
    'name': 'POS Session Report',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Webveer',
    'summary': 'This module allows you to print current session report by thermal printer',
    'description': """

=======================

This module allows you to print current session report by thermal printer

""",
    'depends': ['point_of_sale'],
    'data': [
        'views/views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_session_report/static/src/js/pos.js',
        ],
        'web.assets_qweb': [
            'pos_session_report/static/src/xml/**/*',
        ],
    },
    'images': [
        'static/description/report.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 25,
    'currency': 'EUR',
}
