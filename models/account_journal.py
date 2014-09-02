from openerp.osv import osv, fields
from openerp.tools.translate import _


class account_journal(osv.Model):
    _name = 'account.journal'
    _inherit = 'account.journal'

    _columns = {
        'is_reversable': fields.boolean(u"Is Reversable")
    }
