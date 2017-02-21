from openerp.osv import osv
from openerp.tools.float_utils import float_compare


class stock_picking(osv.osv):

    _inherit = "stock.picking"

    def recompute_remaining_qty(self, cr, uid, picking, context=None):
        "***********Fixing issue on partial incoming and quants++++ line 60,61,62"
        def _create_link_for_index(operation_id, index, product_id, qty_to_assign, quant_id=False):
            move_dict = prod2move_ids[product_id][index]
            # print "prod2move_ids+++++++indes",prod2move_ids,index
            qty_on_link = min(move_dict['remaining_qty'], qty_to_assign)
            self.pool.get('stock.move.operation.link').create(cr, uid, {'move_id': move_dict['move'].id, 'operation_id': operation_id, 'qty': qty_on_link, 'reserved_quant_id': quant_id}, context=context)
            if move_dict['remaining_qty'] == qty_on_link:
                prod2move_ids[product_id].pop(index)
            else:
                move_dict['remaining_qty'] -= qty_on_link
            return qty_on_link

        def _create_link_for_quant(operation_id, quant, qty):
            """create a link for given operation and reserved move of given quant, for the max quantity possible, and returns this quantity"""
            if not quant.reservation_id.id:
                return _create_link_for_product(operation_id, quant.product_id.id, qty)
            qty_on_link = 0
            for i in range(0, len(prod2move_ids[quant.product_id.id])):
                if prod2move_ids[quant.product_id.id][i]['move'].id != quant.reservation_id.id:
                    continue
                qty_on_link = _create_link_for_index(operation_id, i, quant.product_id.id, qty, quant_id=quant.id)
                break
            return qty_on_link

        def _create_link_for_product(operation_id, product_id, qty):
            '''method that creates the link between a given operation and move(s) of given product, for the given quantity.
            Returns True if it was possible to create links for the requested quantity (False if there was not enough quantity on stock moves)'''
            qty_to_assign = qty
            prod_obj = self.pool.get("product.product")
            product = prod_obj.browse(cr, uid, product_id)
            rounding = product.uom_id.rounding
            qtyassign_cmp = float_compare(qty_to_assign, 0.0, precision_rounding=rounding)
            if prod2move_ids.get(product_id):
                while prod2move_ids[product_id] and qtyassign_cmp > 0:
                    qty_on_link = _create_link_for_index(operation_id, 0, product_id, qty_to_assign, quant_id=False)
                    qty_to_assign -= qty_on_link
                    qtyassign_cmp = float_compare(qty_to_assign, 0.0, precision_rounding=rounding)
            return qtyassign_cmp == 0

        uom_obj = self.pool.get('product.uom')
        package_obj = self.pool.get('stock.quant.package')
        quant_obj = self.pool.get('stock.quant')
        link_obj = self.pool.get('stock.move.operation.link')
        quants_in_package_done = set()
        prod2move_ids = {}
        still_to_do = []
        # import pdb
        # pdb.set_trace()

        # Fixing issue of picking.move_lines coming in Descending order which caused issue on partial picking and quants.
        #####################################
        list_move_ids = [x.id for x in picking.move_lines if x.state not in ('done', 'cancel')]
        list_moves = []
        if list_move_ids:
            list_move_ids.sort()
            list_moves = [self.pool.get('stock.move').browse(cr, uid, id) for id in list_move_ids]

        ######################################
        #make a dictionary giving for each product, the moves and related quantity that can be used in operation links
        for move in list_moves:
            links_move = link_obj.search(cr, uid, [('move_id', '=', move.id)], context=context),
            # print "links move__+++++++++move++++",links_move,move
            if not prod2move_ids.get(move.product_id.id):

                prod2move_ids[move.product_id.id] = [{'move': move, 'remaining_qty': move.product_qty}]
                # print "in not prod2move++++++",prod2move_ids
            else:
                prod2move_ids[move.product_id.id].append({'move': move, 'remaining_qty': move.product_qty})
                # print "in prod2move+++",prod2move_ids


        # print "out sude +++prod2move_ids",prod2move_ids
        need_rereserve = False
        #sort the operations in order to give higher priority to those with a package, then a serial number
        operations = picking.pack_operation_ids
        operations = sorted(operations, key=lambda x: ((x.package_id and not x.product_id) and -4 or 0) + (x.package_id and -2 or 0) + (x.lot_id and -1 or 0))
        #delete existing operations to start again from scratch
        links = link_obj.search(cr, uid, [('operation_id', 'in', [x.id for x in operations])], context=context)
        # print "links+++++++++=",links
        if links:
            for link in link_obj.browse(cr, uid,links):
                link_obj.unlink(cr, uid, links, context=context)
                # print "deleting link++++++++",links, link.qty

        #1) first, try to create links when quants can be identified without any doubt
        for ops in operations:
            #for each operation, create the links with the stock move by seeking on the matching reserved quants,
            #and deffer the operation if there is some ambiguity on the move to select
            if ops.package_id and not ops.product_id:
                #entire package
                # print "in package++++++++++++++++++quants"
                quant_ids = package_obj.get_content(cr, uid, [ops.package_id.id], context=context)
                # print "in package++++++++++++++++++quants",quant_ids
                for quant in quant_obj.browse(cr, uid, quant_ids, context=context):
                    remaining_qty_on_quant = quant.qty
                    if quant.reservation_id:
                        # print "in quant reservation +++quant.reservation_id+", quant.reservation_id
                        #avoid quants being counted twice
                        quants_in_package_done.add(quant.id)
                        qty_on_link = _create_link_for_quant(ops.id, quant, quant.qty)
                        remaining_qty_on_quant -= qty_on_link
                    if remaining_qty_on_quant:
                        # print "in+++remaining_qty_on_quant",remaining_qty_on_quant
                        still_to_do.append((ops, quant.product_id.id, remaining_qty_on_quant))
                        need_rereserve = True
                        # print "still_to_do++++",still_to_do
            elif ops.product_id.id:
                #Check moves with same product
                qty_to_assign = uom_obj._compute_qty_obj(cr, uid, ops.product_uom_id, ops.product_qty, ops.product_id.uom_id, context=context)
                # print "qty_to_assign+++++",qty_to_assign
                for move_dict in prod2move_ids.get(ops.product_id.id, []):
                    move = move_dict['move']
                    for quant in move.reserved_quant_ids:
                        if not qty_to_assign > 0:
                            break
                        if quant.id in quants_in_package_done:
                            continue

                        #check if the quant is matching the operation details
                        if ops.package_id:
                            flag = quant.package_id and bool(package_obj.search(cr, uid, [('id', 'child_of', [ops.package_id.id])], context=context)) or False
                        else:
                            flag = not quant.package_id.id

                        flag = flag and ((ops.lot_id and ops.lot_id.id == quant.lot_id.id) or not ops.lot_id)
                        flag = flag and (ops.owner_id.id == quant.owner_id.id)
                        if flag:
                            max_qty_on_link = min(quant.qty, qty_to_assign)
                            qty_on_link = _create_link_for_quant(ops.id, quant, max_qty_on_link)
                            # print "qty_on_link+++++++++",qty_on_link
                            qty_to_assign -= qty_on_link
                            # print "qty_to_assign++++++++",qty_to_assign
                qty_assign_cmp = float_compare(qty_to_assign, 0, precision_rounding=ops.product_id.uom_id.rounding)

                if qty_assign_cmp > 0:
                    #qty reserved is less than qty put in operations. We need to create a link but it's deferred after we processed
                    #all the quants (because they leave no choice on their related move and needs to be processed with higher priority)
                    still_to_do += [(ops, ops.product_id.id, qty_to_assign)]
                    need_rereserve = True

        #2) then, process the remaining part
        all_op_processed = True
        # print "final   still_to_do+++final+",still_to_do
        for ops, product_id, remaining_qty in still_to_do:
            all_op_processed = _create_link_for_product(ops.id, product_id, remaining_qty) and all_op_processed
        return (need_rereserve, all_op_processed)
