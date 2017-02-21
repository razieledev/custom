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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class sale_order(osv.osv):

    _inherit = "sale.order"

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        if context is None:
            context = {}
        ctx = dict(context)
        ctx.update({'default_company_id': order.company_id.id})
        # journal_id = self.pool['account.invoice'].default_get(cr, uid, ['journal_id'], context=ctx)['journal_id']
        journal_id = self.pool.get('account.journal').search(cr, uid, [('company_id', '=', order.company_id.id), ('type','=', 'sale')], context=context, limit=1)
        if isinstance(journal_id, (list, tuple)):
            journal_id = journal_id[0]
        if order.company_id.name == 'SMC Comp Inc (USA)' and order.partner_id.name == 'Productos Plasco SA de CV':
            account_id = order.company_id.partner_id.property_account_receivable.id
        else:
            account_id = order.partner_invoice_id.property_account_receivable.id
        if not journal_id:
            raise osv.except_osv(_('Error!'),
                _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
        invoice_vals = {
            'name': order.client_order_ref or '',
            'origin': order.name,
            'type': 'out_invoice',
            'reference': order.client_order_ref or order.name,
            'account_id': account_id,
            'partner_id': order.partner_invoice_id.id,
            'journal_id': journal_id,
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term': order.payment_term and order.payment_term.id or False,
            'fiscal_position': order.fiscal_position.id or order.partner_invoice_id.property_account_position.id,
            'date_invoice': ctx.get('date_invoice', False),
            'company_id': order.company_id.id,
            'user_id': order.user_id and order.user_id.id or False,
            'section_id' : order.section_id.id
        }

        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
        invoice_vals.update(self._inv_get(cr, uid, order, context=ctx))
        return invoice_vals
