{
    'name': 'POS Receipt Cellar18',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Customize the POS receipt layout',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_receipt.xml',
    ],
    'data': [
            'report/pricetag_report.xml',
        ],
    'qweb': [
        'static/src/xml/pos_receipt.xml',
    ],
    'installable': True,
    'auto_install': False,
}
