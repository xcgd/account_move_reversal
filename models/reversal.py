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
        self, cr, uid, move, journal_id, period_id, context=None
    ):
        """ Create the reverse of 'move'.
        We only switch debit/credit,
        add '-canceled' after the name and reference,
        and change the date_maturity to today
        """

        vals = {
            'name': '/' if move.name == '/' else '%s-canceled' % move.name,
            'ref': '' if not move.ref else '%s-canceled' % move.ref,
            'period_id': period_id,
            'journal_id': journal_id,
            'partner_id': move.partner_id.id,
            'narration': move.narration,
            'company_id': move.company_id.id,
            'reverseof_id': move.id,
        }
        vals['line_id'] = [(0, 0, {
            'name': aml.name + '-canceled',
            'quantity': aml.quantity,
            'product_uom_id': aml.product_uom_id.id,
            'product_id': aml.product_id.id,
            'debit': aml.credit,
            'credit': aml.debit,
            'account_id': aml.account_id.id,
            'move_id': reversed_move_id,
            'narration': aml.narration,
            'ref': aml.ref,
            'amount_currency': aml.amount_currency,
            'currency_id': aml.currency_id.id,
            'partner_id': aml.partner_id.id,
            'date_maturity': datetime.now(),
            'tax_code_id': aml.tax_code_id.id,
            'tax_amount': aml.tax_amount,
            'invoice': aml.invoice.id,
            'account_tax_id': aml.account_tax_id.id,
            'analytic_account_id': aml.analytic_account_id.id,
            'company_id': aml.company_id.id,
        }) for aml in move.line_id]
        self.create(cr, uid, vals, context=context)
        return reversed_move_id
