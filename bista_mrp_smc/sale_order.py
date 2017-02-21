from openerp.osv import osv, fields
from openerp.tools.translate import _
import datetime


class sale_order(osv.Model):
    _inherit = 'sale.order'
    _columns = {
        'master_ids': fields.one2many('master.mrp','sale_id', 'MO\'s'),
    }

    # def company_onchange(self, cr, uid, ids, company_id, context=None):
    #     company_name = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
    #     value = {}
    #     if company_name.name == 'SMC COMPOSITES SA DE CV':
    #         value.update({'order_policy': 'picking'})
    #     else:
    #         value.update({'order_policy': 'manual'})
    #     return {'value': value}

    def create_manufacturing_order(self, cr, uid, ids, context):
        if isinstance(ids, (int , long)): ids = [ids]
        sale_orders = self.browse(cr, uid, ids, context)
        user = self.pool.get('res.users').browse(cr, uid, uid)
        master_ids = []
        master = self.pool.get('master.mrp')
        master_vals = {}
        for so in sale_orders:
            # if not (user.company_id and user.company_id.is_manufacturing_company):
            #     raise osv.except_osv(_('Warning!'), _('Please change your company to Compuestos to create MO.'))
            #
            # if not (so.company_id and so.company_id.is_manufacturing_company):
            #     raise osv.except_osv(_('Warning!'), _('Manufacturing Order can be created only for Compuestos Sales Order.') )
            if not so.order_line:
                raise osv.except_osv(_('Warning!'), _('There are no Sale Order Lines.') )
            if so.master_ids:
                for master_mo in so.master_ids:
                    if master_mo.state != 'cancel':
                        raise osv.except_osv(_('Warning! Cannot Recreate MO until you cancel previously created MO for this SO.'),
                                             _('Please cancel all the Manufacturing orders first for this Sales Order.'))
            for line in so.order_line:
                
                routing_id, bom_id = False, False
                product_uom_id = False
                bom_obj = self.pool.get('mrp.bom')
                product = line.product_id
                bom_id = bom_obj._bom_find(cr, uid, product_id=product.id, properties=[], context=context)
                routing_id = False
                premix_prod_id=''
                premix_bom_qty=0
                if not bom_id:
                    raise  osv.except_osv(_('Warning!'), _('There is no BOM defined for this Product.'))
                if bom_id:
                    bom_point = bom_obj.browse(cr, uid, bom_id, context=context)
                    print "bom+++++++",bom_point
                    premix_count = 0
                    for each in bom_point.bom_line_ids:
                        if each.product_id.product_type=='premix':
                            premix_count += 1
                            premix_prod_id=each.product_id.id
                            premix_bom_qty=each.product_qty
                    print "premix+++++",premix_prod_id,premix_bom_qty
                    routing_id = bom_point.routing_id.id or False
                    if premix_count > 1:
                        raise  osv.except_osv(_('Warning!'), _('Cannot create MO. Product has more than 1 Premix type raw material in '
                                                               'BOM.') )
                product_uom_id = product.uom_id and product.uom_id.id or False
                master_vals.update({
                                'product_id': line.product_id.id,
                                'product_qty': line.product_uom_qty,
                                'product_uom': product_uom_id,
                                'date_planned': datetime.datetime.now(),
                                'origin': line.order_id.name,
                                'product_uos_qty': line.product_uom_qty * product.uos_coeff if product.uos_id.id else False,
                                'product_uos': product.uos_id.id if product.uos_id.id else False,
                                'bom_id' : bom_id,
                                'routing_id': routing_id,
                                'batches': 0,
                                'batch_qty': 0.0,
                                'product_type':product.product_type,
                                'pres_id':product.pres_id.id,
                                'premix_product_id':premix_prod_id,
                                'total_premix_weight':line.product_uom_qty*premix_bom_qty
                                })
                
                master_ids.append(master.create(cr, uid, master_vals, context))
            if master_ids:
                so.write({'master_ids' : [(6 , 0, master_ids)]})
            
        return True


# class sale_order_line(osv.Model):
#
#     _inherit = 'sale.order.line'
#
#     def product_id_change_smc_route(self, cr, uid, ids, pricelist, product, qty=0,
#             uom=False, qty_uos=0, uos=False, name='', partner_id=False,
#             lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, warehouse_id=False, context=None):
#         '''
#             Changing the Onchange on product id to automatically select route to Dropshipping.
#
#         '''
#
#         res = self.product_id_change_with_wh(cr, uid, ids, pricelist, product, qty=qty,
#             uom=False, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
#             lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
#
#         product_obj = self.pool.get('product.product')
#         product = product_obj.browse(cr, uid, product, context=context)
#         route_obj = self.pool.get('stock.location.route')
#         route_ids = route_obj.search(cr, uid, [('name', '=', 'Drop Shipping')])
#         if route_ids and product.is_dropshipping:
#             res['value'].update({'route_id': route_ids[0]})
#         else:
#             res['value'].update({'route_id': False})
#
#         return res

