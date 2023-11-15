{
    'name': 'User Password by API',
    'version': '17.0',
    'summary': 'Create users with API generated password',
    'author': 'daniherzdeveloper',
    'category': 'Extra Tools',
    'auto_install': False,
    'sequence': 10,
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/ir_sequence.xml',
    ],
    'license': 'LGPL-3',
}
