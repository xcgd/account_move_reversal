# -*- coding: utf-8 -*-
import openerp

from osv import fields
from osv import osv

from tools.translate import _


class account_move(osv.osv):

    _inherit = 'account.move'

    _columns ={
        'reverseof_id' : fields.many2one('account.move', _('Reverse Of Move'))
    }

    _defaults = {
        'reverseof_id': False,
    }

    def _browse(self, pool, cr, uid, ids, context=None):
        # common browse
        _iter = pool.browse(cr, uid, ids, context=context)
        # ensure iterator
        if not isinstance(ids, list):
            _iter = [_iter]
        # re-iter
        for record in _iter:
            yield record

    def post(self, cr, uid, ids, context=None):
        """
        Iters ids to reverse and do reverse if it should be. Raise osv
        exception to brake the post action in case of error.
        """
        """
        move_records = self._browse(self, cr, uid, ids, context=context)
        for move in move_records:
            # check if is already has a parent then ask user to confirm
        """
        # everything is ok
        return super(account_move, self).post(cr, uid, ids, context=context)

account_move()
