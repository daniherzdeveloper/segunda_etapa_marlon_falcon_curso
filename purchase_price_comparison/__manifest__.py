{
    'name': 'Purchase Price Comparison',
    'version': '17.0',
    'summary': 'Purchase Price Comparison',
    'category': 'Extra Tools',
    'author': 'daniherzdeveloper',
    'auto_install': False,
    'sequence': 10,
    'depends': ['base', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/cron.xml',
        'data/ir_sequence.xml',
        'views/purchase_price_comparison_view.xml',
    ],
    'license': 'LGPL-3',
}
