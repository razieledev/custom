from openerp import models, fields, api, _
import datetime


class stock_move(models.Model):

    _inherit = 'stock.move'

    stock_entry = fields.Datetime('Stock Entry')

    @api.onchange('stock_entry')
    def onchange_stock_entry(self):
        current_date_time =  str(datetime.datetime.now())
        if self.stock_entry > current_date_time:
            message = ('Your Time is greater than Current Time')
            self.stock_entry = ''
            warning = {'title': _('Warning!'),
                       'message': message
                       }
            return {'warning': warning}

    def do_move_consume(self, cr, uid, ids, context=None):
            if context is None:
                context = {}
            move_obj = self.pool.get('stock.move')
            uom_obj = self.pool.get('product.uom')
            production_obj = self.pool.get('mrp.production')
            move_ids = context['active_ids']
            move = move_obj.browse(cr, uid, move_ids[0], context=context)
            production_id = move.raw_material_production_id.id
            production = production_obj.browse(cr, uid, production_id, context=context)
            precision = self.pool['decimal.precision'].precision_get(cr, uid, 'Product Unit of Measure')

            for data in self.browse(cr, uid, ids, context=context):
                qty = uom_obj._compute_qty(cr, uid, data['product_uom'].id, data.product_qty, data.product_id.uom_id.id)
                remaining_qty = move.product_qty - qty
                #check for product quantity is less than previously planned
                from openerp.tools import float_compare
                if float_compare(remaining_qty, 0, precision_digits=precision) >= 0:
                    move_obj.action_consume(cr, uid, move_ids, qty, data.location_id.id, restrict_lot_id=data.restrict_lot_id.id, context=context)
                else:
                    consumed_qty = min(move.product_qty, qty)
                    new_moves = move_obj.action_consume(cr, uid, move_ids, consumed_qty, data.location_id.id, restrict_lot_id=data.restrict_lot_id.id, context=context)
                    #consumed more in wizard than previously planned
                    extra_more_qty = qty - consumed_qty
                    #create new line for a remaining qty of the product
                    extra_move_id = production_obj._make_consume_line_from_data(cr, uid, production, data.product_id, data.product_id.uom_id.id, extra_more_qty, False, 0, context=context)
                    move_obj.write(cr, uid, [extra_move_id], {'restrict_lot_id': data.restrict_lot_id.id}, context=context)
                    move_obj.action_done(cr, uid, [extra_move_id], context=context)

            return {'type': 'ir.actions.act_window_close'}


class stock_production_lot(models.Model):

    _inherit = 'stock.production.lot'

    @api.model
    def get_lot_wc(self, products):
        if isinstance(products, (int, long)): products = [products]
        #Searching and retrieving or creating new lot if not found.
        lot_obj = self.env['stock.production.lot']
        lot_ids, lot_id = [], False
        if self._context.get('lot', False):
            lot_ids = lot_obj.search([('name', '=', self._context.get('lot', False)),('product_id', '=', products[0].id)])
            # This is done for the beginning wc_request.check() validation process
            if not lot_ids:
                return False
            lot_id = lot_ids[0].id
            # if self._context.get('for_po', False):
            #     #Find or create for Compuestos
            #     lot_ids = lot_obj.search([('name', '=', 'COMP'+self._context.get('lot', False)),('product_id', '=', products[0].id)])
            #     # print "lot_ids++++++++++++",lot_ids, len(lot_ids)
            #     if not lot_ids:
            #
            #         lot_id = lot_obj.create({'name': 'COMP' + self._context.get('lot', False), 'product_id' : products[0].id }).id
            #         # print "in 11111111111", lot_id
            #     else:
            #         lot_id = lot_ids[0].id
            #     # print "in 33333333333",lot_id
            # # elif self._context.get('for_so', False):
            # #     #Find only in Plasco
            # #     lot_ids = lot_obj.search([('name', '=', self._context.get('lot', False)),('product_id', '=', products[0].id)])
            # #     # This is done for the beginning wc_request.check() validation process
            # #     if not lot_ids:
            # #         return False
            # #     lot_id = lot_ids[0].id
            # elif  self._context.get('for_mo_international', False):
            #     lot_ids = lot_obj.search([('name', '=', 'COMP'+self._context.get('lot', False)),('product_id', '=', products[0].id)])
            #     lot_id = lot_ids[0].id
            # elif not self._context.get('for_mo_international', False):
            #     lot_ids = lot_obj.search([('name', '=', self._context.get('lot', False)),('product_id', '=', products[0].id)])
            #     lot_id = lot_ids[0].id
        return lot_id


