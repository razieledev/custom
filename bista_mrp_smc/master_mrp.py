from openerp.osv import osv, fields
from openerp.tools.translate import _
import math
import datetime

class finished_qty(osv.Model):
    _name = 'finished.qty'
    _columns = {
        'finished_qty': fields.float('Finished Qty'),
        'date': fields.date('date'),
        'state': fields.selection([('cancel', 'Cancel'),('assigned', 'Assigned'), ('unassigned', 'Unassigned')]),
        'premix': fields.boolean('Premix'),
        'master_mrp_id': fields.many2one('master.mrp', 'MO'),
        'Idcontenedor': fields.char('Idcontenedor'),
        'Lotes': fields.char('Lotes'),
        'idlote': fields.char('idlote'),
        'pesoneto': fields.float('pesoneto', help="Weight without Pallet wg"),
        'pesobruto': fields.float('pesobruto', help="Weight with Pallet wg"),
        'morden': fields.char('morden'),
        'sorden': fields.char('sorden'),
        'corden': fields.char('corden'),
        'final': fields.char('final'),
        'fecha': fields.char('fecha'),
        'formulaid': fields.char('formulaid'),
        'clienteid': fields.char('clienteid'),
        'ul': fields.char('ul'),

                }

    def create(self, cr, uid, vals, context=None):
        morden = vals.get('morden')
        if morden:
            mo_id = self.pool.get('master.mrp').search(cr, uid, [('name', '=', morden)], context=context)
            if mo_id:
                vals.update({'master_mrp_id':mo_id[0]})
        return super(finished_qty, self).create(cr, uid, vals, context)


class master_mrp(osv.Model):
    _inherit = 'master.mrp'
    _columns = {
#            'machine': fields.selection([('b1', 'B1'),('b2', 'B2'),('b3', 'B3'),
#                                        ('b4', 'B4'),('b5', 'B5'),('s1', 'S1'),
#                                        ('s2', 'S2'),
#                                        ], 'Machine'),
                                        
            'product_type': fields.selection([('bmc', 'BMC'),('smc', 'SMC'),('premix', 'Premix'),('packaging','Packaging'),
                                              ('internal', 'Internal')], 'Product Type'),
            'machine_id':fields.many2one('machine','Machine'),
            'pres_id':fields.many2one('presentation','Presentation Type'),
            'premix_product_id':fields.many2one('product.product','Premix Product'),
            'tank_weight':fields.float('Tank Weight'),
            'tanks':fields.integer('Tanks'),
            'total_premix_weight':fields.float('Premix Quantity'),
            'disperser_id':fields.many2one('disperser','Disperser'),
            'manual': fields.boolean('Manual', help = "Indicates if this MO is created through manual flow."),
            'finished_qty_ids': fields.one2many('finished.qty','master_mrp_id', 'Finished Qty'),

        }
    _defaults = {
            'name': lambda self, cr, uid, context: self.pool['ir.sequence'].get(cr, uid, 'mrp.production', context=context) or '/',
    }
    def onchange_product_qty(self, cr, uid, ids, qty, product_id, context = None):
        ''' This will change the premix qty simultaneously to product qty'''
        res = {'value': {},'domain':{}}
        if not (qty and product_id): return res
        product_data=self.pool.get('product.product').browse(cr,uid,product_id)
        bom_obj=self.pool.get('mrp.bom')
        bom_id=bom_obj._bom_find(cr, uid, product_id=product_id, properties=[], context = context)
        premix_bom_qty=0
        if bom_id:
            bom_data=bom_obj.browse(cr,uid,bom_id)
            for line in bom_data.bom_line_ids:
                if line.product_id.product_type=='premix':
                    premix_bom_qty=line.product_qty    
        res['value'].update({'total_premix_weight' : qty*premix_bom_qty})
        return res
    
    def onchange_tanks(self, cr, uid, ids, tanks,total_premix_weight, context = None):
        res = {'value': {'tank_weight' : 0}}
        tpw = 0
        if isinstance(ids,(int, long)): ids = [ids]
        for master in self.browse(cr, uid, ids):
            if not tanks: return {'value': {'tanks' : 0, 'tank_weight': 0 }}
            tpw = total_premix_weight if total_premix_weight else master.total_premix_weight
            tanks = float(tanks)
            res['value'].update({
                                'tank_weight' : tpw / tanks,
#                                'total_premix_weight' :  math.ceil(tpw / qty) * qty , 
                                })
            return res

    
    def onchange_batch_qty(self, cr, uid, ids, qty, context = None):
        res = {'value': {'batches' : 0}}
        if isinstance(ids,(int, long)): ids = [ids]
        for master in self.browse(cr, uid, ids):
            if not qty: return {'value': {'batches' : 0, 'product_qty' : master.product_qty }}
            qty = float(qty)
            res['value'].update({
                                'batches' : math.ceil(master.product_qty / qty),
                                'product_qty' :  math.ceil(master.product_qty / qty) * qty , 
                                })
            return res
        
        
    def onchange_product_id(self, cr, uid, ids, product_id, context = None):
        res = {'value': {},'domain':{}}
        product_data=self.pool.get('product.product').browse(cr,uid,product_id)
        bom_obj=self.pool.get('mrp.bom')
        product_type=product_data.product_type
        pres_id=product_data.pres_id.id
        bom_search=bom_obj.search(cr,uid,[('product_id','=',product_id)])
        premix_prod_id=False
        premix_bom_qty=0
        if bom_search:
            bom_data=bom_obj.browse(cr,uid,bom_search[0])
            for each in bom_data.bom_line_ids:
                if each.product_id.product_type=='premix':
                    premix_prod_id=each.product_qty

        res['value'].update({'product_type':product_type,'pres_id':pres_id,'premix_product_id':premix_prod_id,
                             'product_uom':product_data.uom_id.id})
        res['domain'].update({'machine_id':[('product_type', '=', product_type)]})
        return res
    
    def get_batch_vals(self, cr, uid, ids, qty, mo, context = None ):
        routing_id, bom_id, batch_vals = False, False, {}
        bom_obj = self.pool.get('mrp.bom')
       
