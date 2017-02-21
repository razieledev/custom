# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tools.translate import _
from openerp.osv import osv
import datetime
from dateutil.relativedelta import relativedelta
from openerp import api
from openerp import models, fields
import logging
_logger = logging.getLogger(__name__)


class generate_monthly_invoice(models.TransientModel):
    _name = 'generate.monthly.invoice'
    _description = 'Generate Monthly Invoice'
    
    @api.model
    def _get_years(self):
        return [(str(year), year) for year in range(2010,3000)]
    
    partner_id = fields.Many2one('res.partner', string = "Supplier")
    picking_type_id = fields.Many2one('stock.picking.type', string = "Picking Type")
    product_categ_id = fields.Many2one('product.category', string = "Product Category")
    journal_id = fields.Many2one('account.journal', string = 'Destination Journal', required=True)
    invoice_date = fields.Datetime(string = 'Invoice Date', default = datetime.datetime.now())
    month = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'Octomber'),
        ('11', 'November'),
        ('12', 'December'),
        ],
        'Month', required=True,)
    year = fields.Selection(_get_years, string = 'Year', required=True, default = '2015')
    
    company_id = fields.Many2one('res.company', string = 'Company', required=True,     
                default = lambda self: self.env['res.company']._company_default_get('generate.monthly.invoice'))
        
    inv_type = fields.Selection([('in_invoice', 'In Invoice'), ('out_invoice', 'Out Invoice')], default = 'out_invoice', string = 'Invoice Type')

    
    def get_moves_product_categ(self, move):
        ''' 
        Returns True when category of product is equal to the category selected in wizard.
        '''
        if move.product_id and (move.product_id.categ_id.id == self.product_categ_id.id):
            return True
        else:
            return False
    
    
    @api.multi
    def generate_invoice(self):
        for wiz in self:
            if not (wiz.month and wiz.year):
                raise  osv.except_osv(_('Warning!'),_('Please select Year and Month!'))
            if not wiz.partner_id:
                raise  osv.except_osv(_('Warning!'),_('No Supplier is selected , Please select one !'))

    #           Keeping start date as 1 by default
            start_datetime = datetime.datetime(eval(self.year), eval(self.month), 1, 0, 0)
            end_datetime = start_datetime + relativedelta(months = 1, days = -1, hour = 23, minute = 59)
            print "start and end datetim", start_datetime, end_datetime
            moves = self.env['stock.move'].search([('create_date', '>=', start_datetime.strftime('%Y-%m-%d %H:%M:%S')), 
                                ('create_date', '<=', end_datetime.strftime('%Y-%m-%d %H:%M:%S')),  
                                ('picking_type_id', '=', self.picking_type_id.id), ('state', '=', 'done')])
    #           Filter the moves having product of category eg.International raw materials
            filtered_moves = moves.filtered(self.get_moves_product_categ) if moves else False
            if not filtered_moves:
                raise  osv.except_osv(_('Warning!'),_('There are no moves with this Product Category to be invoiced'))
            
            filtered_products = filtered_moves.mapped('product_id') if filtered_moves else False
            filtered_lots = filtered_moves.mapped('lot_ids') if filtered_moves else False
            if not filtered_lots:
                raise  osv.except_osv(_('Warning!'),_('There are no Lots defined in the moves.'))
            final_move_dict = {}
            # grouping moves with respect to lot and products ,calculating total uom qty and bringing required fields to create invoice line
            for lot in filtered_lots:
                final_move_dict[lot.id] = {'moves': [], 'product_uom_qty': 0.0}
#                for product in filtered_products:
                for move in filtered_moves:
                    if lot.id in [lot_brw.id for lot_brw in move.lot_ids]:
                        final_move_dict[lot.id]['moves'].append(move)
                        final_move_dict[lot.id]['product_uom_qty'] += move.product_uom_qty
                        final_move_dict[lot.id]['product_uom'] = move.product_uom
                        final_move_dict[lot.id]['product_uos'] = move.product_uos
                        final_move_dict[lot.id]['product_uos_qty'] = move.product_uos_qty
                        final_move_dict[lot.id]['product_id'] = move.product_id 
