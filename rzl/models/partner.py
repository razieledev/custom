from openerp import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    product_code = fields.Char('Product code', help='This code will be used for Product naming')
    product_ids = fields.One2many('product.product','partner_id')

