from openerp import models, fields, api, _
from openerp.exceptions import Warning


class stock_production_lot(models.Model):
    _inherit = 'stock.production.lot'
    
    pedimentos_id = fields.Many2one('pedimentos', string='Pedimento No.')
    cove = fields.Char(string='Cove')


class stock_move(models.Model):
    _inherit = 'stock.move'
    
    inv_id = fields.Many2one('account.invoice', string = 'Invoice')


#class stock_transfer_details(models.TransientModel):
#    _inherit = 'stock.transfer_details'
#
#    @api.one
#    def do_detailed_transfer(self):
#        res = super(stock_transfer_details, self).do_detailed_transfer()
#        picking_id = self.picking_id
#        if self.env.context.get('auto_pick_flag'):
#            purchase_obj = self.env['purchase.order']
#            po = purchase_obj.search([('name', '=', picking_id.origin)])
#            for po_rec in po.ref_po_id.purchase_line_ids:
#                if po_rec.state in ('confirmed', 'approved'):
#                    for picking in po_rec.picking_ids:
#                        if picking.state in ('cancel', 'done'):
#                            continue
#                        if picking.state != 'assigned':
#                            picking.force_assign()
#                        picking.action_done()
#                else:
#                    if po_rec.state == 'cancel':
#                        raise Warning(_('Purchase order %s is cancelled') % po_rec.name)
#                    if po_rec.state not in ('confirmed', 'approved', 'cancel'):
#                        raise Warning(_('Purchase order %s still not process from SMC Comp Inc (USA) ') % po_rec.name)
#
#            for so_rec in po.ref_po_id.sale_line_ids:
#                if so_rec.company_id.name == 'Productos Plasco SA de CV' and so_rec.partner_id.name == 'Compuestos SMC Mexico SA de CV':
#                    continue
#                for picking in so_rec.picking_ids:
#                    if picking.state in ('cancel', 'done'):
#                        continue
#                    if picking.state != 'assigned':
#                        picking.force_assign()
#                    picking.action_done()
#        return res


# class StockPicking(models.Model):
#
#     _inherit = 'stock.picking'
#
#     @api.model
#     def create(self, vals):
#         #Correcting company id in Stock Picking.
#         res = super(StockPicking, self).create(vals)
#         if 'picking_type_id' in vals:
#             picking_type_obj = self.env['stock.picking.type']
#             picking_type  = picking_type_obj.browse(vals.get('picking_type_id'))
#             if picking_type.name == 'Dropship':
#                 return res
#             company = picking_type.warehouse_id.company_id
#             res.update({'company_id': company.id})
#         return res