#            ln_moves = 0
#            for key, val in final_move_dict.items():
#                ln_moves += len(val['moves'])
#            print "total filtered moves == len(actual moves searched)", ln_moves, len(filtered_moves) 
            invoice_id = self.env['account.invoice'].create(self._get_invoice_vals(filtered_moves, inv_type = self.inv_type))
            for lot, line in final_move_dict.items():
                inv_line_vals = self._get_invoice_line_vals(lot, line, self.partner_id, inv_type = self.inv_type)
                inv_line_vals['invoice_id'] = invoice_id.id
                self._create_invoice_line_from_vals(inv_line_vals)

            self.pool.get('account.invoice').button_compute(self.env.cr, self.env.uid, invoice_id.id, context=self.env.context, set_total=(True))
                
        return True
        
        
        
     ############################# INVOICE LINES'#####
#     to create vals following are send in move product_id, product_uom, product_uom_qty, product_uos, product_uos_qty
    @api.model
    def _create_invoice_line_from_vals(self, invoice_line_vals):
       return self.env['account.invoice.line'].create(invoice_line_vals)
    
    @api.model
    def _get_invoice_line_vals(self, lot_id, move, partner, inv_type = 'in_invoice'):
        fp_obj = self.pool.get('account.fiscal.position')
        lot = self.env['stock.production.lot'].browse(lot_id)
        # Get account_id
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = move.get('product_id').property_account_income.id
            if not account_id:
                account_id = move.get('product_id').categ_id.property_account_income_categ.id
        else:
            account_id = move.get('product_id').property_account_expense.id
            if not account_id:
                account_id = move.get('product_id').categ_id.property_account_expense_categ.id
        fiscal_position = partner.property_account_position
        account_id = fp_obj.map_account(self.env.cr, self.env.user.id,fiscal_position, account_id, context  = self.env.context)

        # set UoS if it's a sale and the picking doesn't have one
        uos_id = move.get('product_uom').id
        quantity = move.get('product_uom_qty')
        taxes = self.env['account.tax'].browse(map(lambda x: x.id, move.get('product_id').supplier_taxes_id))
        fpos = fiscal_position and fp_obj.browse( fiscal_position) or False
        taxes_ids = fp_obj.map_tax(self.env.cr, self.env.uid,fpos, taxes, context = self.env.context)
        return {
            'name': 'Purchase Invoice',
            'account_id': account_id,
            'product_id': move.get('product_id').id,
            'uos_id': uos_id,
            'quantity': quantity,
            'price_unit': move.get('price_unit', 0.0),
            'invoice_line_tax_id': [(6, 0, taxes_ids)],
            'discount': 0.0,
            'account_analytic_id': False,
            'lot_id': lot.id,
            'pedimentos_id' : lot and lot.pedimentos_id and lot.pedimentos_id.id,
        }


     ########################### INVOICES
    
    @api.model
    def _get_invoice_vals(self, filtered_moves, inv_type = 'in_invoice'):
        partner, currency_id, company_id, user_id = self.partner_id, self.company_id.currency_id.id, self.company_id.id, self.env.user.id
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = partner.property_account_receivable.id
            payment_term = partner.property_payment_term.id or False
        else:
            account_id = partner.property_account_payable.id
            payment_term = partner.property_supplier_payment_term.id or False
        return {
            'origin': 'Purchase Order Monthly',
            'date_invoice': self.invoice_date,
            'user_id': user_id,
            'partner_id': partner.id,
            'account_id': account_id,
            'payment_term': payment_term,
            'type': inv_type,
            'fiscal_position': partner.property_account_position.id,
            'company_id': company_id,
            'currency_id': currency_id,
            'journal_id': self.journal_id.id,
            'stock_move_ids' : [(6, 0, [move.id for move in filtered_moves])]
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
