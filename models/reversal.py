# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _

from datetime import datetime


class account_move_reversal(osv.Model):

    _inherit = 'account.move'

    _columns ={
        'reverseof_id' : fields.many2one(
            'account.move',
            _('Reverse Of Move')
        )
    }
     
    _defaults = {
        'reverseof_id': lambda *a: False,
    }

    def reverse_move(
        self, cr, uid, move_id, journal_id, period_id, context=None
    ):
        """ Create the reverse of 'move'.
        We only switch debit/credit,
        add '-canceled' after the name and reference,
        and change the date_maturity to today
        """

        move_obj = self.pool['account.move']

        move = move_obj.browse(cr, uid, move_id, context=context)

        # Specific changes for move

        vals = {
            'name': '/' if move.name == '/' else _('%s-canceled') % move.name,
            'ref': '' if not move.ref else _('%s-canceled') % move.ref,
            'period_id': period_id,
            'journal_id': journal_id,
            'partner_id': move.partner_id.id,
            'narration': move.narration,
            'company_id': move.company_id.id,
        }

        # Dynamically copy fields of move lines.

        move_line_fields = self.pool['account.move.line'].fields_get(
            cr, uid, context=context
        )

        vals['line_id'] = []

        # This tricky part just copy the fields from aml depending on the types
        # of the field. The types are mapped in the below enumeration

        fnct_types = {
            'many2one': lambda val: val.id,
            'one2many': lambda vals: [(6, 0, [v.id for v in vals])],
            'many2many': lambda vals: [(6, 0, [v.id for v in vals])],
            'default': lambda val: val,
        }
        for aml in move.line_id:
            new_line = {}
            for key in move_line_fields:
                # Call a function that will format the value depending on type
                new_line[key] = fnct_types.get(
                    move_line_fields[key]['type'],
                    fnct_types['default']
                )(getattr(aml, key))

            # Some specific changes
            new_line['name'] = aml.name + _('-canceled')
            new_line['debit'] = aml.credit
            new_line['credit'] = aml.debit
            new_line['amount_currency'] = -aml.amount_currency

            vals['line_id'].append((0, 0, new_line))

        reversed_move_id = self.create(cr, uid, vals, context=context)
        return reversed_move_id
