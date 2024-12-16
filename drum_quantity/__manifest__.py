{
    'name': 'Drum Qty',
    'version': '1.0',
    'category': 'Sale',
    'summary': 'Add drum qty in sale order line',
    'depends': ['base', 'sale', 'account', 'stock', 'purchase', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
        'views/driver_view.xml',
        'views/stock_picking_view.xml',
        'views/purchase_order_view.xml',
        'report/delivery_order_template.xml',
        'report/issue_detail_report_view.xml'
    ],

    'installable': True,
    'auto_install': False,
}
