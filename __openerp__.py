# -*- coding: utf-8 -*-
{
    'name': 'Account Move Reversal',
    'version': '1.4',
    'category': 'XCG Consulting',
    'description': """
""",
    'author': 'XCG Consulting',
    # 'maintainer': '',
    'website': 'http://www.openerp-experts.net/',
    'depends': [
        'account_streamline',
    ],
    'data': [
        'account_move_reversal_view.xml',
        'account_journal.xml',
        'res_config_view.xml',
        'security/ir.model.access.csv',
        'wizard/account_move_reversal_wizard.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
