# -*- coding: utf-8 -*-
{
    'name': 'Account Move Reversal',
    'version': '0.1',
    'category': 'XCG Consulting',
    'description': """
""",
    'author': 'Florent Pigout <florent.pigout@gmail.com>',
    'maintainer': 'Florent Pigout <florent.pigout@gmail.com>',
    'website': 'http://www.xcg-consulting.fr/fr/services/openerp',
    'depends': [
        'account_accountant',
    ],
    'data': [
        'account_move_reversal_view.xml',
        'security/ir.model.access.csv',
        'wizard/account_move_reversal_wizard.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
