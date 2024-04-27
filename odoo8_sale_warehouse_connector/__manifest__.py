{
    'name': 'Odoo8 Connector',
    'version': '1.0',
    'sequence': 14,
    'summary': 'Inventory Sync',
    'description': """
Odoo8 Connector
===========================
    """,
    'author': '7thcomputing developers',
    'website': 'http://7thcomputing.com',
    'depends': ['base','stock', 'stock_account','point_of_sale'],
    'data': [
            'security/ir.model.access.csv',
            'views/odoo8_connection_view.xml',
            #'views/product_template_view.xml',
    ],
    'demo': [],
    'installable': True,
}
