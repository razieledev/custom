from openerp import models, fields, api, _
from lxml import etree


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.one
    @api.depends('state')
    def _get_invoice_pick_state(self):
        invoice_obj = self.env['account.invoice']
        invoice_id = invoice_obj.search([('name', 'ilike', self.name)])
        if invoice_id:
            for invoice in invoice_id:
                if invoice.state:
                    self.inv_state = invoice.state
        pick_obj = self.env['stock.picking']
        picking_id = pick_obj.search([('origin', 'ilike', self.name)])
        for picking in picking_id:
            if picking.state:
                self.pick_state = picking.state

    pick_state = fields.Selection(
                [('draft', 'Draft'),
                ('cancel', 'Cancelled'),
                ('waiting', 'Waiting Another Operation'),
                ('confirmed', 'Waiting Availability'),
                ('partially_available', 'Partially Available'),
                ('assigned', 'Ready to Transfer'),
                ('done', 'Transferred'),],
    'Picking State', compute='_get_invoice_pick_state', track_visibility='onchange', select=1)
    inv_state = fields.Selection(
    [
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Cancelled'),
        ],
    'Invoice State', compute='_get_invoice_pick_state', track_visibility='onchange', select=1)
    pedimentos_id = fields.Many2one('pedimentos', string='Pedimentos')
    # ref_po_id = fields.Many2one('purchase.order', string='Reference PO')
    # sale_line_ids = fields.One2many('sale.order', 'ref_po_id', string='Related sales orders')
    # purchase_line_ids = fields.One2many('purchase.order', 'ref_po_id', string='Related Purchase orders')

    # @api.model
    # def fields_view_get(self, view_id=None, view_type=False, toolbar=False,
    #                     submenu=False):
    #     res = super(PurchaseOrder, self).fields_view_get(
    #         view_id=view_id, view_type=view_type, toolbar=toolbar,
    #         submenu=submenu)
    #     if self._context.get('smc') or self._context.get('plasco') or self._context.get('compuestos'):
    #         if view_type == 'tree':
    #             doc = etree.XML(res['arch'])
    #             nodes = doc.xpath("//tree[@string='Purchase Order']")
    #             for node in nodes:
    #                 node.set('create', "false")
    #                 node.set('edit', "false")
    #             res['arch'] = etree.tostring(doc)
    #         if view_type == 'form':
    #             doc = etree.XML(res['arch'])
    #             nodes = doc.xpath("//form[@string='Purchase Order']")
    #             for node in nodes:
    #                 node.set('create', "false")
    #                 node.set('edit', "false")
    #             res['arch'] = etree.tostring(doc)
    #     return res

#    def default_get(self, cr, uid, fields, context=None):
#        res = super(PurchaseOrder, self).default_get(cr, uid, fields, context)
#        company_id = res.get('company_id')
#        type_obj = self.pool.get('stock.picking.type')
#        types = type_obj.search(cr, uid, [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)], context=context)
#        if not types:
#            types = type_obj.search(cr, uid, [('code', '=', 'incoming'), ('warehouse_id', '=', False)], context=context)
#            if not types:
#                raise osv.except_osv(_('Error!'), _("Make sure you have at least an incoming picking type defined"))
#        if types:
#            res['picking_type_id'] = types
#        return res

# class product_supplierinfo(models.Model):
#
#     _inherit = "product.supplierinfo"
#
#     product_tmpl_id = fields.Many2one('product.template', 'Product Template', required=False, ondelete='cascade', select=True, oldname='product_id')
#     temp_id = fields.Many2one('product.category', string='temp')


# class product_category(models.Model):
#
#     _inherit = 'product.category'
#
#     seller_ids = fields.One2many('product.supplierinfo', 'temp_id', string='Supplier Info for product')


# class product_template(models.Model):
#
#     _inherit = 'product.template'
#
#     raw_material = fields.Boolean(string='Purchase Configuration', help='Setting this field to true will bring '
#                                                                  'configuration of suppliers from Product Category.')
#
#     @api.onchange('categ_id', 'raw_material')
#     def onchange_cat(self):
#         if self.categ_id and self.raw_material:
#             seller_list = []
#             for seller in self.categ_id.seller_ids:
#                 seller_list.append((4, seller.id))
#             self.seller_ids = seller_list
#         elif not self.raw_material:
#             self.seller_ids = [(5, 0)]
#
#
# class product_product(models.Model):
#
#     _inherit = 'product.product'
#
#     @api.onchange('categ_id', 'raw_material')
#     def onchange_cat(self):
#         if self.categ_id and self.raw_material:
#             seller_list = []
#             for seller in self.categ_id.seller_ids:
#                 seller_list.append((4, seller.id))
#             self.seller_ids = seller_list
#         elif not self.raw_material:
#             self.seller_ids = [(5, 0)]


