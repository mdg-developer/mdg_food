# -*- coding: utf-8 -*-
# ©  2015-2018 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Stock Date",
    'version': '12.0.1.0.0',
    "author": "Terrabit, Dorin Hongu",
    "website": "https://www.terrabit.ro",


    "category": "Warehouse",
    "depends": ["base", "stock","stock_account", "sale", "purchase"],
    "license": "LGPL-3",
    "data": ['views/stock_picking_view.xml',
             'wizard/stock_immediate_transfer_view.xml',
             'views/sale_order_view.xml',
             ],
    'application': False,
    "images": ['images/main_screenshot.png'],
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
