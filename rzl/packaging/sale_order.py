from openerp import models, fields, api
from openerp import osv

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    packaging_qty = fields.Integer('No. of Packages', help='Number of packages to be sold')

    @api.onchange('packaging_qty')
    def onchange_packaging_qty(self):
        self.product_uom_qty = self.product_packaging.qty * self.packaging_qty

class SaleOrder(osv.osv.osv):
    _inherit = 'sale.order'

    def _prepare_order_line_procurement(self,cr, uid, order, line, group_id=False, context = {}):
        context.update({'product_packaging': line.product_packaging.id,
                                'packaging_qty': line.packaging_qty})

        res = super(SaleOrder, self)._prepare_order_line_procurement(cr, uid,order, line, group_id=group_id,context=context)
        # res.update({'product_packaging': line.product_packaging.id,
        #             'packaging_qty': line.packaging_qty})
        # print "preparing order line proc", res
        return res