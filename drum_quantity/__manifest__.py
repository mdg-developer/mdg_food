{
    'name': 'Drum Qty',
    'version': '1.0',
    'category': 'Sale',
    'summary': 'Add drum qty in sale order line',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'views/sale_order_view.xml',
        # 'views/account_move_view.xml'
    ],

    'installable': True,
    'auto_install': False,
}
