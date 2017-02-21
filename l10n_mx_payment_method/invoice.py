# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: isaac (isaac@vauxoo.com)
############################################################################
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
from openerp.osv import fields, osv


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,
                            date_invoice=False, payment_term=False,
                            partner_bank_id=False, company_id=False,
                            context=None):
        res =  super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id,
            date_invoice=date_invoice, payment_term=payment_term, 
            partner_bank_id=partner_bank_id, company_id=company_id, context=None)
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if user and user.company_id and not user.company_id.mexican_localization:
            return res
        pay_method_id = False
        if partner_id:
            partner_obj = self.pool.get('res.partner')
            partner = partner_obj.browse(cr, uid, partner_id)
            pay_method_id = partner and partner.pay_method_id and \
                partner.pay_method_id.id or False
        res['value']['pay_method_id'] = pay_method_id
        return res

    _columns = {
        'pay_method_id': fields.many2one('pay.method', 'Payment Method',
            readonly=True, states={'draft': [('readonly', False)]},
                help='Indicates the way it was paid or will be paid the invoice,\
                where the options could be: check, bank transfer, reservoir in \
                account bank, credit card, cash etc. If not know as will be \
                paid the invoice, leave empty and the XML show “Unidentified”.'),
        'acc_payment': fields.many2one('res.partner.bank', 'Account Number',
            readonly=True, states={'draft': [('readonly', False)]},
                help='Is the account with which the client pays the invoice, \
                if not know which account will used for pay leave empty and \
                the XML will show "“Unidentified”".'),
    }
