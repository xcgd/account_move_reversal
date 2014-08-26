# -*- coding: utf-8 -*-
from openerp.osv import fields
from openerp.osv import osv

from tools.translate import _

from post_function import call_post_function


class account_move_reversal_create(osv.osv_memory):

    _name = 'account.move.reversal.create'

    _columns = {
        'period_id': fields.many2one('account.period', _('Period')),
    }

    _defaults = {
        'period_offset': 0
    }

    def create_reversals(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)

        move_obj = self.pool['account.move']
        period_id = wizard.period_id.id

        for move in move_obj.browse(
            cr, uid, context['active_ids'], context=context
        ):

            move_obj.reverse_move(
                cr, uid, move.id, move.journal_id.id, period_id, context=context
            )

        # Call post functions set by caller
        call_post_function(cr, uid, context)

        return {'type': 'ir.actions.act_window_close'}
