# -*- coding: utf-8 -*-
{
    'name': 'POS Session Report PDF',
    'summary': 'Allow to Print Current Session Report PDF',
    'description': """Module Developed for Session Report PDF.""",

    'author': 'iPredict IT Solutions Pvt. Ltd.',
    'website': 'http://ipredictitsolutions.com',
    "support": "ipredictitsolutions@gmail.com",

    'category': 'Point of Sale',
    'version': '15.0.0.1.0',
    'depends': ['point_of_sale'],

    'data': [
        'views/pos_config.xml',
        'report/report_pos_session.xml',
    ],

    'assets': {
        'web.assets_qweb': [
            'techno_pos_session_report/static/src/xml/**/*',
        ],
        'point_of_sale.assets': [
            'techno_pos_session_report/static/src/css/session_report.css',
            'techno_pos_session_report/static/src/js/session_report.js',
        ],
    },

    'license': "OPL-1",
    'price': 10,
    'currency': "EUR",

    "auto_install": False,
    "installable": True,

    'images': ['static/description/banner.png'],
    'pre_init_hook': 'pre_init_check',
}
