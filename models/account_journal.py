from openerp.osv import osv, fields


class account_journal(osv.Model):
    _name = 'account.journal'
    _inherit = 'account.journal'

    _columns = {
        'is_not_reversable': fields.boolean(u"Reversal forbidden")
    }
