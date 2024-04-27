{
    'name': 'POS Promotion Date',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Add Pos Promotio From Date',
    'depends': ['point_of_sale', 'pos_loyalty'],
    'data': [
        'views/loyalty_program_view.xml',
    ],

    'installable': True,
    'auto_install': False,
}
