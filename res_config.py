# -*- coding: utf-8 -*-
from openerp.osv import fields, osv

from tools.translate import _


class account_config_settings(osv.osv_memory):

    _inherit = 'account.config.settings'
    _name = 'account.config.settings'

    _columns = {
        'journal_reversal_id': fields.many2one(
            'account.journal', _('Default Reversal Journal')
        )
    }
