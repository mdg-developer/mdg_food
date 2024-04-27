{
    'name'      : """Stock Inventory Report""",
    'summary'   : """Allows group by warehouse in inventory report"""
               """ Add the warehouse in inventory report.""",
    'category'  : "Inventory",
    'version'   : "13.0.1.1",
    'author'    : "Nisu Company",
    'website'   : "https://nisu.consulting",
    'depends'   : [
                'stock', 'stock_account',
                ],
    'data'      : [
                'views/stock_inventory_views.xml',
                'security/ir.model.access.csv',
                'security/inventory_report_security.xml',
                'wizard/inventory_wizard.xml',
                'inventory_report.xml',
                'views/inventory_report_by_warehouse.xml',
                'views/inventory_report_by_category.xml'
                ],
    'development_status': 'Production/Stable',
    'maintainers': [],
}
