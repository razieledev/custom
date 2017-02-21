# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import Warning
from openerp.osv import osv

class stock_transfer_details(models.TransientModel):
    _inherit = 'stock.transfer_details'

    def _get_product_selection(self):
        picking_ids = self.env.context.get('active_ids')
        StockPicking = self.env['stock.picking'].browse(picking_ids and picking_ids[0])
        res = []
        for line in StockPicking.move_lines:
            res.append((str(line.product_id.id), line.product_id.name_get()[0][1]))
        return res

    product_id = fields.Selection(_get_product_selection, 'Product')
    split_number = fields.Integer('Split Lot Number')

    @api.multi
    def split_tranfer_quantities(self):
        if not self.product_id:
            raise Warning(_('You cannot split lots without product.'))
        if not self.split_number > 0:
            raise Warning(_('You cannot enter zero or less than zero lots.'))

        self.item_ids.split_move()
        return self.wizard_view()

    @api.one
    def do_detailed_transfer(self):
        if self.env.user.has_group('qc_serial.group_disable_auto_qc_serial'):
            return super(stock_transfer_details, self).do_detailed_transfer()
        stock_lot = self.env['stock.production.lot']
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))

        # create QC serial number only base in this condition
        if picking.picking_type_id.code == 'incoming':
            product_ids = []
            line_number = 1
            sequence_no = None
            # sort lines by product_id to maintain auto sequence
            for item in self.item_ids.sorted(lambda item: item.product_id.id):
                if item.lot_id:
                    continue
                product_default_code = item.product_id.default_code
                if not item.product_id.product_type:
                    raise osv.except_osv(_('Warning!'), _('Please Select the product type in the Product!'))
                if not item.product_id.product_type in ('bmc','smc', 'premix', 'packaging', 'internal', 'miselaneous'):
                    if item.product_id.id not in product_ids:
                        sequence_no = self.env['ir.sequence'].next_by_code('stock.production.lot.sequence')
                        product_ids.append(item.product_id.id)
                        line_number = 1
                    lot_name = '%s - %s' % (sequence_no, str(line_number).zfill(2))
                    if product_default_code:
                        lot_name = '%s - %s - %s' % (product_default_code, sequence_no, str(line_number).zfill(2))
                    lot_vals = {
                        'name': lot_name,
                        'product_id': item.product_id.id,
                        'picking_id': picking.id,
                        'date': fields.Date.today(),
                        'company_id': picking.company_id.id,
                        'supplier_ref': item.supplier_ref,
                    }
                    item.lot_id = stock_lot.create(lot_vals)
                    line_number = line_number + 1
        res = super(stock_transfer_details, self).do_detailed_transfer()

        # auto transfer quont in inter company
#        sale_order = self.env['sale.order'].search([('name' , '=', picking.origin)])
#        for item in self.item_ids.sorted(lambda item: item.product_id.id):
#            auto_pickings = sale_order.ref_po_id.picking_ids.filtered(lambda p: p.state == 'assigned')
#            auto_picking = auto_pickings and auto_pickings[0]
#            auto_picking.with_context(product_qty=item.quantity, product_id=item.product_id.id).process_picking(auto_picking.id)
        return res


class stock_transfer_details_items(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    supplier_ref = fields.Char('Supplier Ref.')

    @api.multi
    def split_move(self):
        transfer = self and self[0].transfer_id
        qty = 0.0
        line = None
        unlink_items = self.env['stock.transfer_details_items']
        for itm in transfer.item_ids:
            if itm.product_id.id == int(transfer.product_id):
                qty += itm.quantity
                line = itm
                unlink_items += itm
        copy_vals = line.copy_data()[0]
        # set it to False because creating new pack operation
        set_qty = qty / float(transfer.split_number)
        copy_vals['packop_id'] = False
        copy_vals['quantity'] = set_qty

        all_vals = []
        for i in range(transfer.split_number):
            all_vals.append((0,0, copy_vals))

        # unlink product lines and then create new lines with specified quantities
        unlink_items.unlink()
        transfer.write({'item_ids': all_vals})
        return True