#        if context.get('pack') and context['pack']==True:
#            product = mo.product_id.pack_product_id
#
#            bom_id = bom_obj._bom_find(cr, uid, product_id=product.id, properties=[], context = context)
#            routing_id = False
#            if bom_id:
#                bom_point = bom_obj.browse(cr, uid, bom_id, context=context)
#                routing_id = bom_point.routing_id.id or False
#            product_uom_id = product.uom_id and product.uom_id.id or False
#            batch_vals.update({
#
#                            'product_id': product.id,
#                            'product_qty': qty,
#                            'product_uom': product_uom_id,
#                            'date_planned': mo and mo.sale_id and mo.sale_id.date_order or datetime.datetime.now(),
#                            'source_document': mo and mo.sale_id and mo.sale_id.name or '/',
#                            'product_uos_qty': qty * product.uos_coeff if product.uos_id.id else False,
#                            'product_uos': product.uos_id.id if product.uos_id.id else False,
#                            'bom_id' : bom_id,
#                            'routing_id': routing_id,
#                            'master_id' : mo.id,})

        if context.get('premix',False):
            product = mo.premix_product_id

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
                            'date_planned': mo and mo.sale_id and mo.sale_id.date_order or datetime.datetime.now(),
                            'origin': mo and mo.sale_id and mo.sale_id.name or '/',
                            'product_uos_qty': qty * product.uos_coeff if product.uos_id.id else False,
                            'product_uos': product.uos_id.id if product.uos_id.id else False,
                            'bom_id' : bom_id,
                            'routing_id': routing_id,
                            'master_id' : mo.id,
                            })                  

        else:
            batch_vals = super(master_mrp, self).get_batch_vals(cr, uid, ids, qty, mo, context = context )
        batch_vals.update({'machine_id': mo.machine_id.id or ''})
        
        return batch_vals
        
    def create(self, cr, uid, vals, context):
        if vals.get('batch_qty', False) and not vals.get('batches', False):
            qty = float(vals.get('batch_qty'))
            vals.update({
                        'batches' : math.ceil(vals.get('product_qty',0) / qty),
                        'product_qty' :  math.ceil(vals.get('product_qty',0) / qty) * qty , 
                        })
            
        return super(master_mrp, self).create(cr, uid, vals, context)

    def confirm_check_batches(self, cr, uid, id, context = None):
        '''
            Confirms the production in draft state and than checks availability.
        '''
        if isinstance(id, (list, tuple)): id = id[0]
        master = self.browse(cr, uid, id)
        batch_ids = [batch.id for batch in master.batch_ids]
        self.pool.get('mrp.production').confirm_check(cr, uid, batch_ids, context=context)
#        if master.state != 'draft':
#                raise osv.except_osv(_('Warning!'), _('To validate MO state must be in Draft'))
        return self.write(cr, uid, id, {'state': 'confirmed'})

    def create_batches(self, cr, uid, ids, context):
        batch_vals, batches = {},[]
        batch_obj = self.pool.get('mrp.production')
        #This context will identify if the batch created is for master Mrp
        # If not then the regular batch order can be created directly and new sequence can be assigned.
        # Passsing this context from view+++++
        # context.update({'has_master': True})
        for mo in self.browse(cr, uid, ids):
