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

    def _create_reversed_move(self, cr, uid, move, next_journal_id,
                              next_period_id, context=None):
        """
        Creates reversed move record according passed move and next period id.

        Returns id of the new record.
        """
        return self.create(cr, uid, {
            'name': '/' if move.name == '/' else '%s-reversed' % move.name,
            'ref': False if not move.ref else '%s-reversed' % move.ref,
            'period_id': next_period_id,
            'journal_id': next_journal_id,
            'partner_id': move.partner_id.id,
            'narration': move.narration,
            'company_id': move.company_id.id,
            'reverseof_id': move.id,
        }, context=context)

    def _create_reversed_move_line(self, cr, uid, move_line, reversed_move_id,
                                   context=None):
        """
        Creates reversed move line for the passed move line and reversed move
        id.

        Returns id of the new record.
        """
        move_line_pool = self.pool.get('account.move.line')
        return move_line_pool.create(cr, uid, {
            'name': move_line.name + '-reversed',
            'quantity': move_line.quantity,
            'product_uom_id': move_line.product_uom_id.id,
            'product_id': move_line.product_id.id,
            'debit': move_line.credit,
            'credit': move_line.debit,
            'account_id': move_line.account_id.id,
            'move_id': reversed_move_id,
            'narration': move_line.narration,
            'ref': move_line.ref,
            'amount_currency': move_line.amount_currency,
            'currency_id': move_line.currency_id.id,
            'partner_id': move_line.partner_id.id,
            # 'date_maturity': move_line.date_maturitya, # TODO should we keep it??
            'tax_code_id': move_line.tax_code_id.id,
            'tax_amount': move_line.tax_amount,
            'invoice': move_line.invoice.id,
            'account_tax_id': move_line.account_tax_id.id,
            'analytic_account_id': move_line.analytic_account_id.id,
            'company_id': move_line.company_id.id,
        }, context=context)

    def reverse_move(self, cr, uid, move, next_journal_id, next_period_id,
                     context=None):
        # create next move
        reversed_move_id =\
            self._create_reversed_move(cr, uid, move, next_journal_id,
                                       next_period_id, context=context)
        # little check
        if not reversed_move_id:
            # error messge shortcut
            _msg = _('Can\'t create reversed move for move %s (%s)'
                     ' and next period id %s.')
            _msg = _msg % (move.name, move.id, next_period_id)
            # raise msg
            raise osv.except_osv(_('Reverse Move Error'), _msg)
        # create next lines
        for move_line in move.line_id:
            if self._create_reversed_move_line(cr, uid, move_line,
                                               reversed_move_id,
                                               context=context):
                # created do next
                continue
            # error messge shortcut
            _msg = _('Can\'t create reversed move line for move %s (%s)'
                     ' and next period id %s.')
            _msg = _msg % (move.name, move.id, next_period_id)
            # raise msg
            raise osv.except_osv(_('Reverse Move Line Error'), _msg)
        # returns the new created move
        return reversed_move_id
