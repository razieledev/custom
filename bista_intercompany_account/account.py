# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import logging
import openerp
from openerp import SUPERUSER_ID, api
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class account_period(osv.osv):

    _inherit = "account.period"

    @api.returns('self')
    def find(self, cr, uid, dt=None, context=None):
        if context is None: context = {}
        if not dt:
            dt = fields.date.context_today(self, cr, uid, context=context)
        args = [('date_start', '<=' ,dt), ('date_stop', '>=', dt)]
        if context.get('import_comp', False):
            args.append(('company_id', '=', context['import_comp']))
        elif context.get('company_id', False):
            args.append(('company_id', '=', context['company_id']))
        else:
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
            args.append(('company_id', '=', company_id))
        result = []
        if context.get('account_period_prefer_normal', True):
            # look for non-special periods first, and fallback to all if no result is found
            result = self.search(cr, uid, args + [('special', '=', False)], context=context)
        if not result:
            result = self.search(cr, uid, args, context=context)
        if not result:
            model, action_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'account', 'action_account_period')
            msg = _('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.') % dt
            raise openerp.exceptions.RedirectWarning(msg, action_id, _('Go to the configuration panel'))
        return result

