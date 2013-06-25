# -*- coding: utf-8 -*-
import openerp

from osv import fields
from osv import osv

from tools.translate import _


class account_config_settings(osv.osv_memory):

    _inherit = 'account.config.settings'
    _name = 'account.config.settings'

    _columns ={
        'journal_reversal' : fields.many2one('account.journal',
                                             _('Default Reversal Journal'))
    }
