from openerp.osv import osv, fields

class sale_order(osv.Model):

    _inherit = 'sale.order'

    # _columns = {
    #     'ref_po_id': fields.many2one('purchase.order', string='Reference PO')
    # }

    def _prepare_order_line_procurement(self, cr, uid, order, line, group_id=False, context=None):
        ''' Overriding to bring property_stock_customer from company for multi-company scenario.
            This function will limit us from using customer location specified for each customer.'''
        result = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order, line, group_id=group_id, context=context)
        if not result: result = {}
        if order.company_id:
            result.update({'location_id' : order.company_id.partner_id and order.company_id.partner_id.property_stock_customer and order.company_id.partner_id.property_stock_customer.id or False})
        return result
    
    # def action_button_confirm(self, cr, uid, ids, context=None):
    #     res = super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)
    #     orders = self.browse(cr, uid, ids)
    #     for order_rec in orders:
    #         if order_rec.company_id and order_rec.company_id.name == 'SMC Comp Inc (USA)':
    #             self.manual_invoice(cr, uid, [order_rec.id], context=context)
    #             return res
    #         else:
    #             return res
