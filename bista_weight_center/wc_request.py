from openerp import models, fields, osv
from openerp import api
import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class wc_request(models.Model):

    _name = 'wc.request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char(string = 'Name', default = 'Weigh Center Request')
    lot_name = fields.Char(string = 'Lot')
    shared_product_id = fields.Integer(string = 'Shared Product Id')
    product_qty = fields.Float(string = 'Product Qty', digits = dp.get_precision('Product Unit of Measure'))
    batch_id = fields.Many2one('mrp.production', string = 'Batch Id')
    wc_id = fields.Integer(string = 'Weight Center Id')
    state = fields.Selection([('new','New'), ('exception', 'Exception'), ('done', 'Done'),('cancel','Cancelled')], string = 'State', track_visibility = 'always')
    done_picking = fields.Boolean(string = 'Picking Done', help = 'Used as Flag, when picking is processed and flow stopped'
                                                                  'due to condition not satisfied in processeing MO')

    @api.multi
    def cancel_request(self):
        for req in self:
            if self.state == 'done':
                raise  osv.except_osv(_('Warning!'), _('Cannot cancel the request that is already processed.'))
            self.write({'state': 'cancel'})

    @api.one
    def get_products(self):
        "Returns Products recordset for provided shared Product id "
        product_obj = self.env['product.product']
        # shared_product_id = self._context.get('product_id', False)
        products = product_obj.search([('shared_product_id', '=', self.shared_product_id)])
        return products

    @api.one
    def run(self):
        """
        This method will run the WC Request.
        :return:
        """
        # print "self++++",self
        if self.state in ('cancel', 'done'):
            raise Warning(_('Cannot Process the Cancelled/Done Request!'))
        # print "context+rn manula++++++++=",self._context.get('run_manual', False)
        if self._context.get('run_manual', False):
    #  In case we are running manually from UI through button.
            if self.state not in ('exception', 'new'):
                raise Warning(_('You can process request only if it is in New or Exception state!'))

            context = self.env.context.copy()
            context.update({'batch_id':self.batch_id and self.batch_id.id or False,'product_id':self.shared_product_id,
                                 'product_qty':self.product_qty,
                                 'lot':self.lot_name, 'wc_id': self.wc_id})
            self.env.context = context

            # self.with_context(batch_id=self.batch_id and self.batch_id.id or False,product_id = self.shared_product_id,
            #                      product_qty =self.product_qty,
            #                      lot = self.lot_name, wc_id = self.wc_id)
        mrp_obj = self.env['mrp.production']
        mrp = mrp_obj.browse([self._context.get('batch_id', False)])
        # print "mrp+++_context+++",mrp,self._context.get('batch_id', False)
        if mrp.state == 'cancel':
            self.message_post(body=_('The Batch is Cancelled! Cannot Procced '))
            #Do not proceed
            self.write({'state':'exception'})
            return True
        # print "mrp.state++++++++=",mrp.state
        if mrp.state == 'draft':
            # print "workflow++++++++"
            # mrp.signal_workflow('button_confirm')
            # mrp.action_assign()
            mrp.confirm_check()

        products = self.get_products()
        products = products[0] if isinstance(products, (list, tuple)) else products
        if not products :
            self.message_post(body=_('No Product found for the given Shared Product Id.'))
                #Do not proceed in case of any error
            self.write({'state':'exception'})
            return True
            # return {'error':'No Product found for the given Shared Product Id.'}
        if len(products) > 1:
            self.message_post(body=_('Multiple products found with same shared ID.'))
                #Do not proceed in case of any error
            self.write({'state':'exception'})
            return True
            # return {'error':'Multiple products found with same shared ID.'}
        # check if the move exists in Batch or not
        move = mrp.check_move(products)
        move = move[0] if isinstance(move, (list, tuple)) else move
        if not move:
            self.message_post(body=_('Either the Raw Mateial %s in batch %s is already consumed or else does not exist in BOM'%(products[0].name, mrp.name)))
                #Do not proceed in case of any error
            self.write({'state':'exception'})
            # return {'error': 'Either the Raw Mateial %s in batch %s is already consumed or else does not exist in BOM'%(products[0].name, self.name)}
            return True
        if not self.done_picking:
            result = self.check()
            # print "returning to heck the picking output"
            # return True
            if isinstance(result, list):
                result = result[0]
            if isinstance(result, dict):
                # err = result.get('error','')
                # print 'errrrr++++',err
                self.message_post(body=_(result.get('error','')))
                #Do not proceed in case of any error
                self.write({'state':'exception'})
                return True
            else:
                po_picking_id, products, so_picking_id = result
            # print "picking_id, products, so_id", po_picking_id, products, so_picking_id
            #process the PO & SO
            # self.sudo().drive_order(po_picking_id, so_picking_id, products)
            self.write({'done_picking': True})
        #if stat is true then operation is done properly in case of international or not international raw material type.
        # if not stat:
        #     # NO PO found for International Raw material else No picking in Assigned state for the PO found.
        #     po_obj.drive_po(picking_id, products)
        #     return True
        # mrp.with_context(from_mrp_batch = True)
        # context = self.env.context.copy()
        # context.update({'force_company':False })
        # self.env.context = context
        mrp.with_context(force_company = 1).confirm_check()
        # mrp.refresh()
        # mrp = mrp_obj.browse([self._context.get('batch_id', False)])
        res = mrp.sudo().auto_consume_line()
        # print "resSSS+++++++++",res
        if isinstance(res[0], dict):
            # print " in isinstance+++++",res[0].get('error','')
            # self.message_post(self._cr, self._uid, [self.id], body=_('The move for product Neutral Accumag AM-9033 in batch D1150018 is not in assigned state'), context=self._context)
            self.message_post(body=_(res[0].get('error','')))
            # No Move with this product found in assigned state
            self.write({'state': 'exception'})
            return True

        self.write({'state': 'done'})

    @api.model
    def check(self):
        '''This method is used for validation before flow starts and returns Picking_id

        :return: picking_id in assigned state from earliest PO
                so_id related to PO
        '''
        so_picking_id, po_picking_id = False, False
        po_obj = self.env['purchase.order']
        pol_obj = self.env['purchase.order.line']
        product_obj = self.env['product.product']

        # shared_product_id = self._context.get('product_id', False)
        # products = product_obj.search([('shared_product_id', '=', shared_product_id)])
        products = self.get_products()
        products = products[0] if isinstance(products, (list, tuple)) else products



        # Checking only for international raw materials
        # Checking if the said Serial Number actually exists in our system for fetching in SO
        # Not checking for PO as if not found then it will be created in Compuestos.
        stock_prod = self.env['stock.production.lot']
        # if products.is_international:
        #     # return {'error': 'International flow stopped to correct issues.'}
        #     lot_id = stock_prod.get_lot_wc(products)
        #     if not lot_id:
        #         return {'error': 'No such Serial Number %s found for processing SO in Plasco'%(self._context.get('lot', False))}
        # else:
        # searching with for_so=True as it does only the searching by actual serial no. rather than COMP+Sr.no. and fulfilling our purpose
        lot_id = stock_prod.get_lot_wc(products)
        if not lot_id:
            return {'error': 'No such Serial Number %s found for processing in case of Local Raw Material'%(self._context.get('lot', False))}
        # if products and not products[0].is_international:
        #     return po_picking_id, products, so_picking_id
        # company_id = self.env['res.company'].search([('is_manufacturing_company', '=', True )])
        # # ,('state', '=', 'approved')
        # pol_s = pol_obj.search([('product_id', '=', products[0].id),('company_id', '=', company_id[0].id)])
        # po_s = [pol.order_id for pol in pol_s if pol.order_id.state == 'approved']
        #
        # # print "poss++++++",po_s
        # if not po_s:
        #     return {'error': 'No Po found for Product %s'%(products[0].name)}
        # # Finding PO with minimum date
        # dts = [datetime.datetime.strptime(po.date_order,'%Y-%m-%d %H:%M:%S') for po in po_s]
        # dt = min(dts)
        # dts_dct = dict([(datetime.datetime.strptime(po.date_order,'%Y-%m-%d %H:%M:%S'),po) for po in po_s])
        # po = dts_dct.get(dt)
        #
        # plas_company_id = self.env['res.company'].search([('name', '=', 'Productos Plasco SA de CV' )])
        #
        # #Finding the Picking for PO
        # pick_ids = []
        # pick_ids += [picking.id for picking in po.picking_ids if picking.state == 'assigned']
        # if not pick_ids:
        #     return {'error': 'No Picking found for PO %s'%(po.name)}
        # if len(pick_ids)>1:
        #     return {'error':'More then 1 picking found for PO %s'%(po.name)}
        # po_picking_id = pick_ids[0]
        #
        # #Find related Sales Order
        # so_s = []
        # for line in po.sale_line_ids:
        #     if line.company_id.id == plas_company_id.id:
        #         so_s.append(line)
        # if len(so_s) > 1:
        #     return {'error':'More then 1 related SO found for PO %s'%(po.name)}
        # if not so_s:
        #     return {'error':'No related SO found for PO %s'%(po.name)}
        # so = so_s[0]
        #
        # #Finding the Picking for SO
        # so_pick_ids = []
        # so_pick_ids += [picking.id for picking in so.picking_ids if picking.state not in ('done', 'cancel')]
        #
        # if not so_pick_ids:
        #     return {'error': 'No Picking found for SO %s in assigned state.'%(so.name)}
        # if len(so_pick_ids)>1:
        #     self.message_post(body=_('More then 1 picking found for SO %s , using 1st one %s.'%(so.name, so_pick_ids[0])))
        # so_picking_id = so_pick_ids[0]
        #
        # # self.with_context(force_company = plas_company_id)
        # # sending force_company as Plasco to make the move assigned of SO's picking
        # context = self.env.context.copy()
        # context.update({'force_company':plas_company_id.id })
        # self.env.context = context
        # # print "self._context+++0000++",str(self._context) +"\n" + str(self.env.context)
        # so_picking = self.env['stock.picking'].browse(so_picking_id)
        # st = so_picking.state
        # if st == 'waiting' :
        #     # print "b4 reresreving+++++++"
        #     self.pool.get('stock.picking').rereserve_pick(self._cr, self._uid, [so_picking_id], self._context )
        #     # self.env['stock.picking'].rereserve_pick( [so_picking_id])
        #     so_picking = self.env['stock.picking'].browse(so_picking_id)
        #     # print "state after rereserving",so_picking.state
        #
        # if st in ('draft','confirmed', 'partially_available'):
        #     # print "plas_company_id+++++++",plas_company_id
        #     # so_picking.with_context(force_company = plas_company_id)
        #     # print "self._contex++++++++++",self._context
        #     self.pool.get('stock.picking').action_assign(self._cr, self._uid, [so_picking_id], self._context )
        #     # print "so picking state++++++++++++",so_picking.state
        #     # self.with_context(force_company = False)
        # context = self.env.context.copy()
        # context.update({'force_company':False })
        # self.env.context = context
        return po_picking_id, products, so_picking_id

    @api.model
    def drive_order(self, po_picking_id, so_picking_id, products):
        stock_pick_obj = self.env['stock.picking']

        # Purchase flow to be done only for international raw materials
        if products and not products[0].is_international:
            return True
        # #Check if the quantity is already available in Compuestos stock for International raw material
        # self._cr.execute('select sum(qty) from stock_quant where location_id = 12 and product_id = %s and reservation_id is null'%products[0].id)
        # # print "cr execteue",self._cr.fetchone()
        # fetch = self._cr.fetchone()
        # # print "ftetch++++",fetch
        # stock_qty = fetch and fetch[0] or False
        # # print "stock wty++++++++",stock_qty
        # if stock_qty and stock_qty >= self.product_qty:
        #     # print "condition satisfied"
        #     return True

        # print "picking id++++++++++",po_picking_id, so_picking_id
        #processing picking attached to SO
        stock_pick_obj.with_context(for_po = False, for_so = True).process_picking(so_picking_id)
        #processing picking attached to PO i.e Input Loc in case of 3 step receipt
        stock_pick_obj.with_context(for_po = True, for_so = False).process_picking(po_picking_id)
        
        # #processing chained picking  i.e pick from Input -> QC and QC -> Stock Loc in case of 3 step receipt
        # picking_obj = self.env['stock.picking']
        # picking = picking_obj.browse(picking_id)
        # group_id = picking.group_id.id
        # po_s = self.search([('product_id', '=', products[0].id),('state', '=', 'approved')])
        # print "pos picking ids++++++",po_s.picking_ids
        # # First processing assigned or partially available pickings i.e Input -> QC
        # chained_assigned_picking_ids = [picking.id for picking in picking_obj.search([('group_id', '=', group_id)]) or [] \
        #                        if picking.state in ('assigned', 'partially_available') and \
        #                        picking.id not in [picking.id for picking in po_s.picking_ids] ]
        #
        # print "chained_assigned_picking_ids++", chained_assigned_picking_ids
        # for pick_id in chained_assigned_picking_ids:
        #     self.process_picking(pick_id)
        #
        # # Then processing QC -> Stock Loc
        # chained_wait_picking_ids = [picking.id for picking in picking_obj.search([('group_id', '=', group_id)]) or [] \
        #                        if picking.state in ('waiting') and \
        #                        picking.id not in [picking.id for picking in po_s.picking_ids] ]
        # print "chained_wait_picking_ids++", chained_wait_picking_ids
        # for pick_id_wait in chained_wait_picking_ids:
        #     self.process_picking(pick_id_wait)

        return True
