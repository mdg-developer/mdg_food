{
    'name': 'POS Member Type',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Add member types to POS and integrate with the loyalty program',
    'depends': ['point_of_sale', 'pos_loyalty'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_member.xml',
        'views/loyalty_program_view.xml',
        'views/res_partner_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos_member_templates.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_member_type/static/src/js/models.js',
            'pos_member_type/static/src/js/pos_member.js',
            'pos_member_type/static/src/js/ClientDetailsEdit.js',
        ],
        'web.assets_qweb': [
            'pos_member_type/static/src/xml/PartnerDetailsEdit.xml',
            'pos_member_type/static/src/xml/PartnerLine.xml',
            'pos_member_type/static/src/xml/PartnerListScreen.xml',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
