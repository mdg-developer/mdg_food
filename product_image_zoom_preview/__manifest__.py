# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': 'Image zoom preview in product page ',
    'version': '15.0.1.0',
    'summary': 'Image zoom preview in product page | website product zoom | zoom image | product image zoom | automatic zoom',
    'description': """
Image zoom preview in product page
Improvement in zoom image small issue.
=========================================================================
User can able to zoom the product image on website product page
    """,
    'license': 'OPL-1',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'category': 'Website/Website',
    'depends': ['website_sale','atharva_theme_base'],
    'data': [
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'product_image_zoom_preview/static/src/js/website_sale.js',
            'product_image_zoom_preview/static/src/lib/js/jquery.elevatezoom.js',
            'product_image_zoom_preview/static/src/css/styles.css',
        ],
        'web.assets_backend': [
            'product_image_zoom_preview/static/src/css/overlay.css',
        ]
    },
    'images': ['static/description/banner.jpg'],
    'sequence': 1,
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 20,
    'currency': 'EUR',
}
