# -*- coding: utf-8 -*-
from openerp.osv import fields
from openerp.osv import osv

from tools.translate import _


class account_move_reversal(osv.osv_memory):

    _name = 'account.move.reversal'

    _columns = {
        'current_period': fields.boolean(_('Use Current Period')),
        'offset_period': fields.integer(_('Use Period Offset')),
        'period_id': fields.many2one('account.period', _('Specific Period')),
        'default_journal': fields.boolean(_('Use Default Journal')),
        'previous_journal': fields.boolean(_('Use Previous Journal')),
        'journal_id': fields.many2one('account.journal', _('Specific Journal')),
    }

    def create_reversals(sef, cr, uid, ids, context=None):
        print context['active_ids']


account_move_reversal()
