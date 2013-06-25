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
