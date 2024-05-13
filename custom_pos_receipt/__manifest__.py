# -*- coding: utf-8 -*-
################################################################################
{
    'name': 'Customized POS Slip for Odooo 15',
    'version': '15.0.1.0.0',
    'category': 'Point of Sale',
    'summary': "POS Customization",
    'description': "Odoo 15 POS",
    'author': 'MDG Developer',
    'company': 'Myanmar Distribution Group',
    'maintainer': 'Myanmar Distribution Group',
    'website': 'https://www.myanmardistributiongroup.com/',
    'depends': ['point_of_sale'],
    'data': [
        'views/res_partner_inherit_view.xml'],
    'assets': {
        'point_of_sale.assets': [
            'custom_pos_receipt/static/src/js/Receipt.js',
            # 'custom_pos_receipt/static/src/js/main.js'
        ],
        'web.assets_qweb': [
            'custom_pos_receipt/static/src/xml/Receipt.xml',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
