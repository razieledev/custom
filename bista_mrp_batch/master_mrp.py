from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime

class master_mrp(osv.Model):
    _name = 'master.mrp'
    _description = 'Manufacturing Order'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def product_id_change(self, cr, uid, ids, product_id, product_qty=0, context=None):
        """ Finds UoM of changed product.
        @param product_id: Id of changed product.
        @return: Dictionary of values.
        """
        result = {}
        if not product_id:
            return {'value': {
                'product_uom': False,
                'bom_id': False,
                'routing_id': False,
                'product_uos_qty': 0,
                'product_uos': False
            }}
        bom_obj = self.pool.get('mrp.bom')
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        bom_id = bom_obj._bom_find(cr, uid, product_id=product.id, properties=[], context=context)
        routing_id = False
        if bom_id:
            bom_point = bom_obj.browse(cr, uid, bom_id, context=context)
            routing_id = bom_point.routing_id.id or False
        product_uom_id = product.uom_id and product.uom_id.id or False
        result['value'] = {'product_uos_qty': 0, 'product_uos': False, 'product_uom': product_uom_id, 'bom_id': bom_id, 'routing_id': routing_id}
        if product.uos_id.id:
            result['value']['product_uos_qty'] = product_qty * product.uos_coeff
            result['value']['product_uos'] = product.uos_id.id
        return result
    _columns = {
        'name': fields.char('Reference', required=True, readonly=True, states={'draft': [('readonly', False)]}, copy=False),
        'origin': fields.char('Source Document', readonly=True, states={'draft': [('readonly', False)]},
            help="Reference of the document that generated this production order request.", copy=False),
#        'priority': fields.selection([('0', 'Not urgent'), ('1', 'Normal'), ('2', 'Urgent'), ('3', 'Very Urgent')], 'Priority',
#            select=True, readonly=True, states=dict.fromkeys(['draft', 'confirmed'], [('readonly', False)])),

        'product_id': fields.many2one('product.product', 'Product', required=True, readonly=True, states={'draft': [('readonly', False)]}, 
                                      domain=[('type','!=','service')]),
        'product_qty': fields.float('Product Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'product_uos_qty': fields.float('Product UoS Quantity', readonly=True, states={'draft': [('readonly', False)]}),
        'product_uos': fields.many2one('product.uom', 'Product UoS', readonly=True, states={'draft': [('readonly', False)]}),
#        'progress': fields.function(_get_progress, type='float',
#            string='Production progress'),

#        'location_src_id': fields.many2one('stock.location', 'Raw Materials Location', required=True,
#            readonly=True, states={'draft': [('readonly', False)]},
#            help="Location where the system will look for components."),
#        'location_dest_id': fields.many2one('stock.location', 'Finished Products Location', required=True,
#            readonly=True, states={'draft': [('readonly', False)]},
#            help="Location where the system will stock the finished products."),
        'date_planned': fields.datetime('Scheduled Date', required=True, select=1, readonly=True, states={'draft': [('readonly', False)]}, copy=False),
        'date_start': fields.datetime('Start Date', select=True, readonly=True, copy=False),
        'date_finished': fields.datetime('End Date', select=True, readonly=True, copy=False),
        'bom_id': fields.many2one('mrp.bom', 'Bill of Material', readonly=True, states={'draft': [('readonly', False)]},
            help="Bill of Materials allow you to define the list of required raw materials to make a finished product."),
        'routing_id': fields.many2one('mrp.routing', string='Routing', on_delete='set null', readonly=True, states={'draft': [('readonly', False)]},
            help="The list of operations (list of work centers) to produce the finished product. The routing is mainly used to compute work center costs during operations and to plan future loads on work centers based on production plannification."),
        'state': fields.selection(
            [('draft', 'New'), ('cancel', 'Cancelled'), ('confirmed', 'In Process'),
                 ('done', 'Done')],
            string='Status', readonly=True,
            track_visibility='onchange', copy=False,
            help="When the production order is created the status is set to 'Draft'.\n\
                If the order is confirmed the status is set to 'In Process'.\n\
                When the production is over, the status is set to 'Done'."),
        
        'user_id': fields.many2one('res.users', 'Responsible'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
#        'ready_production': fields.function(_moves_assigned, type='boolean', store={'stock.move': (_mrp_from_move, ['state'], 10)}),
        'batches' : fields.integer('Batches'),
        'batch_qty' : fields.float('Batch Weight'),
        'batch_ids' : fields.one2many('mrp.production', 'master_id','Batches'),
        'sale_id': fields.many2one('sale.order', 'Refrence SO'),
    }
    _defaults = {
        'state': 'draft',
        'user_id' : lambda self, cr, uid, c: uid , 
        'company_id': lambda self, cr, uid, context: self.pool.get('res.company')._company_default_get(cr, uid, 'master.mrp', context=context)
    }
    def create(self, cr, uid, vals, context = None):
        print "in create ++++++++++++++++",vals
        return super(master_mrp, self).create(cr, uid, vals, context)
    
#    def validate(self, cr, uid, ids, context = None):
#        if isinstance(ids, (int , long)): ids = [ids]
#        for mo in self.browse(cr, uid, ids):
#            if mo.state != 'draft':
#                raise osv.except_osv(_('Warning!'), _('To validate MO state must be in Draft'))
#        return self.write(cr, uid, ids, {'state': 'confirmed'})
    
    def get_batch_vals(self, cr, uid, ids, qty, mo, context=None):
        routing_id, bom_id, batch_vals = False, False, {}
        product_uom_id = False
        bom_obj = self.pool.get('mrp.bom')
        product = mo.product_id
        bom_id = bom_obj._bom_find(cr, uid, product_id=product.id, properties=[], context = context)
        routing_id = False
        if bom_id:
            bom_point = bom_obj.browse(cr, uid, bom_id, context=context)
            routing_id = bom_point.routing_id.id or False
        product_uom_id = product.uom_id and product.uom_id.id or False
        batch_vals.update({
                        'product_id': product.id,
                        'product_qty': qty,
                        'product_uom': product_uom_id,
                        'date_planned': mo and mo.date_planned or datetime.datetime.now(),
                        'origin': mo and mo.sale_id and mo.sale_id.name or '/',
                        'product_uos_qty': qty * product.uos_coeff if product.uos_id.id else False,
                        'product_uos': product.uos_id.id if product.uos_id.id else False,
                        'bom_id' : bom_id,
                        'routing_id': routing_id,
                        'master_id' : mo.id,
                        })
        return batch_vals
    
    def create_batches(self, cr, uid, ids, context):
        if isinstance(ids, (int , long)): ids = [ids]
        batch_vals, batch_ids = {}, []
        batch_obj = self.pool.get('mrp.production')
        
        for mo in self.browse(cr, uid, ids):
#            if mo.batch_ids:
#                raise osv.except_osv(_('Warning!'), _('Batches are already created.') )
#            if mo.state in ('draft','cancel','done'):
#                raise osv.except_osv(_('Warning!'), _('Batches can be created in Confirmed state only') )
            for qty in [mo.batch_qty for batch in range(0, mo.batches)]:
                batch_vals = self.pool('master.mrp').get_batch_vals(cr, uid, ids, qty, mo, context=context)
                batch_ids.append(batch_obj.create(cr, uid, batch_vals, context))
        return batch_ids
    
    
    def cancel_master(self, cr, uid, ids, context = None):
        if isinstance(ids, (int, long)): ids = [ids]
        for master in self.browse(cr, uid, ids):
            batch_ids = []
            if master.state == 'done':
                raise osv.except_osv(_('Warning!'), _('Cannot be cancelled once the Manufacturing is Done') )
            for batch in master.batch_ids:
                batch_ids.append(batch.id)
                if batch.state == 'done':
                    raise osv.except_osv(_('Warning!'), _('One of the batch is already Done. \\n Please cancel the particular batch manually.') )
            
            if batch_ids:
                self.pool.get('mrp.production').action_cancel(cr, uid, batch_ids, context)
                master.write({'state': 'cancel'})
            else:
                master.write({'state': 'cancel'})
            
            return True