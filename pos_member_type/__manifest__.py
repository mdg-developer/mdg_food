{
    'name': 'POS Member Type',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Add member types to POS and integrate with the loyalty program',
    'depends': ['point_of_sale', 'pos_loyalty'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_member.xml',
        'views/res_partner_view.xml',
        'views/loyalty_program_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos_member_templates.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            # 'pos_member_type/static/src/js/models.js',
            # 'pos_member_type/static/src/js/Screens/PartnerListScreen/PartnerDetailsEdit.js',
            'pos_member_type/static/src/xml/Screens/PartnerListScreen/PartnerDetailsEdit.xml',
            'pos_member_type/static/src/xml/Screens/PartnerListScreen/PartnerLine.xml',
            'pos_member_type/static/src/xml/Screens/PartnerListScreen/PartnerListScreen.xml',
            # 'pos_member_type/static/src/js/Screens/ProductScreen/Loyalty.js',
        ]
    },
    'installable': True,
    'auto_install': False,
}
