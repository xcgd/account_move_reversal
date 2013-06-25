# -*- coding: utf-8 -*-
from openerp.osv import fields
from openerp.osv import osv

from tools.translate import _


def _create_reversals(model, cr, uid, ids, context=context):
    pass



class account_move_reversal_confirm(osv.osv_memory):

    _name = 'account.move.reversal.confirm'

    _columns = {
        'to_confirm_id': fields.many2many('account.move',
                                          string=_('Moves To Confirm')),
    }

    def confirm_reversals(sef, cr, uid, ids, context=None):
        return {
            'type': 'ir.actions.act_window_close',
         }

account_move_reversal_confirm()


class account_move_reversal_create(osv.osv_memory):

    _name = 'account.move.reversal.create'

    _columns = {
        'period_choice': fields.selection([
            ('current', _('Use Current Period')),
            ('offset', _('Enter a Period Offset')),
            ('specific', _('Choose a Specific Period')),
        ], _('Period Choice')),
        'period_offset': fields.integer(_('Period Offset')),
        'period_id': fields.many2one('account.period', _('Specific Period')),
        'journal_choice': fields.selection([
            ('default', _('Use Default Journal')),
            ('previous', _('Use Journal of the Move')),
            ('specific', _('Choose a Specific Journal')),
        ], _('Journal Choice')),
        'journal_id': fields.many2one('account.journal', _('Specific Journal')),
    }

    def create_reversals(sef, cr, uid, ids, context=None):
        context['to_confirm_id'] = context['active_ids']
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

account_move_reversal_create()
