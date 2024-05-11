# -*- coding: utf-8 -*-
################################################################################
{
    'name': 'Customized POS Slip for Odooo 15',
    'version': '15.0.1.0.0',
    'category': 'Point of Sale',
    'summary': "Customized POS Customer Creation Screen",
    'description': "Odoo 15 POS",
    'author': 'MDG Developer',
    'company': 'Myanmar Distribution Group',
    'maintainer': 'Myanmar Distribution Group',
    'website': 'https://www.myanmardistributiongroup.com/',
    'depends': ['point_of_sale','contacts', 'web'],
    'data': [],
    'assets': {
        'point_of_sale.assets': [
            'pos_customer_creation/static/src/scss/pos.scss',
        ],
        'web.assets_qweb': [
            'pos_customer_creation/static/src/xml/pos.xml',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