class stock_picking(models.Model):

    _inherit = 'stock.picking'

    done_date = fields.Date('Date done')

    @api.model
    def process_picking(self, picking_id):
        '''
            This method will process the picking in assigned state to done.
        '''
        product_obj = self.env['product.product']
        shared_product_id = self._context.get('product_id', False)
        products = product_obj.search([('shared_product_id', '=', shared_product_id)])

        #Searching and retrieving or creating new lot  if not found.
        lot_obj = self.env['stock.production.lot']
        # print "lot_obj._context+++++++",lot_obj._context

        lot_id = lot_obj.get_lot_wc(products)

        picking = self.env['stock.picking'].browse(picking_id)
        picking.action_confirm()
        picking = self.env['stock.picking'].browse(picking_id)
        items = []
        packs = []
        if not picking.pack_operation_ids:
            picking.do_prepare_partial()
        # print "picking pack operations+++product qty++++++++++++++++",picking.pack_operation_ids, self._context.get('product_qty',0)
        for op in picking.pack_operation_ids:
            item = {
                'packop_id': op.id,
                'product_id': op.product_id.id,
                'product_uom_id': op.product_uom_id.id,
                'quantity': self._context.get('product_qty',0),
                'package_id': op.package_id.id,
                'lot_id': lot_id,
                'sourceloc_id': op.location_id.id,
                'destinationloc_id': op.location_dest_id.id,
                'result_package_id': op.result_package_id.id,
                'date': op.date,
                'owner_id': op.owner_id.id,
            }
            if op.product_id:
                items.append(item)
            elif op.package_id:
                packs.append(item)

        processed_ids = []
        # Create new and update existing pack operations
        for lstits in [items, packs]:
            for prod in lstits:
                pack_datas = {
                    'product_id': prod.get('product_id', False) ,
                    'product_uom_id': prod.get('product_uom_id'),
                    'product_qty': prod.get('quantity'),
                    'package_id': prod.get('package_id'),
                    'lot_id': prod.get('lot_id'),
                    'location_id': prod.get('sourceloc_id'),
                    'location_dest_id': prod.get('destinationloc_id'),
                    'result_package_id': prod.get('result_package_id'),
                    'date': prod.get('date') if prod.get('date',False) else datetime.datetime.now(),
                    'owner_id': prod.get('owner_id', False),
                }
                if prod.get('packop_id', False):
                    self.env['stock.pack.operation'].browse(prod.get('packop_id', False)).with_context(no_recompute=True).write(pack_datas)
                    processed_ids.append(prod.get('packop_id', False))
                else:
                    pack_datas['picking_id'] = picking_id
                    packop_id = self.env['stock.pack.operation'].create(pack_datas)
                    processed_ids.append(packop_id.id)
        # Delete the others
        packops = self.env['stock.pack.operation'].search(['&', ('picking_id', '=', picking_id), '!', ('id', 'in', processed_ids)])
        packops.unlink()

        # Execute the transfer of the picking
        # self.env['stock.picking'].browse('picking_id').do_transfer()
        self.pool.get('stock.picking').do_transfer(self._cr, self._uid, [picking_id], self._context)

        return True
    
    @api.cr_uid_ids_context
    def action_assign(self, cr, uid, ids, context=None):
        "Just adding api to be able to pass context"
        return super(stock_picking, self).action_assign( cr, uid, ids, context=context)
