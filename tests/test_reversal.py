# -*- coding: utf-8 -*-
import os
import time

from openerp.tools import convert_xml_import
from osv import osv

from openerp.tests.common import TransactionCase


ROOT = os.path.dirname(__file__)
DATA = os.path.join(ROOT, 'data.xml')

MODULE = 'account_move_reversal'


class TestReversal(TransactionCase):

    def setUp(self):
        super(TestReversal, self).setUp()
        # load xml data
        convert_xml_import(self.cr, MODULE, DATA, {}, 'update')

    def tearDown(self):
        self.cr.rollback()
 
    def _get_id(self, model, filter_):
        cr, uid = self.cr, self.uid
        res = model.search(cr, uid, filter_)
        return None if not res else res[0]

    @property
    def _journal(self):
        return self.registry('account.journal')

    @property
    def _period(self):
        return self.registry('account.period')

    @property
    def _move(self):
        return self.registry('account.move')

    @property
    def _move_line(self):
        return self.registry('account.move.line')

    @property
    def _reversal_create(self):
        return self.registry('account.move.reversal.create')

    @property
    def _settings(self):
        return self.pool.get('account.config.settings') 

    def _iter_move_ids(self):
        cr, uid = self.cr, self.uid
        for i in self._move.search(cr, uid, [('reverseof_id', '=', False)]):
            yield i    

    def _iter_moves(self):
        cr, uid = self.cr, self.uid
        # read move ids
        move_ids = [i for i in self._iter_move_ids()]
        # browse moves
        for move in self._move.browse(cr, uid, move_ids):
            yield move

    def _iter_moves_lines(self):
        cr, uid = self.cr, self.uid
        for move in self._iter_moves():
            for move_line in move.line_id:
                yield move_line

    def _get_next_move_line(self, move_line):
        cr, uid = self.cr, self.uid
        next_line_filter = [
            ('name', '=', '%s-reversed' % move_line.name),
            ('credit', '=', move_line.debit),
            ('debit', '=', move_line.credit)
        ]
        for next_line_id in self._move_line.search(cr, uid,
                                                        next_line_filter):
            yield self._move_line.browse(cr, uid, next_line_id)

    def _journal_id(self):
        cr, uid = self.cr, self.uid
        return self._get_id(self._journal, [
            ('code', '=', 'TBNK')
        ])

    def _period_id(self, month='01'):
        cr, uid = self.cr, self.uid
        return self._get_id(self._period, [
            ('code', 'like', month + '%')
        ])

    def test_reversed_lines(self):
        cr, uid = self.cr, self.uid
        journal_id = self._journal_id()
        period_id = self._period_id()
        # iter moves
        for move in self._iter_moves():
            reverse_move_id = self._move.reverse_move(cr, uid, move,
                                                      journal_id, period_id)
            reverse_move = self._move.browse(cr, uid, reverse_move_id)
            # check reversed move values
            self.assertEqual(reverse_move.journal_id.id, journal_id)
            self.assertEqual(reverse_move.period_id.id, period_id)
            self.assertEqual(reverse_move.state, 'draft')
            self.assertEqual(reverse_move.amount, move.amount)
        # iter moves lines
        for move_line in self._iter_moves_lines():
            next_move_line = [l for l in self._get_next_move_line(move_line)]
            self.assertEqual(len(next_move_line), 1)
            next_move_line = next_move_line[0]
            # check reversed moves lines
            self.assertEqual(next_move_line.quantity, move_line.quantity)
            self.assertEqual(next_move_line.product_id.id, move_line.product_id.id)
            self.assertEqual(next_move_line.account_id.id, move_line.account_id.id)
            self.assertEqual(next_move_line.statement_id.id, move_line.statement_id.id)
            self.assertEqual(next_move_line.amount_currency, move_line.amount_currency)
            self.assertEqual(next_move_line.currency_id.id, move_line.currency_id.id)
            self.assertEqual(next_move_line.journal_id.id, journal_id)
            self.assertEqual(next_move_line.period_id.id, period_id)
            self.assertEqual(next_move_line.blocked, move_line.blocked)
            self.assertEqual(next_move_line.partner_id.id, move_line.partner_id.id)
            # self.assertEqual(next_move_line.balance, 0.0) # !! not 0 ??
            self.assertEqual(next_move_line.state, move_line.state)
            self.assertEqual(next_move_line.invoice.id, move_line.invoice.id)
            self.assertEqual(next_move_line.tax_code_id.id, move_line.tax_code_id.id)
            self.assertEqual(next_move_line.tax_amount, move_line.tax_amount)
            self.assertEqual(next_move_line.account_tax_id.id, move_line.account_tax_id.id)
            self.assertEqual(next_move_line.analytic_account_id.id, move_line.analytic_account_id.id)
            self.assertEqual(next_move_line.company_id.id, move_line.company_id.id)

    def test_reversed_moves_refs(self):
        cr, uid = self.cr, self.uid
        journal_id = self._journal_id()
        period_id = self._period_id()
        # iter moves
        for move in self._iter_moves():
            self._move.write(cr, uid, [move.id], {'ref': 'test-move-ref'})
            reverse_move_id = self._move.reverse_move(cr, uid, move,
                                                      journal_id, period_id)
            reverse_move = self._move.browse(cr, uid, reverse_move_id)
            # check reversed moves
            self.assertEqual(reverse_move.ref, move.ref + '-reversed')

    def test_reversed_moves_no_refs(self):
        cr, uid = self.cr, self.uid
        journal_id = self._journal_id()
        period_id = self._period_id()
        # iter moves
        for _id in self._iter_move_ids():
            self._move.write(cr, uid, [_id], {'ref': False})
            move = self._move.browse(cr, uid, _id)
            reverse_move_id = self._move.reverse_move(cr, uid, move,
                                                        journal_id, period_id)
            reverse_move = self._move.browse(cr, uid, reverse_move_id)
            # check reversed moves
            self.assertFalse(reverse_move.ref)

    def test_reversed_moves_name(self):
        cr, uid = self.cr, self.uid
        journal_id = self._journal_id()
        period_id = self._period_id()
        # iter moves
        for _id in self._iter_move_ids():
            self._move.write(cr, uid, [_id], {'name': 'Move #%s' % _id})
            move = self._move.browse(cr, uid, _id)
            reverse_move_id = self._move.reverse_move(cr, uid, move,
                                                      journal_id, period_id)
            reverse_move = self._move.browse(cr, uid, reverse_move_id)
            # check reversed moves
            self.assertEqual(reverse_move.name, move.name + '-reversed')

    def test_wizard__get_reversed_moves(self):
        cr, uid = self.cr, self.uid
        # parent id for the test
        parent_id = self._get_id(self._move, [('ref', '=', 'move#1')])
        # child id for the test
        child_id = self._get_id(self._move, [('ref', '=', 'move#2')])
        # shortcut
        move_ids = [parent_id, child_id]
        # no reversed lines at start
        res = self._reversal_create._get_reversed_move_ids(cr, uid, move_ids)
        self.assertEqual(res, [])
        # add reversed link
        self._move.write(cr, uid, [child_id], {
            'reverseof_id': parent_id
        })
        # use wizard reversed moves method
        res = self._reversal_create._get_reversed_move_ids(cr, uid, move_ids)
        self.assertEqual(res, [child_id])

    def test_wizard__get_default_journal(self):
        cr, uid = self.cr, self.uid
        # bank journal
        bank_journal_id = self._journal_id()
        # get default journal
        journal_id = self._reversal_create._get_default_journal_id(cr, uid)
        # should be the same
        self.assertEqual(bank_journal_id, journal_id)

    def test_wizard__get_offset_period_id(self):
        cr, uid = self.cr, self.uid
        # current period
        period_id = self._period_id(month=time.strftime('%m'))
        # offset period id to test
        offset_period_id = self._reversal_create\
                               ._get_offset_period_id(cr, uid, offset=0)
        # check
        self.assertEqual(period_id, offset_period_id)
        # period +1
        period_plus_1_id =\
             self._period_id(month='%02d' % (int(time.strftime('%m')) + 1))
        # offset period id to test
        offset_period_id = self._reversal_create\
                               ._get_offset_period_id(cr, uid, offset=1)
        # check
        self.assertEqual(period_plus_1_id, offset_period_id)
        # period +1
        period_plus_2_id =\
             self._period_id(month='%02d' % (int(time.strftime('%m')) + 2))
        # offset period id to test
        offset_period_id = self._reversal_create\
                               ._get_offset_period_id(cr, uid, offset=2)
        # check
        self.assertEqual(period_plus_2_id, offset_period_id)
