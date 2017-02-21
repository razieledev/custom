from openerp import models, api

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _prepare_sale_order_line_data(self, line, company, sale_id, intercompany_uid):
        res = super(purchase_order, self)._prepare_sale_order_line_data(line, company, sale_id, intercompany_uid)
        res.update({
            'product_packaging': line.product_packaging.id,
            'packaging_qty': line.packaging_qty
            })
        return res