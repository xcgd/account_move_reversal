# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Move Reversal, for OpenERP
#    Copyright (C) 2013 XCG Consulting (http://odoo.consulting)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Account Move Reversal',
    'version': '1.5',
    'category': 'Accounting & Finance',
    'description': """
""",
    'author': 'XCG Consulting',
    # 'maintainer': '',
    'website': 'http://odoo.consulting/',
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