class procurement_order(models.Model):

    _inherit = 'procurement.order'

#     @api.cr_uid_context
#     def create_procurement_purchase_order(self, cr, uid, procurement, po_vals, line_vals, context=None):
#         so_name = procurement.group_id.name
#         so_id = self.pool.get('sale.order').search(cr, uid, [('name', '=', so_name)])
#         if  isinstance(so_id, (list, tuple)): so_id = so_id[0]
#         so = self.pool.get('sale.order').browse(cr, uid, so_id)
# #        Bringing refrence Po Id in case of automatic inter company flow
#         if so.auto_generated :
#             po_vals.update({'ref_po_id': so.ref_po_id.id})
#         # # In case of Dropshipping flow automatically making PO's Invoice method as 'picking' to adhere flow of stock_dropshipping_dual_invlice module
#         if so.company_id and so.company_id.name == 'SMC COMPOSITES SA DE CV':
#             if so.order_policy == 'picking':
#                 po_vals.update({'invoice_method': 'picking'})
#         res = super(procurement_order, self).create_procurement_purchase_order(cr, uid, procurement, po_vals, line_vals, context=context)
#         po_obj = self.pool.get('purchase.order')
#         company_id = po_obj.browse(cr, uid, res).company_id
#         #Auto confirming PO's created through procurement except for Company SMC Comp Inc (USA)
#         # # SMC COMPOSITES SA DE CV In case of Dropshipping flow need to make PO's Invoice method as 'picking' to adhere flow of stock_dropshipping_dual_invlice module
#         if company_id and company_id.name == 'SMC Comp Inc (USA)':
#             return res
#         return res

    # @api.cr_uid_ids_context
    # def make_po(self, cr, uid, ids, context=None):
    #     """
    #     Stopping flow to create PO in Compuestos in case of Drop shipping flow as product is MTO and Buy.
    #     :param cr:
    #     :param uid:
    #     :param ids:
    #     :param context:
    #     :return:
    #     """
    #     res = {}
    #     for procurement in self.browse(cr, uid, ids, context=context):
    #         ctx_company = dict(context or {}, force_company=procurement.company_id.id)
    #         partner = self._get_product_supplier(cr, uid, procurement, context=ctx_company)
    #         # if Partner and company is same then return
    #         if partner and partner.name == procurement.company_id.name:
    #             res[procurement.id] = False
    #             return res
    #         res = super(procurement_order, self).make_po(cr, uid, ids, context=context)
    #         po_lines = self.pool.get('purchase.order.line').browse(cr, uid, res.values(), context=context)
    #         for po in po_lines.mapped('order_id'):
    #             if po.company_id and po.company_id.name in ('SMC Comp Inc (USA)'):
    #                 continue
    #             po.signal_workflow('purchase_confirm')
    #         return res

    @api.cr_uid_context
    def _get_po_line_values_from_proc(self, cr, uid, procurement, partner, company, schedule_date, context=None):
        vals = super(procurement_order, self)._get_po_line_values_from_proc(cr, uid, procurement=procurement, partner=partner, company=company, schedule_date=schedule_date, context=context)
        uom_obj = self.pool.get('product.uom')
        pricelist_obj = self.pool.get('product.pricelist')
        seller_qty = procurement.product_id.seller_qty if procurement.location_id.usage != 'customer' else 0.0
        pricelist_id = partner.property_product_pricelist_purchase.id
        currency = pricelist_obj.browse(cr, uid, pricelist_id).currency_id
        uom_id = procurement.product_id.uom_po_id.id
        qty = uom_obj._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, uom_id)
        if seller_qty:
            qty = max(qty, seller_qty)
        price = pricelist_obj.price_get(cr, uid, [pricelist_id], procurement.product_id.id, qty, partner.id, dict(context, uom=uom_id))[pricelist_id]
        if price == 0.0 and procurement:
            if currency:
                if currency.id == procurement.product_id.cost_price_currency_id.id:
                    price = procurement.product_id.standard_price or 0.0
                elif currency.id == procurement.product_id.cost_price_type_currency_id.id:
                    price = procurement.product_id.cost_price_on_list_price_type_currency or 0.0
                else:
                    price = 0.0
        if 'price_unit' in vals:
            vals.update({'price_unit': price})
        return vals
