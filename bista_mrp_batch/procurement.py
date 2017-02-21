from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

class procurement_order(osv.osv):
    _inherit = 'procurement.order'
    
    # Method Overidden
    def _prepare_mo_vals(self, cr, uid, procurement, context=None):
        res_id = procurement.move_dest_id and procurement.move_dest_id.id or False
        newdate = self._get_date_planned(cr, uid, procurement, context=context)
        bom_obj = self.pool.get('mrp.bom')
        if procurement.bom_id:
            bom_id = procurement.bom_id.id
            routing_id = procurement.bom_id.routing_id.id
        else:
            properties = [x.id for x in procurement.property_ids]
            bom_id = bom_obj._bom_find(cr, uid, product_id=procurement.product_id.id,
                                       properties=properties, context=dict(context, company_id=procurement.company_id.id))
            bom = bom_obj.browse(cr, uid, bom_id, context=context)
            routing_id = bom.routing_id.id
        return {
            'origin': procurement.origin,
            'product_id': procurement.product_id.id,
            'product_qty': procurement.product_qty,
            'product_uom': procurement.product_uom.id,
            'product_uos_qty': procurement.product_uos and procurement.product_uos_qty or False,
            'product_uos': procurement.product_uos and procurement.product_uos.id or False,
#            'location_src_id': procurement.location_id.id,
#            'location_dest_id': procurement.location_id.id,
            'bom_id': bom_id,
            'routing_id': routing_id,
            'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
#            'move_prod_id': res_id,
            'company_id': procurement.company_id.id,
        }
    
    # Method Overidden
    def make_mo(self, cr, uid, ids, context=None):
        """ Make Manufacturing(production) order from procurement
        @return: New created Production Orders procurement wise
        """
        res = {}
        production_obj = self.pool.get('master.mrp')
        procurement_obj = self.pool.get('procurement.order')
        for procurement in procurement_obj.browse(cr, uid, ids, context=context):
            if self.check_bom_exists(cr, uid, [procurement.id], context=context):
                #create the MO as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
                vals = self._prepare_mo_vals(cr, uid, procurement, context=context)
                produce_id = production_obj.create(cr, SUPERUSER_ID, vals, context=dict(context, force_company=procurement.company_id.id))
                res[procurement.id] = produce_id
                self.write(cr, uid, [procurement.id], {'production_id': produce_id})
#                self.production_order_create_note(cr, uid, procurement, context=context)
#                production_obj.action_compute(cr, uid, [produce_id], properties=[x.id for x in procurement.property_ids])
#                production_obj.signal_workflow(cr, uid, [produce_id], 'button_confirm')
            else:
                res[procurement.id] = False
                self.message_post(cr, uid, [procurement.id], body=_("No BoM exists for this product!"), context=context)
        return res
