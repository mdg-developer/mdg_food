{
    'name': 'Website Sale Extension',
    'category': 'Website',
    'summary': 'Website Sale Extensio',
    'author': 'MDG Developer',

    'version': '12.0.1.0.1',
    'license': 'AGPL-3',
    'depends': ['base','website_sale', 'theme_alan', 'website_sale_delivery', 'res_township'],
    'data': [
        'views/templates.xml',
    ],
    'assets' :  {
        'web.assets_frontend': [
            'website_sale_ext/static/src/js/website_sale.js',
            'website_sale_ext/static/src/css/website_sale.css'
    ]},
    'installable': True,
}
