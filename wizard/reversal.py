# -*- coding: utf-8 -*-
from collections import defaultdict

from openerp.osv import fields
from openerp.osv import osv

from openerp.tools.translate import _

from post_function import (
    call_post_function,
    call_post_err_function,
)


class account_move_reversal_create(osv.osv_memory):

    _name = 'account.move.reversal.create'

    _columns = {
        'date': fields.date(u"Reversal date", required=True),
    }

    def reconcile_moves(self, cr, uid, moves, context):
        aml_obj = self.pool['account.move.line']

        line_ids = defaultdict(list)

        # We regroup amls by account
        for move in moves:
            for line in move.line_id:
                line_ids[line.account_id.id].append(line.id)

        # we reconcile for each account
        for ids in line_ids.values():
            aml_obj.reconcile(cr, uid, ids, context=context)

    def _check_reconciliation(self, cr, uid, move, context):
        for line in move.line_id:
            if line.reconcile_partial_id or line.reconcile_id:
                return True
        return False

    def __create_reversals(self, cr, uid, ids, context):
        wizard = self.browse(cr, uid, ids[0], context=context)

        move_obj = self.pool['account.move']

        for move in move_obj.browse(
            cr, uid, context['active_ids'], context=context
        ):
            if self._check_reconciliation(cr, uid, move, context):
                raise osv.except_osv(
                    _(u"Error"),
                    _(u"One of the transaction of te journal is reconciled. "
                      u"Reversing the move is forbidden.")
                )

            reversed_move_id = move_obj.reverse_move(
                cr, uid, move.id,
                move.journal_id.id,
                wizard.date,
                context=context
            )
            reversed_move = move_obj.browse(
                cr, uid, [reversed_move_id], context
            )[0]
            self.reconcile_moves(cr, uid, [move, reversed_move], context)

        # Call post functions set by caller
        call_post_function(cr, uid, context)

        return {'type': 'ir.actions.act_window_close'}

    def create_reversals(self, cr, uid, ids, context=None):
        try:
            self.__create_reversals(cr, uid, ids, context)
        except Exception as e:
            call_post_err_function(cr, uid, context)
            raise e
