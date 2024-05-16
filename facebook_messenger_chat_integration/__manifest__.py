# -*- coding: utf-8 -*-
{
    'name': "Facebook Messenger Chat Integration",

    'summary': """Facebook Messenger: One more way to communicate with your customers""",

    'description': """The Facebook Messenger Customer Chat Integration plugin allows you to integrate Messenger 
    directly into your business website. Customers can interact with your business at any time with the same 
    personalized experience they get in Messenger.""",

    'author': 'ErpMstar Solutions',
    'category': 'Website',
    'version': '1.0',


    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'price': 9,
    'currency': 'EUR',
    'installable': True,
}
