from openerp import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_packaging = fields.Many2one('product.packaging', 'Packaging')
    packaging_qty = fields.Integer('No. of Packages', help='Number of packages to be sold')