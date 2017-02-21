from openerp import api,fields, models, _


class res_partner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def tik_on(self):
        rec = self.search([('is_company', '=', True)])
        rec_f = self.search([('is_company', '=', False)])
        for res_id in rec:
            res_id.is_company = False
            res_id.is_company = True

        for res_id in rec_f:
            res_id.is_company = True
            res_id.is_company = False

    @api.multi
    def serial_c(self):
        lot_obj = self.env['stock.production.lot']
        all_product = self.env['product.product'].search([])
        for product in all_product:
            lot_obj.create({'name': 1, 'product_id': product.id})

    @api.multi
    def inv_c(self):
        inv = self.env['stock.inventory']
        inv_line = self.env['stock.inventory.line']
        all_product = self.env['product.product'].search([])
        inv_id = inv.create({'name': 'Test',
                             'location_id': 12,
                             'filter': 'none'})
        if inv_id:
            for product in all_product:
                lot_id = self.env['stock.production.lot'].search([('name', '=', '1'), ('product_id', '=', product.id)])
                inv_line.create({'inventory_id': inv_id.id,
                                 'product_id': product.id,
                                 'location_id': 12,
                                 'prod_lot_id': lot_id.id,
                                 'product_uom_id': product.uom_id.id,
                                 'product_qty': 1000,
                                 })
