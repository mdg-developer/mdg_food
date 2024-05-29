{
    'name': 'res_township',
    'version': '1.0',
    'sequence': 14,
    'summary': 'Township',
    'description': """
Manage Township part of state
======================================
With this module for township.
    """,
    'author': 'MDG developers',
    'website': 'https://www.odoo.com/page/crm',
    'depends': ['base',
                'sale',
                
                ],
    'data' : [
        'security/ir.model.access.csv',
        'views/res_township_view.xml',
        'views/res_city_view.xml',
        'views/res_partner_view.xml',
    ],
    'demo': [],
    'installable': True,
}
