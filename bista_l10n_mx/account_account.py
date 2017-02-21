# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Authors: Openpyme (<http://openpyme.mx>)
#
#    Coded by: Salvador Martínez (chavamm.83@gmail.com)
#              Miguel Angel Villafuerte Ojeda (mikeshot@gmail.com)
#              Luis Felipe Lores (luisfqba@gmail.com)
#              Agustín Cruz Lozano (agustin.cruz@openpyme.mx)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields
from openerp.tools.translate import _


class account_account(osv.Model):
    _inherit = 'account.account'
    _columns = {
        'nature': fields.selection(
            [('D', 'Deudora'),
             ('A', 'Acreedora')
             ],
            string='Naturaleza',
            help=_('Express the account nature (Debitor or Creditor)')
        ),
        'sat_group_id': fields.many2one(
            'account.account.sat_group', string='SAT Group',
            ondelete='set null',
            help=_('Used for express the group code according to SAT catalog')
        ),
    }

#    def _check_account(self, cr, uid, ids, context=None):
        # Validates that view type account must have a SAT group defined
        # except for the account with code "0"
#        for account in self.browse(cr, uid, ids, context=context):
#            if not account.sat_group_id and \
#                account.type == "view" and \
#                    account.code != "0":
#                return False
#        return True

#    _constraints = [
#        (_check_account, 'Not defined a SAT group for the account!\n'
#            'A view type account must have a SAT group defined!',
#            ['sat_group_id']),
#    ]


class account_account_template(osv.Model):
    _inherit = 'account.account.template'
    _columns = {
        'nature': fields.selection(
            [('D', 'Deudora'),
             ('A', 'Acreedora')
             ],
            string='Naturaleza',
            help='Express the account nature (Debitor or Creditor)'
        ),
        'sat_group_id': fields.many2one(
            'account.account.sat_group', string='SAT Group',
            ondelete='set null',
            help='Used for express the group code according to SAT catalog'
        ),
    }

#    def _check_account(self, cr, uid, ids, context=None):
        # Validates that view type account must have a SAT group defined
        # except for the account with code "0"
#        for account in self.browse(cr, uid, ids, context=context):
#            if not account.sat_group_id and \
#                account.type == "view" and \
#                    account.code != "0":
#                return False
#        return True

#    _constraints = [
#        (_check_account, 'Not defined a SAT group for the account!\n'
#            'A view type account must have a SAT group defined!',
#            ['sat_group_id']),
#    ]
