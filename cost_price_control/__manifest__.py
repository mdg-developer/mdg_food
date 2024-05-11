{
    'name': 'Cost Price Access Contrl',
    'version': '16.0.1.0.0',
    'author': '7th computing developer',
    'website': 'https://www.7thcomputing.com',
    'license': 'LGPL-3',
    'depends': ['base','product','stock_account'],
    'data': [
        'security/product_security.xml',
        'views/product_view.xml',
        'views/stock_valuation_layer_view.xml',
    ],
    'applications': True,
    "auto_install": False,
    'installable': True,
}