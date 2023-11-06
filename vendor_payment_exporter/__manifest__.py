{
    'name': 'Vendor Payment Exporter',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Manage vendor payments and export them to CSV/XLS',
    'description': """
        This module allows you to manage vendor payments in multiple currencies and export them to CSV or XLS files.
    """,
    'author': 'Tu Nombre',
    'depends': ['base', 'account'],
    'data': [
        'views/vendor_payment_views.xml',
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
