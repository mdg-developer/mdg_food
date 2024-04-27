{
    'name': 'POS Customer Form Customization',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Add birthday field in POS Customer screen',
    'author': '7th Computing',
    'website': 'https://www.7thcomputing.com',
    'depends': ['point_of_sale', 'contacts', 'web','pos_member_type'],
    'data': [
        'views/res_partner_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_customer_creation/static/src/xml/Screens/PartnerListScreen/pos.xml',
            'pos_customer_creation/static/src/scss/pos.scss',
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}