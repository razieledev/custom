from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import json


class _formula_c1(osv.osv):

    '''Below is the required format for WC
        {"Formula":"SBT4000-B004,2000056", "bom_lines":"RP0002,1,13.41,AD0009,100009,10.15,AD0029,100029,0.5,
            CA0002,200001,0.2,CA0003,200002,0.2,IN0004,300003,0.02,DE0001,400000,1,
            PI0001,500000,0.008,MI0005,600004,61.512,RE0006,800005,13","customer":1,"version":0}


        The bom_lines has 3 values for each row, and must continued in the same string (as in the example)

        1.- RawMaterial Code
        2.- Identifier
        3.- Percentage
    '''

    _inherit = 'formula.c1'

    def get_bom_data(self, cr, uid, product_dict):
        "This method will return list of, bom_data dictionary which will have bom_line_data in it.\
        The data formaat is developed to communicate with Weight center."
        # The below list will contain bom's data for multiple product
        def qty_percent(product,bom_qty, qty):
            '''
            this function gives percentage of qty depending upon product type
            :param product: This  is the BOM Product
            :param qty: This is the Bom Line Quatity
            :param bom_qty: This tis the actual BOM Quantity
            :return: Percentage of line qty required
            '''

            percent = False
            if product.product_type != 'premix':
                percent = qty * 100.0
            else:
                percent = (qty/float(bom_qty)) * 100.0

            return percent

        # if isinstance(product_ids, (int, long)): ids = [product_ids]
        bom_list = []
        bom_data = {}
        bom_lines_data = []
        product_obj = self.pool.get('product.product')
        product = product_obj.browse(cr, uid, product_dict.get('product_id', False)) \
                if product_dict.get('product_id', False) else False

        premix = product_obj.browse(cr, uid, product_dict.get('premix_id', False)) \
                if product_dict.get('premix_id', False) else False

        if not product.default_code:
                raise osv.except_osv(_('Error!'), _('Please enter Internal Reference for %s.'% product.name))
        formula = [str(product.default_code) if product else False, str(product.shared_product_id) if product else False,
                   str(premix.shared_product_id) if premix else False]

        bom_data.update({'Formula' : ','.join(formula)})

        for prod in [premix, product]:

            bom_ids = self.pool.get('mrp.bom').search(cr, uid, [('product_id', '=', prod.id)])
            if not bom_ids: return bom_lines_data
            bom = self.pool.get('mrp.bom').browse(cr, uid, bom_ids[0])
            bom_qty = bom.product_qty
            for line in bom.bom_line_ids:
                if not line.product_id.shared_product_id:
                    raise osv.except_osv(_('Error!'), _('No Shared Product Id Assigned to product %s'%(line.product_id.name)))
                if not line.product_id.default_code:
                    raise osv.except_osv(_('Error!'), _('Please enter Internal Reference for %s.'% line.product_id.name))
                if line.product_id and not line.product_id.product_type == 'premix':
                    bom_lines_data += [str(line.product_id.default_code) or '', str(line.product_id.shared_product_id),
                                       str(qty_percent(product, bom_qty, line.product_qty))]
                else:
                    continue
        bom_data.update({"bom_lines": ','.join(bom_lines_data), "customer":1, "version":product.formula_id.count})
        bom_list.append(bom_data)

        return bom_list

    def make_products_data(self, cr, uid, product_dict, context = None):
        'This function will return the list of products data for WC'
        bom_list = self.get_bom_data(cr, uid,product_dict)
        # for product in self.pool.get('product.product').browse(cr, uid, product_ids):
        #     # shared +=1
        #     # data = {}
        #     # if not product.shared_product_id:
        #     #     raise osv.except_osv(_('Error!'), _('No Shared Product Id Assigned to product %s'%(product.name)))
        #     bom_list = self.get_bom_data(cr, uid,[product.id])
        #     # data.update({
        #     #     product.shared_product_id : {
        #     #                                         'name': product.name,
        #     #                                         'BOM' :bom_list and bom_list[0] or {},
        #     #                                         }
        #     #             })
        #     # data_list.append(bom_list and bom_list[0])
        return bom_list

    def export_product(self, cr, uid, ids, context=None):
        '''
        This method exports the Product data to WC in the required format.
        :param cr:
        :param uid:
        :param ids:
        :param context:
        :return:

        Required Format:{"Formula": "product internal reference, products shared product id, premix shared product id",
                        "bom_lines":"line1.product_id,line1.product_id.shared_pro_id,line1.qty,line2...",
                        "customer":Does this Formula has a customer attached, "version": Formula Revision Number}
        Note: bom_lines has lines of both premix and product
        Example:       '{"Formula":"SBT4000-B004,3000001,3000000", "bom_lines":"RP0002,1,13.41,AD0009,100009,10.15,
                        AD0029,100029,0.5","customer":1,"version":12}'
        '''
        if not context: context = {}
        if isinstance(ids, (int, long)): ids = [ids]
        for formula in self.pool.get('formula.c1').browse(cr, uid, ids):
            prods_dict = {}
            if context.get('export_lp',False) == True:
                print "in export lp++++++++++"
                prod_id = formula.product_lp_variant and formula.product_lp_variant.id or False
                premix_id = formula.product_premix_variant and formula.product_premix_variant.id or False
                if not prod_id: raise osv.except_osv(_('Error!'), _('There is no LP to be sent.'))
            elif context.get('export_product',False) == True:
                print "in export product++++++++++"
                prod_id = formula.final_product_id and formula.final_product_id.id or False
                premix_id = formula.final_premix_id and formula.final_premix_id.id or False
                if not prod_id: raise osv.except_osv(_('Error!'), _('There is no Final Product to be sent.'))
            if premix_id: prods_dict.update({'premix_id': premix_id})
            if prod_id: prods_dict.update({'product_id': prod_id})
            data_list = self.make_products_data(cr, uid, prods_dict)
            for data in data_list:
                print "\n\n\n",data

                    # {'pro_temp_lp': pro_id and pro_id[0], 'pro_temp1_premix': pro_id1 and pro_id1[0],
            #  'pro_variant_lp':product_id and product_id[0], 'pro_variant_premix': product_id1 and product_id1[0]}
            weigh_center = self.pool.get('weigh.center')
            weigh_id = weigh_center.get_add_formula_web_service_id(cr, uid, context)
            if not weigh_id:
                raise osv.except_osv(_('Error!'), _('No WC Add Formula Configuration/URL defined or Active.'))

            print "weich Id+++++++++",weigh_id
            # return True
            # context = context.update({'is_not_json': False})
            if data_list:
                for data in data_list:
                    res = weigh_center.send_data(cr, uid, weigh_id, data, context = context)
            # if isinstance(res, dict) and res.get('error', False):
            #     raise osv.except_osv(_('Error!'), _('"%s".') % res.get('message', ''))
        return True
