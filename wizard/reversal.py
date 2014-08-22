# -*- coding: utf-8 -*-
from openerp.osv import fields
from openerp.osv import osv

from tools.translate import _


def _browse(pool, cr, uid, ids, context=None):
    # common browse
    _iter = pool.browse(cr, uid, ids, context=context)
    # ensure iterator
    if not isinstance(ids, list):
        _iter = [_iter]
    # re-iter
    for record in _iter:
        yield record


def _create_reversals(model, cr, uid, context):
    # context check
    for key in ['active_ids', 'journal_id', 'period_id']:
        # ok
        if key in context: continue
        # ??
        raise osv.except_osv(_('Invalid Context!'),
                             _('Missing key: %s!') % key)
    # shortcut
    _move = model.pool.get('account.move')
    journal_id = context.pop('journal_id', None) # can be None if use previous
    period_id = context.pop('period_id')
    # create reversal
    for move in _move.browse(cr, uid, context['active_ids'], context=context):
        # journal factory
        _journal_id = journal_id or move.journal_id.id
        # reverse
        _move.reverse_move(cr, uid, move.id, _journal_id,
                           period_id, context=context)


class account_move_reversal_confirm(osv.osv_memory):

    _name = 'account.move.reversal.confirm'

    _columns = {
        'to_confirm_id': fields.many2many('account.move',
                                          string=_('Moves To Confirm')),
    }

    def confirm_reversals(self, cr, uid, ids, context=None):
        # check if as reversed moves to re-reverse
        if ids:
            # get memory item
            item = self.browse(cr, uid, ids[0], context=context)
            # update to reverse list
            context['active_ids'] += [move.id for move in item.to_confirm_id]
        # create reversals with context
        # ex.: {'journal_id': 0, 'period_id': 0, 'active_ids': [0]}
        _create_reversals(self, cr, uid, context)
        # close
        return {
            'type': 'ir.actions.act_window_close',
         }


class account_move_reversal_create(osv.osv_memory):

    _name = 'account.move.reversal.create'

    _columns = {
        'period_choice': fields.selection([
            ('current', _('Use Current Period')),
            ('offset', _('Enter a Period Offset')),
            ('specific', _('Choose a Specific Period')),
        ], _('Period Choice'), required=True),
        'period_offset': fields.integer(_('Period Offset')),
        'period_id': fields.many2one('account.period', _('Specific Period')),
        'journal_choice': fields.selection([
            ('default', _('Use Default Journal')),
            ('previous', _('Use Journal of the Move')),
            ('specific', _('Choose a Specific Journal')),
        ], _('Journal Choice'), required=True),
        'journal_id': fields.many2one('account.journal', _('Specific Journal')),
    }

    _defaults = {
        'period_offset': 0
    }

    @property
    def _move(self):
        return self.pool.get('account.move') 

    @property
    def _period(self):
        return self.pool.get('account.period') 

    @property
    def _settings(self):
        return self.pool.get('account.config.settings') 

    def _get_reversed_move_ids(self, cr, uid, ids, context=None):
        return self._move.search(cr, uid, [
            ('id', 'in', ids),
            ('reverseof_id', '!=', False)
        ])

    def _get_offset_period_id(self, cr, uid, offset=0, context=None):
        # shortcut
        _period = self._period
        # as in account addons
        _context = dict(context or {}, account_period_prefer_normal=True)
        period_ids = _period.find(cr, uid, context=_context) 
        # little check
        if not period_ids:
            raise osv.except_osv(
                _('Period Error!'),
                _('Current period not found!') % offset
            )
        # offset 0
        if not offset:
            return period_ids[0]
        # browse record required to get next
        period = _period.browse(cr, uid, period_ids[0], context=context)
        offset_period_id = _period.next(cr, uid, period, offset,
                                        context=context)
        # little check
        if not offset_period_id:
            raise osv.except_osv(
                _('Period Offset Error!'),
                _('Invalid period offset: %s!') % offset
            )
        return offset_period_id

    def _get_period_id(self, cr, uid, record, context=None):
        # current period
        if record.period_choice == 'current':
            return self._get_offset_period_id(cr, uid, context=context)
        # period offset
        elif record.period_choice == 'offset':
            return self._get_offset_period_id(cr, uid,
                                               offset=record.period_offset,
                                               context=context)
        # specific period
        elif record.period_choice == 'specific':
            return record.period_id.id
        # impossible
        else:
            raise osv.except_osv(
                _('Period Choice Error!'),
                _('%s unknown option!') % record.period_choice
            )

    def _get_default_journal_id(self, cr, uid, context=None):
        # shortcut
        _settings = self._settings
        # get current account settings id
        _settings_id = self._settings.search(cr, uid, [], context=context)
        # little check
        if not _settings_id:
            raise osv.except_osv(
                _('Account Settings Error!'),
                _('Account settings not initialized!'),
            )
        # shortcut
        field = 'journal_reversal_id'
        # get and return default journal reversal
        item = self._settings.read(cr, uid, _settings_id[0], [field])
        if not item\
        or not field in item:
            raise osv.except_osv(
                _('Journal Setting Error!'),
                _('No default journal for reversal in account settings!'),
            )
        # split obtained item, ex.: (26, u'Bank Journal - (test) (EUR)')
        _id, name = item[field]
        return _id

    def _get_journal_id(self, cr, uid, record, context=None):
        # default journal
        if record.journal_choice == 'default':
            return self._get_default_journal_id(cr, uid, context=context)
        # previous move
        elif record.journal_choice == 'previous':
            return None
        # specific journal
        elif record.journal_choice == 'specific':
            return record.journal_id.id
        # impossible
        else:
            raise osv.except_osv(
                _('Journal Choice Error!'),
                _('%s unknown option!') % record.journal_choice
            )
 
    def create_reversals(self, cr, uid, ids, context=None):
        # get current osv memory item
        record = self.browse(cr, uid, ids[0], context=context)
        # get the user expected period
        context['period_id'] = self._get_period_id(cr, uid, record,
                                                   context=context)
        # check period is open
        period = self._period.browse(cr, uid, context['period_id'])
        if period.state == 'done':
            raise osv.except_osv(
                _('Period Close Error!'),
                _('The selected period (%s) is closed!') % period.name
            )
        # get the user expected journal
        context['journal_id'] = self._get_journal_id(cr, uid, record,
                                                     context=context)
        # filter ids to confirm and update the context
        context['reversed_move_ids'] = self._get_reversed_move_ids(
            cr, uid, context['active_ids']
        )
        # if move already reversed just reverse and quit
        if not context['reversed_move_ids']:
            _create_reversals(self, cr, uid, context)
            # close the wizard
            return {
                'type': 'ir.actions.act_window_close',
             }
        # remove reversed ids from active ids
        for _id in context['reversed_move_ids']:
            context['active_ids'].remove(_id)
        # call confirm already reversed lines wizard
        return {
            'name': 'Confirm Moves Reversals',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.reversal.confirm',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'multi': 'True',
            'context': context,
        }