#            if mo.product_id.product_type in ['bmc','smc']:
#                if not mo.product_id.pack_product_id:
#                    raise osv.except_osv(_('Warning!'), _('Please define  packaging product of %s'%(mo.product_id.name)) )
               
#            if mo.product_id.pack_product_id:
#                context.update({'pack':True})
#                pack_product=mo.product_id.pack_product_id
#                batch_vals = self.pool('master.mrp').get_batch_vals(cr, uid, ids, mo.product_qty, mo,context=context)
#                batches.append(batch_obj.create(cr, uid, batch_vals, context))
#            
#            
#            batch_vals={}
#            context.update({'pack':False})
            if mo.batch_ids:
                raise osv.except_osv(_('Warning!'), _('Batches are already created.') )
            # This context 'default_manual' is send from action of Manual MO
            if context.get('default_manual',False) and mo.product_id and mo.product_id.product_type != 'internal':
                raise osv.except_osv(_('Warning!'), _('The Product Type of the selcted Product must be Internal.') )

            if mo.premix_product_id!=False:
                context.update({'premix':True})
                for qty in [mo.tank_weight for batch in range(0, mo.tanks)]:
                    batch_vals = self.pool('master.mrp').get_batch_vals(cr, uid, ids, qty, mo,context=context)
                    batches.append(batch_obj.create(cr, uid, batch_vals, context))
#                making premix false as batches get identified properly in get_batch_vals
                context.update({'premix': False})
            batches.append(super(master_mrp,self).create_batches(cr,uid,ids,context=context))
            mo.confirm_check_batches()
        return True

    def produce(self, cr, uid, ids, context = None):
        '''
            Produces the Master MO when 'final' is received as '1' in finished request
        '''
        print "in produce mo+++++"
        if not context: context= {'premix': False}
        if isinstance(ids, (int, long)): ids = [ids]
        batch_obj = self.pool.get('mrp.production')
        print "mo++++",self.browse(cr, uid, ids)
        for mo in self.browse(cr, uid, ids):
            print "in loop mo+++++++++"
            batch_ids = []
            tot_qty = 0
            for fin_qty in mo.finished_qty_ids:
                if fin_qty.premix == context.get('premix', False):
                    print "idlote+++",fin_qty.idlote, fin_qty.idlote.split(',')
                    batch_ids += fin_qty.idlote.split(',')
                    tot_qty += fin_qty.pesoneto if fin_qty.state != 'cancel' else 0
            batch_ids = list(set(batch_ids))
            batch_ids = [int(bt) for bt in batch_ids]
            batch_ids.sort()
            print "batch_ids+++++++",batch_ids
            # batch_ids = list(set(batch_ids))
            print "batch _ ids++++++tota++++++++=",batch_ids,tot_qty
            # mo_qty = mo.product_qty if not context.get('premix',False)  else mo.total_premix_weight
            # if tot_qty >= mo_qty:
            #
            #     qty_per_batch = tot_qty / len(batch_ids)
            #     rem_qty = tot_qty % len(batch_ids)
            #     print "in tot_qty greter++qty_per_batch, rem_qtyr", qty_per_batch, rem_qty
            # if tot_qty < mo_qty:
            #
            #     qty_per_batch = tot_qty / (len(batch_ids)-1)
            #     rem_qty = mo_qty - tot_qty
            #     print "in tot_qty lesesr++qty_per_batch, rem_qtyr", qty_per_batch, rem_qty
            # if context.get('premix', False):
            qty_per_batch = tot_qty / len(batch_ids)
            # else:
            #     qty_per_batch = mo_qty / mo.product_qty
            if not all([batch.id in [bt.id for bt in mo.batch_ids] for batch in batch_obj.browse(cr, uid,batch_ids)]):
                btchs = [batch.name for batch in batch_obj.browse(cr, uid,batch_ids) if batch.id not in [bt.id for bt in mo.batch_ids] ]
                self.message_post(body=_('Something went wrong.Batch id %s is not present in this MO.'% btchs))
                return True
            batch_count = 1
            for batch in batch_obj.browse(cr, uid,batch_ids):
                # if batch_count < len(batch_ids):
                print "in batch_count less"
                batch_obj.action_produce(cr, uid, batch.id, qty_per_batch, 'produce')
                # else: #in case of last batch use remaining qty
                #     print "in batch_count more"
                #     batch_obj.action_produce(cr, uid, batch.id, rem_qty, 'produce')
                # batch_count += 1

        return  True
