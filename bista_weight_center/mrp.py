from openerp import models
from openerp import api, _
from openerp.tools import float_compare, float_is_zero
from openerp import workflow, fields


class mrp_production(models.Model):
    _inherit = 'mrp.production'

    wc_request_ids = fields.One2many('wc.request', 'batch_id', 'Consume Requests')

    @api.cr_uid
    def _get_raw_material_procure_method(self, cr, uid, product, location_id=False, location_dest_id=False, context=None):
        "Overriding this method to creeate move of type make_to_stock for mrp - products to consume moves.This will always return make_to_stock"
        '''We have override this method and all the Moves to consume will be created of type 'make to stock'.
        Reason: Check Availabilty was not working as the product is of type Buy and MTO.
        Effect: We cannot have a flow of type MTO and Buy for Manufacturing.'''

        return "make_to_stock"

    

    @api.one
    def check_move(self, products):
        "Check and return move if move exits in Products to consume"
        move = False
        for line in self.move_lines:
            if line.product_id.id in [product.id for product in products]:
                move = line
        return move

    @api.one
    def auto_consume_line(self):
        "Consumes line automatically"
        #sending the context to override make_po created by procurement
        self.with_context(auto_consume_line = True)
        batch = self
        move = False
        product_obj = self.env['product.product']
        uom_obj = self.env['product.uom']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        production_obj = self.env['mrp.production']
        move_obj = self.env['stock.move']

        # for batch in self.browse(cr, uid, ids):
        shared_product_id = self._context.get('product_id', False)
        product_qty = self._context.get('product_qty', False)
        # print "peoduct qty+++++++",product_qty
        products = product_obj.search([('shared_product_id', '=', shared_product_id)])
        # print "prodssssssssss++++++", products
        for product in products:
            product_uom = product.uom_id.id
        move =  self.check_move(products)
        move = move[0] if isinstance(move, (list, tuple)) else move
        # for line in batch.move_lines:
        #     if line.product_id.id in [product.id for product in products]:
        #         move = line
        if not move :
            return {'error': 'Either the Raw Mateial %s in batch %s is already consumed or else does not exist in BOM'%(products[0].name, self.name)}
        # Testing the reserved quants to see if the requested qty is available
        tot_quant = 0
        for quant in move.reserved_quant_ids:
            tot_quant += quant.qty
        # The quantity can be more or less by 1%
        # When the raw material quantity is measured to be more by 1% or less then below conditon will allow to proccess.
        max_qty = tot_quant + (tot_quant * 0.01)

        if not max_qty >= product_qty:
            return {'error': 'The move for product %s in batch %s does not have proper reserved Quants'%(products[0].name, self.name)}
        # if move and move.state != 'assigned':
        #     print "in move condition true"
        #     return {'error': 'The move for product %s in batch %s is not in assigned state'%(products[0].name, self.name)}

        lot_obj = self.env['stock.production.lot']
        # if products.is_international:
        #     lot_id = lot_obj.with_context(for_mo_international = True, for_po=False , for_so = False).get_lot_wc(products)
        # else:
        lot_id = lot_obj.get_lot_wc(products)
        if not lot_id:
            print "bista_weigh_center/mrp.py***********Lot Id not found+++++++++++++"
        # print "move++++++++++",move
        production_id = move.raw_material_production_id.id
        production = production_obj.browse(production_id)

        uom = uom_obj.browse(product_uom)
        qty = uom._compute_qty(uom.id, product_qty, uom.id)
        # print 'qty++++++++++',qty
        remaining_qty = move.product_qty - qty
        #check for product quantity is less than previously planned
        if float_compare(remaining_qty, 0, precision_digits=precision) >= 0:
            res = move.action_consume(qty, move.location_id.id, restrict_lot_id=lot_id)
            # cancelling the remaining qty move
            self.env['stock.move'].browse(res).action_cancel()
        else:
            consumed_qty = min(move.product_qty, qty)
            new_moves = move.action_consume(consumed_qty, move.location_id.id, restrict_lot_id=lot_id)
            #consumed more in wizard than previously planned
            extra_more_qty = qty - consumed_qty
            #create new line for a remaining qty of the product
            extra_move_id = production_obj._make_consume_line_from_data(production, move.product_id, move.product_id.uom_id.id, extra_more_qty, False, 0)
            extra_move = move_obj.browse(extra_move_id)
            extra_move.write({'restrict_lot_id': lot_id})
            extra_move.action_done()

        return True

    def action_produce(self, cr, uid, production_id, production_qty, production_mode, wiz=False, context=None):
        """
        Overwriting this function to include only the functionality to Produce.

        To produce final product based on production mode (consume/consume&produce).
        If Production mode is consume, all stock move lines of raw materials will be done/consumed.
        If Production mode is consume & produce, all stock move lines of raw materials will be done/consumed
        and stock move lines of final product will be also done/produced.
        @param production_id: the ID of mrp.production object
        @param production_qty: specify qty to produce in the uom of the production order
        @param production_mode: specify production mode (consume/consume&produce).
        @param wiz: the mrp produce product wizard, which will tell the amount of consumed products needed
        @return: True
        """
        stock_mov_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get("product.uom")
        production = self.browse(cr, uid, production_id, context=context)
        production_qty_uom = uom_obj._compute_qty(cr, uid, production.product_uom.id, production_qty, production.product_id.uom_id.id)
        precision = self.pool['decimal.precision'].precision_get(cr, uid, 'Product Unit of Measure')

        main_production_move = False
        if production_mode in ('consume_produce', 'produce'):
            # To produce remaining qty of final product
            produced_products = {}
            for produced_product in production.move_created_ids2:
                if produced_product.scrapped:
                    continue
                if not produced_products.get(produced_product.product_id.id, False):
                    produced_products[produced_product.product_id.id] = 0
                produced_products[produced_product.product_id.id] += produced_product.product_qty
            for produce_product in production.move_created_ids:
                subproduct_factor = self._get_subproduct_factor(cr, uid, production.id, produce_product.id, context=context)
                lot_id = False
                if wiz:
                    lot_id = wiz.lot_id.id
                qty = min(subproduct_factor * production_qty_uom, produce_product.product_qty) #Needed when producing more than maximum quantity
                new_moves = stock_mov_obj.action_consume(cr, uid, [produce_product.id], qty,
                                                         location_id=produce_product.location_id.id, restrict_lot_id=lot_id, context=context)
                stock_mov_obj.write(cr, uid, new_moves, {'production_id': production_id}, context=context)
                remaining_qty = subproduct_factor * production_qty_uom - qty
                if not float_is_zero(remaining_qty, precision_digits=precision):
                    # In case you need to make more than planned
                    #consumed more in wizard than previously planned
                    extra_move_id = stock_mov_obj.copy(cr, uid, produce_product.id, default={'product_uom_qty': remaining_qty,
                                                                                             'production_id': production_id}, context=context)
                    stock_mov_obj.action_confirm(cr, uid, [extra_move_id], context=context)
                    stock_mov_obj.action_done(cr, uid, [extra_move_id], context=context)

                if produce_product.product_id.id == production.product_id.id:
                    main_production_move = produce_product.id

        if production_mode in ['consume', 'consume_produce']:
            if wiz:
                consume_lines = []
                for cons in wiz.consume_lines:
                    consume_lines.append({'product_id': cons.product_id.id, 'lot_id': cons.lot_id.id, 'product_qty': cons.product_qty})
            else:
                consume_lines = self._calculate_qty(cr, uid, production, production_qty_uom, context=context)
            for consume in consume_lines:
                remaining_qty = consume['product_qty']
                for raw_material_line in production.move_lines:
                    if raw_material_line.state in ('done', 'cancel'):
                        continue
                    if remaining_qty <= 0:
                        break
                    if consume['product_id'] != raw_material_line.product_id.id:
                        continue
                    consumed_qty = min(remaining_qty, raw_material_line.product_qty)
                    stock_mov_obj.action_consume(cr, uid, [raw_material_line.id], consumed_qty, raw_material_line.location_id.id,
                                                 restrict_lot_id=consume['lot_id'], consumed_for=main_production_move, context=context)
                    remaining_qty -= consumed_qty
                if not float_is_zero(remaining_qty, precision_digits=precision):
                    #consumed more in wizard than previously planned
                    product = self.pool.get('product.product').browse(cr, uid, consume['product_id'], context=context)
                    extra_move_id = self._make_consume_line_from_data(cr, uid, production, product, product.uom_id.id, remaining_qty, False, 0, context=context)
                    stock_mov_obj.write(cr, uid, [extra_move_id], {'restrict_lot_id': consume['lot_id'],
                                                                    'consumed_for': main_production_move}, context=context)
                    stock_mov_obj.action_done(cr, uid, [extra_move_id], context=context)

        self.message_post(cr, uid, production_id, body=_("%s produced") % self._description, context=context)

        # Remove remaining products to consume if no more products to produce
        if not production.move_created_ids and production.move_lines:
            stock_mov_obj.action_cancel(cr, uid, [x.id for x in production.move_lines], context=context)

        self.signal_workflow(cr, uid, [production_id], 'button_produce_done')
        return True
