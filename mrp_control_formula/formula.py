# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from lxml import etree
import openerp.addons.decimal_precision as dp
import openerp.exceptions
from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import xmlrpclib
import datetime

class _formula_c1(osv.osv):
    _name = 'formula.c1'
    _description = 'Formula'
    _inherit = ['mail.thread']
    _rec_name = 'count'

    def mymod_confirmed(self, cr, uid, ids, context=None):
        #action_reformla=False
        #action_reformla=self.action_reformular(cr, uid,ids, context=context)
        self.write(cr, uid, ids, { 'state' : 'Confirmed' }, context=None)
        return True

    def mymod_reformu(self, cr, uid, ids, context=None):
        action_reformla=False
        action_reformla=self.action_reformular(cr, uid,ids, context=context)
        self.write(cr, uid, ids, { 'state' : 'Reformulacion' },context=None)
        return True

    def mymod_p(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'Pruebas' }, context=None)
        return True

    def action_formulaenvio(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'formulaenviar' }, context=None)
        formula_obj=self.pool.get('formula.c1')
        formula_brw = self.pool.get('formula.c1').browse(cr, uid, ids)
#        if formula_brw.final_product_id or formula_brw.final_premix_id:
#            raise osv.except_osv(_('Error!'), _('You Can not validate this formula because Final Product and Final Premix set. If you want to update BOM please use update button'))
        formula_ids=formula_obj.search(cr,uid,[('state','in',('Confirmed','Reformulacion'))])
        return{
            'domain':"[('id','in',["+','.join(map(str,formula_ids))+"])]",
            'name':('Formulas'),
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'formula.c1',
            'view_id':False,
            'type':'ir.actions.act_window'
        }
        #return True

    def mymod_l(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'L' }, context=None)
        return True

#    def create(self, cr, uid, vals, context=None):
#        if vals.get('cod_formula','/')=='/':
#            vals['cod_formula'] = self.pool.get('ir.sequence').get(cr, uid, 'code-formula') or '/'
#        return super(_formula_c1, self).create(cr, uid, vals, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'date': fields.date.context_today(self, cr, uid, context=context),
            'state': 'Confirmed',
            'client': '',
            'cod_formula': self.pool.get('ir.sequence').get(cr, uid, 'code-formula'),
        })
        return super(_formula_c1, self).copy(cr, uid, id, default, context=context)

    def button_dummy(self, cr, uid, ids, context=None):
        return True

    def _convertkg(self,cr,uid,ids,field_name, arg, context=None):
        records=self.browse(cr,uid,ids,)
        resu={}
        for r in records:
            resu[r.id] = (r.n_cantidad * 1000)
        return resu

    def _total(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)
        res = {}
        for r in records:
            res[r.id] = 0
            for line in r.line:
                res[r.id] += line.cantidadproduct
        return res

    def _costo(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)
        res = {}
        for r in records:
            res[r.id] = 0
            for line in r.line:
                res[r.id] += line.cantidadcoste
        return res

    def _totalporcentaje(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)
        ress = {}
        for r in records:
            ress[r.id] = 0
            for line in r.line:
                ress[r.id] += line.calculate_porcentaje
        return ress

    def _costo_indirecto(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)
        res = {}
        for r in records:
            res[r.id] = 0
            for line in r.line:
                res[r.id] += line.costotal
        return res

    def _totalpventa(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)
        ress = {}
        for r in records:
            ress[r.id] = 0
            for line in r.line:
                ress[r.id] += line.p_venta
        return ress

    def _totaltpv1(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)
        ress = {}
        for r in records:
            ress[r.id] = 0
            for line in r.line:
                ress[r.id] += line.pzc1
        return ress

    def _totaltpv2(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)
        ress = {}
        for r in records:
            ress[r.id] = 0
            for line in r.line:
                ress[r.id] += line.pzc2
        return ress

    def _funcion_validacionporcentaje(self, cr, uid, ids, context=None):
        records = self.browse(cr, uid, ids)
        for r in records:
            if r.totalP > r.n_total:
                return False
        return True

    _constraints = [
        (_funcion_validacionporcentaje, ('A pasado el 100%'), ['n_total'])
    ]

    def _funcion_validacionkg(self, cr, uid, ids, context=None):
        records = self.browse(cr, uid, ids)
        for r in records:
            if r.n_cantidad <=0:
                return False
        return True

    _constraints = [
        (_funcion_validacionkg, ('Ingrese Cantidad en KG'), ['kg'])
    ]

    def lines_formula(self, cr, uid,ids,context=None):
        formulas_envio=False
        model_conec = self.pool.get('openerp.rpc').search(cr, uid, [('state', '=', 'conectado')])
        resu=model_conec[0] or False
        conect_obj = self.pool.get('openerp.rpc').browse(cr, uid, resu, context=context)
        destinobd=conect_obj.db_destino
        destinouser=conect_obj.user_destino
        destinopasword=conect_obj.pass_destino
        sock_common = xmlrpclib.ServerProxy ('http://0.0.0.0:8069/xmlrpc/common')
        conection = sock_common.login(destinobd, destinouser, destinopasword)
        sock = xmlrpclib.ServerProxy('http://0.0.0.0:8069/xmlrpc/object')
        for formula in self.browse(cr, uid, ids, context=context):
            formulas_envio=self.action_envioxmlrpc(cr, uid,ids,formula, context=context)
            idenvio = formula.idcreado
            linesformula = formula.line
            for idlines in linesformula:
                product_ids=idlines.producto.name
                porcentaje=idlines.calculate_porcentaje
                ingredentes= [('name', '=',product_ids)]
                idingredientes = sock.execute(destinobd, conection, destinopasword, 'product.product', 'search', ingredentes)
                ingredientes_ids=idingredientes[0]
                #raise osv.except_osv(("Hola"),str(ingredientes_ids))
                valune_lines={
                    'formula_id':idenvio,
                    'producto':ingredientes_ids,
                    'calculate_porcentaje':porcentaje,
                }
                new_lines = sock.execute(destinobd, conection,destinopasword,'mrpformul00','create',valune_lines)
                #self.write(cr, uid, ids, { 'mp_state' :'Solicitado'}, context=context)
            return True

    def action_envioxmlrpc(self, cr, uid, ids, formula, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        formula_obj = self.pool.get('formula.c1')
        model_conec = self.pool.get('openerp.rpc').search(cr, uid, [('state', '=', 'conectado')])
        resu=model_conec[0] or False
        conect_obj = self.pool.get('openerp.rpc').browse(cr, uid, resu, context=context)
        destinobd=conect_obj.db_destino
        destinouser=conect_obj.user_destino
        destinopasword=conect_obj.pass_destino
        sock_common = xmlrpclib.ServerProxy ('http://0.0.0.0:8069/xmlrpc/common')
        conection = sock_common.login(destinobd, destinouser, destinopasword)
        sock = xmlrpclib.ServerProxy('http://0.0.0.0:8069/xmlrpc/object')
        args = [('name', '=',wizard._cliente.name)]
        idpartner = sock.execute(destinobd, conection, destinopasword, 'res.partner', 'search', args)
        partner_id=idpartner[0]
        arg_familia = [('name', '=',wizard.familia.name)]
        idfamily = sock.execute(destinobd, conection, destinopasword, 'family', 'search', arg_familia)
        family_id=idfamily[0]
        #raise osv.except_osv(("Hola"),str(idfamily))
        value_formula = {
            '_cliente':partner_id,
            'familia':family_id,
            'n_cantidad':1,
            'state':'Confirmed',
            'name':'agus',
            }
        creteremote_id = sock.execute(destinobd, conection,destinopasword, 'formula.c1', 'create', value_formula)
        #raise osv.except_osv(("Hola"),str(creteremote_id))
        self.write(cr,uid,ids,{'idcreado':creteremote_id},context=context)
        return True
    # def action_reformular(self, cr, uid, ids, context=None):
    #     cont=0
    #     for this in self.browse(cr, uid, ids, context=context):
    #         cont=this.count+1
    #         this.write({'count':+cont})
    #     return True
    def lines_reformula_local(self, cr, uid,ids,context=None):
        formulas_envio=False
        reformula_obj  = self.pool.get('mrpformul00')
        for reformulacion in self.browse(cr, uid, ids, context=context):
            formulas_envio = self.action_reformular(cr, uid,ids,reformulacion, context=context)
            linesformula = reformulacion.line
            idcreate=reformulacion.idcreado_local.id
            for idsline in linesformula:
                result={
                    'formula_id':idcreate,
                    'producto':idsline.producto.id,
                    'calculate_porcentaje':idsline.calculate_porcentaje,
                    'premix': idsline.premix
                }
                new_lot_id = reformula_obj.create(cr, uid,result)
            return True

    def action_reformular(self, cr, uid, ids,reformulacion, context=None):
        cont=0
        reformula_obj = self.pool.get('formula.c1')
        wizard = self.browse(cr,uid,ids[0],context=context)
        cont=wizard.count+1
        values_reformula = {
            '_cliente':  wizard._cliente.id,
            'familia':  wizard.familia.id,
            'name':wizard.name,
            'product_color':wizard.product_color.id,
            'process':wizard.process,
            'n_cantidad':1,
            'count':+cont,
            'state':'Reformulacion',
            'cost_date': wizard.cost_date,
            'move_ids':[],
            'product_type': wizard.product_type,
            'final_product_id': wizard.final_product_id.id,
            'final_premix_id': wizard.final_premix_id.id,
         }
        new_refor = reformula_obj.create(cr, uid, values_reformula)
        self.write(cr, uid, ids, { 'idcreado_local': new_refor, 'state': 'enviadorefor'}, context=context)
        return True

    def get_bom_lines(self, cr, uid,formula_brw, premix = False, context = None):
        bom_lines = []
        kg_uom_id = self.pool.get('product.uom').search(cr, uid, [('name', '=', 'kg')], limit=1)
        if not premix:
            #  Counting the quantity of premixes in Formula lines
            premix_qty = sum([line.cantidadproduct for line in formula_brw.line if line.premix == True]) or 0
            premix_prod_id = context.get('premix_prod_id', False)
            if (premix_qty > 0) and not premix_prod_id:
                raise osv.except_osv(_('Error!'), _('No Premix created even though it exits in formula lines.'))
            # In case we are creating lines for Product (not premix) we will add premix to product if present
            if (premix_qty > 0):
                bom_lines.append((0, 0, {
                        'product_id': premix_prod_id,
                        'product_uom': kg_uom_id and kg_uom_id[0],
                        'product_qty': premix_qty,
                        'product_efficiency': 1,
                        'type': 'normal'}))

        for line in formula_brw.line:
            if line.premix == premix:
                bom_lines.append((0, 0, {
                    'product_id': line.producto.id,
                    'product_uom': kg_uom_id and kg_uom_id[0],
                    'product_qty': line.cantidadproduct,
                    'product_efficiency': 1,
                    'type': 'normal'}))

        return bom_lines


    def script_update_formula(self, cr, uid,ids, context=None):
        cr.execute(" select final_product_id from formula_c1 where final_product_id is not null")
        prod_prod_ids = filter(None, map(lambda x: x[0], cr.fetchall()))
        for each_product in self.pool.get('product.product').browse(cr, uid, prod_prod_ids):
            cr.execute(" select max(id) from formula_c1 where final_product_id is not null and final_product_id=%s" % (each_product.id))
            fromual_id = filter(None, map(lambda x: x[0], cr.fetchall()))
            formula = self.browse(cr, uid, fromual_id)
            each_product.write({'formula_id': formula.id})

        return True



    def script_create_formula(self, cr, uid,ids, context = None):
#        product_ids = self.pool.get('product.product').search(cr, uid, [('categ_id' , 'in', [658,622])])
        product_ids = self.pool.get('product.product').search(cr, uid, [('product_type' , '=', 'internal')])
        for sale_ok_product in self.pool.get('product.product').browse(cr, uid, product_ids):
            bom_id = self.pool.get('mrp.bom').search(cr, uid, [('product_id', '=', sale_ok_product.id)], limit=1)
            bom = self.pool.get('mrp.bom').browse(cr, uid, bom_id)
            if bom.rev_no:
                count = bom.rev_no
            else:
                count = 1
            formula_line_obj = self.pool.get('mrpformul00')
            formula_vals = {}
            formula_line_vals = {}
            formula_vals.update({'count': count,
                                'familia':2,
                                'name':'Internal Product',
                                'product_type': sale_ok_product.product_tmpl_id and sale_ok_product.product_tmpl_id.product_type,
                                'final_product_id':sale_ok_product.id,
                            })
            formula_id = self.create(cr, uid, formula_vals)
            for bom_lin in bom.bom_line_ids:
                if not bom_lin.product_id.product_type == 'premix':
                    formula_line_vals.update({
                                            'producto':bom_lin.product_id.id,
                                            'calculate_porcentaje':bom_lin.product_qty * 100,
                                            'formula_id':formula_id,
                                            'premix':False,
                                            })
                    formula_line_obj.create(cr, uid, formula_line_vals)
                    premix_prod_id = ''
                else:
                    premix_prod_id = bom_lin.product_id.id
                    premix_bom_ids = self.pool.get('mrp.bom').search(cr, uid, [('product_id', '=', premix_prod_id)], limit=1)
                    premix_bom = self.pool.get('mrp.bom').browse(cr, uid, premix_bom_ids)
                    for each_line in premix_bom.bom_line_ids:
                        formula_line_vals.update({'producto':each_line.product_id.id,
                                                'calculate_porcentaje':each_line.product_qty * 100.0,
                                                'formula_id':formula_id,
                                                'premix':True,
                                                })
                        formula_line_obj.create(cr, uid, formula_line_vals)
                formula_id_brw = self.browse(cr, uid, formula_id)
                formula_id_brw.write({'final_premix_id':premix_prod_id,'state':'L'})
        return True



    def create_product_bom(self, cr, uid,formula_brw, tmp_id, pro_id, premix_id, revision, premix = False, context = None):
        kg_uom_id = self.pool.get('product.uom').search(cr, uid, [('name', '=', 'kg')], limit=1)
        compues_comp_id = self.pool.get('res.company').search(cr, uid, [], limit=1)
        "If the Product has premix then will have premix_id for it."
        """
        premix_id : If the Product has premix then will have premix_id for it.
        premix: Flag to say if a product is of type premix or not.
        """
        # bom_premix_list = []
        if premix_id and not premix:
            context.update({'premix_prod_id': premix_id})

        bom_lines = self.get_bom_lines(cr, uid, formula_brw, premix, context = context)
        product = self.pool.get('product.product').browse(cr, uid, pro_id)
        # product_tmp = self.pool.get('product.template').browse(cr, uid, tmp_id)
        bom_vals = {}
        if premix:
            premix_qty = sum([line.cantidadproduct for line in formula_brw.line if line.premix == True]) or 0
            bom_vals.update({'product_qty': premix_qty})
        else:
            bom_vals.update({'product_qty': 1})
        nm_lst = [str(product.name)]
        if revision:
            nm_lst.append(str(revision))
        bom_vals.update({
                    'bom_line_ids': bom_lines or False,
                    'product_tmpl_id': tmp_id,
                    'product_id': pro_id,
                    'company_id': compues_comp_id and compues_comp_id[0] or 1,
                    'type': 'normal',
                    'product_uom': kg_uom_id and kg_uom_id[0],
#                    'name': product.name + (' - ' if revision else '') + (revision if revision else '')
                    'name': ' - '.join(nm_lst)
        })
        self.pool.get('mrp.bom').create(cr, uid, bom_vals)

        return True


        # for i in formula_brw.line:
        #     # bom_premix_list.append(i.premix)
        #     # print " the premix list is as follows :::::>>>>>>>>>>>>>>>>>>>>>>", bom_premix_list
        #     if i.premix == premix:
        #         # print "\n\n\nproduct----qty", i, i.cantidadproduct
        #         # bom_premix_product += i.cantidadproduct
        #         print "\n\n\nbom_premix_product", bom_premix_product
        #         bom_line_id_premix.append([0, 0, {
        #             'product_id': i.producto.id,
        #             'product_uom': 1,
        #             'product_qty': i.cantidadproduct,
        #             'product_efficiency': 1,
        #             'type': 'normal'}])
        #
        #         print "\n\n\nbom_line_id_premix", bom_line_id_premix, bom_premix_list
        #
        #         bom_vals_premix = {
        #             'bom_line_ids': bom_line_id_premix or False,
        #             'product_tmpl_id': pro_id1[0],
        #             'product_id': product_id1[0],
        #             'product_qty': 1,
        #             'type': 'normal',
        #             'name': product_product_brow1.name or product_product_brow1.name + ' - ' + current_rev
        #         }
        #         bom_product_premix_id = self.pool.get('mrp.bom').create(cr, uid, bom_vals_premix)
        #
        #         if len(set(bom_premix_list)) == 1:
        #             bom_inactive = {
        #                 'active': False
        #             }
        #             bom_inactive_id = self.pool.get('mrp.bom').write(cr, uid, bom_product_premix_id, bom_inactive)
        #             print " the bom inactive id is ============================", bom_inactive_id
        #
        #
        # # =========  Creating the BOM for actual product without premix =======================
        #
        # # Updating the bom line ids from the product ingredients and passing that value in the bom_line values
        # if bom_premix_product > 0:
        #     bom_line_id = [[0, 0, {'product_id': product_id1[0], 'product_uom': 1, 'product_qty': bom_premix_product, 'product_efficiency': 1, 'type': 'normal'}]]
        # else:
        #     bom_line_id = [[0, 0, {'product_id': product_id1[0], 'product_uom': 1, 'product_qty': 1, 'product_efficiency': 1, 'type': 'normal'}]]


    #  Method to create the product templates and the product variants
    def create_lp(self, cr, uid, ids, context=None):
        "This function creates products of product type Formula and assigns Shared Product ID"
        # Searching the product object, product variant,  attribute and attribute values to be created
        product_obj = self.pool.get('product.template')
        product_product_obj = self.pool.get("product.product")
        product_attribute = self.pool.get('product.attribute')
        ir_confg_ob = self.pool.get('ir.config_parameter')
        prod_categ_obj = self.pool.get('product.category')
        product_attribute_value_obj = self.pool.get("product.attribute.value")
        compues_comp_id = self.pool.get('res.company').search(cr, uid, [], limit=1)
        kg_uom_id = self.pool.get('product.uom').search(cr, uid, [('name', '=', 'kg')], limit=1)
#        categ_id = self.pool.get('product.category').search(cr, uid, [('name', '=', 'All Products')], limit=1)
        product_id, pro_id, product_id1, pro_id1 = False, False, False, False
        # Searching the formula object(current object) and using the result to search the product in the product object
        formula_bro = self.browse(cr, uid, ids, context=context)
        if formula_bro.product_lp_variant or formula_bro.product_premix_variant:
            raise osv.except_osv(_('Warning!'), _('Product or Premix have already been created for this formula.'))
        # For creating the product attributes and attribute values of the product from the description field
        attribute_id = product_attribute.search(cr, uid, [('name', '=', 'Revision')])
        if not attribute_id:
            attribute_id = self.pool.get('product.attribute').create(cr, uid, {'name': 'Revision'})
        if isinstance(attribute_id, (list, tuple)):
            attribute_id = attribute_id[0]

        # getting varialbes in case of already existing Product.
        current_rev = str(formula_bro.count).zfill(5)
        # print "current revision id is >>>>>>>>>>>>>", current_rev

        pro_att_val = product_attribute_value_obj.search(cr, uid, [('name', '=', current_rev)])
        if not pro_att_val:
            pro_att_val = product_attribute_value_obj.create(cr, uid, {'attribute_id': attribute_id, 'name': current_rev})
        if isinstance(pro_att_val, (list, tuple)): pro_att_val = pro_att_val[0]

        # Searching the formula description named object in the product template pool
        pro_id = product_obj.search(cr, uid, [('name', '=', 'LP-' + formula_bro.name)])
        # print"the pro_id >>>>>>>>>>>>>", pro_id

        pro_id1 = product_obj.search(cr, uid, [('name', '=', 'LP-' + formula_bro.name + '-Premix')])
        # print "the pro_id1 is >>>>>>>>>>>>>>", pro_id1

        
        product_att_id = product_attribute_value_obj.search(cr, uid, [('attribute_id', '=', attribute_id), ('name', '=', current_rev)])
        product_att_id = product_att_id and product_att_id[0] or False

        if not product_att_id:
            product_att_id = product_attribute_value_obj.create(cr, uid, {
                'attribute_id': attribute_id, 'name': current_rev
            }, context=context)
        if isinstance(product_att_id,(list, tuple)): product_att_id = product_att_id[0]
        ####################

        # check if any premix material exist in Formulation Lines
        bool_premix = True if any([ln.premix for ln in formula_bro.line]) else False
        # For other product created in the product_name_premix
        if pro_id1 and bool_premix:
            #adding Attributes
            product_tmpl_rec1 = product_obj.browse(cr, uid, pro_id1, context=context)
            for line in product_tmpl_rec1.attribute_line_ids:
                if line.attribute_id.id == attribute_id and line.attribute_id.name == 'Revision':
                    attribute_lines_id = line.id

                if attribute_lines_id:
                    product_obj.write(cr, uid, pro_id1[0], {
                        'attribute_line_ids': [(1, attribute_lines_id, {'value_ids': [(4, product_att_id)]})]
                    }, context=context)

                else:
                    product_attribute_value_obj.create(cr, uid, {
                        'product_tmpl_id': pro_id1[0],
                        'attribute_id': attribute_id,
                        'value_ids': [(4, product_att_id)],
                    })

                # product_id1 = product_product_obj.search(cr, uid, [
                #     ('product_tmpl_id', '=', pro_id1[0]),
                #     ('attribute_value_ids', '=', product_att_id)], context=context)
                # # print " the product id of zdgxgdgdfgdg fsgsdgdfg the variant is as >>>>>>", product_id1
                # self.write(cr, uid, ids, {'product_premix_variant': product_id1[0]}, context=context)
                #
                # product_product_brow1 = product_product_obj.browse(cr, uid, product_id1, context=context)
        # If Yes and not Premix Product template then create Premix
        if (not pro_id1) and bool_premix:
            val = ir_confg_ob.get_param(cr, uid, 'LP')
            if not val:
                raise osv.except_osv(_('Warning!'), _('There is no Config Parameter define for this %s Product Type') % (formula_bro.product_type))
            else:
                if val.split(','):
                    split_val = val.split(',')
            categ_id = prod_categ_obj.search(cr, uid, [('name', '=', split_val[1])])
            # createing template and adding Attributes
            res2 = {
                'name': 'LP-' + formula_bro.name + '-Premix',
                'type': 'product',
                'product_type': 'premix',
                'company_id': compues_comp_id and compues_comp_id[0] or 1,
                'sale_ok': False,
                'state': 'draft',
                'valuation': 'real_time',
                'formula': True,
                'uom_id': kg_uom_id and kg_uom_id[0],
                'uom_po_id': kg_uom_id and kg_uom_id[0],
                'categ_id': categ_id and categ_id[0],
                'attribute_line_ids':  [(0, 0, {'attribute_id': attribute_id ,
                                                'value_ids': [(6, 0, [pro_att_val])]})]
            }
            pro_id1 = product_obj.create(cr, uid, res2, context=context)
            pro_id1 = [pro_id1]

        if pro_id1:
            # Creating BOM for Product
            # Searching the product variant ID's for creating BOM  ..
            product_id1 = product_product_obj.search(cr, uid, [
                ('product_tmpl_id', '=', pro_id1[0]),
                ('attribute_value_ids', '=', product_att_id)], context=context)

            context.update({'display_default_code': False})
            product_name = product_product_obj.name_get(cr, uid, product_id1, context=context)
            if type(product_name) == list:
                product_name = product_name[0][1]
            else:
                product_name = False
            

            product_id_bro = product_product_obj.browse(cr, uid, product_id1)
            product_id_bro.write({'formula_id': formula_bro.id, 'default_code': product_name})
            self.write(cr, uid, ids, {'product_premix_variant': product_id1 and product_id1[0]}, context=context)
            # product_product_brow1 = product_product_obj.browse(cr, uid, product_id1, context=context)
            
            asd1 = self.create_product_bom(cr, uid,formula_bro, pro_id1 and pro_id1[0], product_id1 and product_id1[0], False, current_rev, True, context = context)

        if pro_id:
            # adding Attributes
            product_tmpl_rec = product_obj.browse(cr, uid, pro_id, context=context)
            attribute_lines_id = False
            # For the product created with the actual name without the suffix - Premix
            for line in product_tmpl_rec.attribute_line_ids:
                if line.attribute_id.id == attribute_id and line.attribute_id.name == 'Revision':
                    attribute_lines_id = line.id
                if attribute_lines_id:
                    product_obj.write(cr, uid, pro_id[0], {
                        'attribute_line_ids': [(1, attribute_lines_id, {'value_ids': [(4, product_att_id)]})]
                    }, context=context)
                else:
                    product_attribute_value_obj.create(cr, uid, {
                        'product_tmpl_id': pro_id[0],
                        'attribute_id': attribute_id,
                        'value_ids': [(4, product_att_id)],
                    })

    #  Creating the product if not found in the product template pool
        if not pro_id:
            val = ir_confg_ob.get_param(cr, uid, 'LP')
            if not val:
                raise osv.except_osv(_('Warning!'), _('There is no Config Parameter define for this %s Product Type') % (formula_bro.product_type))
            else:
                if val.split(','):
                    split_val = val.split(',')
            categ_id = prod_categ_obj.search(cr, uid, [('name', '=', split_val[0])])
            # createing template and adding Attributes
            res1 = {
                'name': 'LP-' + formula_bro.name,
                'type': 'product',
                'product_type': formula_bro.product_type,
                'company_id': compues_comp_id and compues_comp_id[0] and 1,
                'sale_ok': False,
                'state': 'draft',
                'valuation': 'real_time',
                'formula': True,
                'uom_id': kg_uom_id and kg_uom_id[0],
                'uom_po_id': kg_uom_id and kg_uom_id[0],
                'categ_id': categ_id and categ_id[0],
                'attribute_line_ids':  [(0, 0, {'attribute_id': attribute_id,
                                                'value_ids': [(6, 0, [pro_att_val])]})]
            }
            pro_id = product_obj.create(cr, uid, res1, context=context)
            pro_id = [pro_id]
        if pro_id:
            
            # Searching the product variant ID's for creating BOM   ..
            product_id = product_product_obj.search(cr, uid, [
                    ('product_tmpl_id', '=', pro_id[0]),
                    ('attribute_value_ids', '=', product_att_id)], context=context)

            context.update({'display_default_code': False})
            product_name = product_product_obj.name_get(cr, uid, product_id, context=context)
            if type(product_name) == list:
                product_name = product_name[0][1]
            else:
                product_name = False
            
            product_id_bro = product_product_obj.browse(cr, uid, product_id)

            product_id_bro.write({'formula_id': formula_bro.id, 'default_code':product_name})
#                        l;kl
            #  Writing the product variants into the fields after finding product templates existing
            self.write(cr, uid, ids, {'product_lp_variant': product_id and product_id[0]}, context=context)
            # product_product_brow = product_product_obj.browse(cr, uid, product_id[0], context=context)
#            create_product_bom(self, cr, uid,formula_brw, tmp_id, pro_id, premix_id, revision, premix = False, context = None):
            asd2 = self.create_product_bom(cr, uid,formula_bro, pro_id[0], product_id and product_id[0],
                                    (product_id1 and product_id1[0]), current_rev, False, context = context)
            

        misc = {'pro_temp_lp': pro_id and pro_id[0], 'pro_temp1_premix': pro_id1 and pro_id1[0],
                'pro_variant_lp':product_id and product_id[0], 'pro_variant_premix': product_id1 and product_id1[0]}
        return misc


        #     # ========================== Creating the BOM for premix product =======================
        #
        # # Updating the bom line ids from the product ingredients and passing that value in the bom_line values
        # bom_premix_list = []
        # bom_line_id_premix = []
        # bom_premix_product = 0
        # bom_premix_exist = self.pool.get('mrp.bom').search(cr, uid, [('product_id', '=', product_id1[0])], context=context)
        # # print "BOM exists is =============>>>>>>>>>>>>>>>>===============", bom_premix_exist
        # if bom_premix_exist:
        #     raise osv.except_osv(_('Warning!'), _('BOM for this product already exists !!!!'))
        #
        # if pro_id1 and product_id1 and not bom_premix_exist:
        #     for i in formula_bro.line:
        #         bom_premix_list.append(i.premix)
        #         print " the premix list is as follows :::::>>>>>>>>>>>>>>>>>>>>>>", bom_premix_list
        #         if i.premix is True:
        #             print "\n\n\nproduct----qty", i, i.cantidadproduct
        #             bom_premix_product += i.cantidadproduct
        #             print "\n\n\nbom_premix_product", bom_premix_product
        #             bom_line_id_premix.append([0, 0, {
        #                 'product_id': i.producto.id,
        #                 'product_uom': 1,
        #                 'product_qty': i.cantidadproduct,
        #                 'product_efficiency': 1,
        #                 'type': 'normal'}])
        #
        #             print "\n\n\nbom_line_id_premix", bom_line_id_premix, bom_premix_list
        #
        #             bom_vals_premix = {
        #                 'bom_line_ids': bom_line_id_premix or False,
        #                 'product_tmpl_id': pro_id1[0],
        #                 'product_id': product_id1[0],
        #                 'product_qty': 1,
        #                 'type': 'normal',
        #                 'name': product_product_brow1.name or product_product_brow1.name + ' - ' + current_rev
        #             }
        #             bom_product_premix_id = self.pool.get('mrp.bom').create(cr, uid, bom_vals_premix)
        #
        #             if len(set(bom_premix_list)) == 1:
        #                 bom_inactive = {
        #                     'active': False
        #                 }
        #                 bom_inactive_id = self.pool.get('mrp.bom').write(cr, uid, bom_product_premix_id, bom_inactive)
        #                 print " the bom inactive id is ============================", bom_inactive_id
        #
        #
        # # =========  Creating the BOM for actual product without premix =======================
        #
        # # Updating the bom line ids from the product ingredients and passing that value in the bom_line values
        # if bom_premix_product > 0:
        #     bom_line_id = [[0, 0, {'product_id': product_id1[0], 'product_uom': 1, 'product_qty': bom_premix_product, 'product_efficiency': 1, 'type': 'normal'}]]
        # else:
        #     bom_line_id = [[0, 0, {'product_id': product_id1[0], 'product_uom': 1, 'product_qty': 1, 'product_efficiency': 1, 'type': 'normal'}]]
        #
        # bom_exist = self.pool.get('mrp.bom').search(cr, uid, [('product_id', '=', product_id[0])], context=context)
        # if bom_exist:
        #     raise osv.except_osv(_('Warning!'), _('BOM for this product already exists !!!!'))
        #
        # if pro_id and product_id and not bom_exist:
        #     for i in formula_bro.line:
        #         if i.premix is False:
        #             # print i
        #             bom_line_id.append([0, 0, {
        #                 'product_id': i.producto.id,
        #                 'product_uom': 1,
        #                 'product_qty': i.cantidadproduct,
        #                 'product_efficiency': 1,
        #                 'type': 'normal'}])
        #             # print "BOM line ids are >>>>>>====================", bom_line_id
        #
        #     bom_vals = {
        #         'bom_line_ids': bom_line_id,
        #         'product_tmpl_id': pro_id[0],
        #         'product_id': product_id[0],
        #         'product_qty': 1,
        #         'type': 'normal',
        #         'name': product_product_brow.name or product_product_brow.name + ' - ' + current_rev
        #     }
        #     bom_product_id = self.pool.get('mrp.bom').create(cr, uid, bom_vals)

#    this function change state Pruebas to revisado
    def revisado(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'revisado' }, context=None)
        return True

#    this function change state formulaenviar to Pruebas
    def Pruebas(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'Pruebas' }, context=None)
        return True

    def create_mo(self,cr,uid,ids,context):
        lp_seq = self.pool.get('ir.sequence').get(cr, uid, 'lp.mo.sequence') or '/'
        formula_id = self.browse(cr, uid, ids)
        
        if not formula_id.product_lp_variant:
            raise  osv.except_osv(_('Warning!'), _('You Can not Create MO Please Create LP Product'))
        if not formula_id.lp_product_qty:
            raise  osv.except_osv(_('Warning!'), _('Please Enter Quantity in LP Product QTY'))
        if formula_id.mo_refrence and formula_id.mo_refrence.state not in ('cancel'):
            raise  osv.except_osv(_('Warning!'), _('You can not Create Mo, Please set State cancel of this %s')% (formula_id.mo_refrence.name))
        bom_id = False
        bom_obj = self.pool.get('mrp.bom')
        bom_id = bom_obj._bom_find(cr, uid, product_id=formula_id.product_lp_variant.id, properties=[], context=context)
        if not bom_id:
            raise  osv.except_osv(_('Warning!'), _('There is no BOM defined for this Product.'))
        premix_bom_qty = 0
        if bom_id:
            bom_point = bom_obj.browse(cr, uid, bom_id, context=context)
            premix_count = 0
            for each in bom_point.bom_line_ids:
                if each.product_id.product_type=='premix':
                    premix_count += 1
                    premix_prod_id = each.product_id.id
                    premix_bom_qty = each.product_qty
            routing_id = bom_point.routing_id.id or False
            if premix_count > 1:
                raise  osv.except_osv(_('Warning!'), _('Cannot create MO. Product has more than 1 Premix type raw material in '
                                                       'BOM.') )
        master = self.pool.get('master.mrp')
        master_vals = {}
        master_vals.update({    'name':lp_seq or False,
                                'product_id': formula_id.product_lp_variant.id,
                                'product_qty': formula_id.lp_product_qty,
                                'product_uom': formula_id.product_lp_variant.uom_id.id,
                                'date_planned': datetime.datetime.now(),
                                'origin': '',
#                                'product_uos_qty': line.product_uom_qty * product.uos_coeff if product.uos_id.id else False,
#                                'product_uos': product.uos_id.id if product.uos_id.id else False,
                                'bom_id' : bom_id,
                                'formula_id' : formula_id.id,
                                'routing_id': routing_id,
                                'batches': 0,
                                'batch_qty': 0.0,
                                'product_type':formula_id.product_lp_variant.product_type,
                                'pres_id':formula_id.product_lp_variant.pres_id.id,
                                'premix_product_id':formula_id.product_premix_variant and formula_id.product_premix_variant.id,
                                'total_premix_weight':formula_id.lp_product_qty* (premix_bom_qty or 0.0)
                                })
        mo_id = master.create(cr, uid, master_vals, context)
        self.write(cr, uid, ids, {'mo_refrence':mo_id,'state':'mo_created'}, context=None)
        return True

    def create_product(self,cr,uid,ids,context):
        "This function creates Final Product and/or premix from Formula  "
        ir_confg_ob = self.pool.get('ir.config_parameter')
        prod_categ_obj = self.pool.get('product.category')
        if isinstance(ids, (int, long)): ids = [ids]
        compues_comp_id = self.pool.get('res.company').search(cr, uid, [], limit=1)
        
        for formula in self.browse(cr,uid,ids):
            val = ir_confg_ob.get_param(cr, uid, formula.product_type)
            if not val:
                raise osv.except_osv(_('Warning!'), _('There is no Config Parameter define for this %s Product Type') % (formula.product_type))
            else:
                if val.split(','):
                    split_val = val.split(',')
                    if len(split_val) != 2:
                        split_val.append(False)

            if formula.final_premix_id or formula.final_product_id:
                raise osv.except_osv(_('Warning!'), _('Final Product or Final Premix is already set, please update this Product!'))
#            'state': fields.selection([('Confirmed','Formulacion'),('Reformulacion','Reformulacion'),('enviadorefor','Formula Hitorica'),('formulaenviar','Formula a Enviar'),('Pruebas','Pruebas'),('revisado','Formula Revisado'),('L','Listo/Produción')],'Estado',readonly=True),
            if formula.state not in ('revisado'):
                raise osv.except_osv(_('Warning!'), _('You can Create Product at Revisado State'))
            # creating premix first as it will be attched in the BOM of product
            products = [formula.product_premix_variant, formula.product_lp_variant]
            # formula_premix = formula.product_premix_variant
            # product = formula.product_lp_variant
            for product in products:
                if product:
                    tmpl = product.product_tmpl_id
                    premix_flag = True if tmpl.product_type == 'premix' else False
                    
                    categ_id = prod_categ_obj.search(cr, uid, [('name', '=', split_val[1] or 'All Premix')])
                    if premix_flag:
                        default = {'name' : formula.name + ' - PR', 'product_type': 'premix',
                                   'formula': False, 'formula_id':formula.id, 'sale_ok': False, 'state': 'draft','valuation': 'real_time','company_id': compues_comp_id and compues_comp_id[0] or 1, 'categ_id':categ_id and categ_id[0]}
                    else:
                        categ_id = prod_categ_obj.search(cr, uid, [('name', '=', split_val[0])])
                        default = {'name' : formula.name, 'product_type': formula.product_type,
                                   'formula': False, 'formula_id':formula.id,'sale_ok': True, 'state': 'draft','valuation': 'real_time','company_id': compues_comp_id and compues_comp_id[0] or 1, 'categ_id':categ_id and categ_id[0]}

                    new_tmp_id = self.pool.get('product.template').copy(cr, uid, tmpl.id, default=default, context = context)
                    new_pro_ids = self.pool.get('product.product').search(cr, uid, [('product_tmpl_id', '=', new_tmp_id)])
#                    pass formula record id in product mastre
                    if premix_flag:
                        self.pool.get('product.template').write(cr, uid,new_tmp_id,{'name':formula.name + '- Premix'}, context = context)
                        formula.write({'final_premix_id': new_pro_ids[0]})
                        self.pool.get('product.product').write(cr, uid,new_pro_ids[0],{'formula_id':formula.id, 'default_code': formula.name + '- Premix'}, context = context)
                    else:
                        self.pool.get('product.template').write(cr, uid,new_tmp_id,{'name':formula.name}, context = context)
                        formula.write({'final_product_id': new_pro_ids[0]})
                        self.pool.get('product.product').write(cr, uid,new_pro_ids[0],{'formula_id':formula.id, 'default_code': formula.name}, context = context)

                    premix_id = False
                    if not premix_flag:
                        formula.refresh()
                        premix_id = formula.final_premix_id.id
                    # Sending Revision False as this is the final product
                    revision = False
                    print "premix_id, premix+++++++",premix_id, premix_flag
                    # Premix flag identifies a product is premix or not.
                    self.create_product_bom(cr, uid,formula, new_tmp_id, new_pro_ids[0],
                                            premix_id, revision, premix = premix_flag, context = context)
                    self.write(cr, uid, ids, { 'state' : 'L' }, context=None)

    # def update_bom_lines(self, cr, uid, formula,product, lines_to_update = []):
    #     "This method will update the bom lines from formula based on product type"
    #     # lines = [ for line in lines_to_update]
    #     if product.product_type == 'premix':




    def update_product(self, cr, uid, ids, context):
        "This method updates the BOM of Final Product and Premix if present on Formula"
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        bom_obj = self.pool.get('mrp.bom')
        bom_line_obj = self.pool.get('mrp.bom.line')
        product_proucuct_obj = self.pool.get('product.product')
        for formula in self.browse(cr, uid, ids):
            if not (formula.final_product_id):
                raise osv.except_osv(_('Warning!'), _('Final Product is not present in Formula. Please Create Product First!'))
            bool_premix = True if any([ln.premix for ln in formula.line]) else False
            if not formula.final_premix_id and bool_premix:
                raise osv.except_osv(_('Warning!'), _('Final Premix Product is not present in Formula!'))
            products = [formula.final_product_id , formula.final_premix_id]
            # formula_premix = formula.product_premix_variant
            # product = formula.product_lp_variant
            revision, premix_id = False, False
            for product in products:
                product.write({'formula_id':formula.id})
                premix_flag = True if product.product_type == 'premix' else False
                if not premix_flag:
                    premix_id = formula.final_premix_id.id
                lines_to_update = []
                if product:
                    bom = bom_obj.search(cr, uid, [('product_id', '=', product.id)])
                    bom = bom_obj.browse(cr, uid, bom)
                    if not bom:
                        # Create BOM if not present
                        tmp_id = self.pool.get('product.product').search(cr, uid, [('product_tmpl_id', '=', product.id)])
                        self.create_product_bom(cr, uid,formula, tmp_id and tmp_id[0], product.id,
                                                premix_id, revision, premix = premix_flag, context = context)
                    else:
                        if product.product_type == 'premix':
                            lines_to_update = [fr_line for fr_line in formula.line if fr_line.premix == True]
                        else:
                            lines_to_update = [fr_line for fr_line in formula.line if fr_line.premix <> True]

                    bom_product_ids , formula_product_ids, premix_qty = [], [], 0.0

                    for each_line in lines_to_update:
                        calculate_porcentaje = each_line.calculate_porcentaje
                        product_id = each_line.producto
                        for bom_line in bom.bom_line_ids:
                            if bom_line.product_id.id == product_id.id:
                                calculate_porcentaje = calculate_porcentaje / formula.n_total
                                bom_line.write({'product_qty':calculate_porcentaje})
                        if product.product_type == 'premix':
                            formula_product_ids = [fr_line.producto.id for fr_line in formula.line if fr_line.premix == True]
                        else:
                            formula_product_ids = [fr_line.producto.id for fr_line in formula.line if fr_line.premix <> True]
#                        formula_product_ids = lines_to_update
                        bom_product_ids = [bom_line.product_id.id for bom_line in bom.bom_line_ids]
#                        new_bom_product_ids: this variable stores the products present in formula but not in bom
#                        thsi  produc will be added to product bom
                        new_bom_product_ids = set(formula_product_ids) - set(bom_product_ids)
#                       
                        vals = {}
                        for each_product in product_proucuct_obj.browse(cr, uid, new_bom_product_ids):
                            vals = {'product_id': each_product.id,
                                            'product_qty': each_line.calculate_porcentaje / formula.n_total,
                                            'bom_id':bom.id,
                                            'product_uom':each_product.uom_id.id,
                                            'type':bom.type
                                            }
                            bom_line_obj.create(cr, uid, vals)
#                        bom_line_to_delete: this product not found in formula hence will delete from bom
                        bom_line_to_delete = set(bom_product_ids) - set(formula_product_ids)
                        if bom_line_to_delete:
                            bom_lines_ids = bom_line_obj.search(cr, uid, [('product_id', 'in', list(bom_line_to_delete)), ('bom_id', '=', bom.id)])
                            for line in bom_line_obj.browse(cr, uid, bom_lines_ids):
                                if line.product_id.product_type == 'premix':
                                    continue
                                else:
                                    bom_line_obj.unlink(cr, uid, line.id, context=context)
#                        if each_line.premix == True:
                    if product.product_type == 'premix':
                        total_premix_qty = sum([fr_line.calculate_porcentaje for fr_line in formula.line if fr_line.premix == True])/ formula.n_total
#                        this bom is for premix product
                        bom.write({'product_qty':total_premix_qty})
#                        seraching bom fro final product
                        bom_final_product = bom_obj.search(cr, uid, [('product_id', '=', formula.final_product_id.id)])
                        bom_line_ids = bom_line_obj.search(cr, uid, [('product_id', '=', formula.final_premix_id.id), ('bom_id', '=', bom_final_product)])
                        for line in bom_line_obj.browse(cr, uid, bom_line_ids):
                            line.write({'product_qty':total_premix_qty})
                    self.write(cr, uid, ids, { 'state' : 'L' }, context=None)
#                        self.update_bom_lines(cr, uid, formula, product, lines_to_update = lines_to_update)
        return True



#    # Method that creates the manufacturing order directly from the formulation page
#    def create_manufacturing_order(self, cr, uid, ids, context=None):
#        # For creating the Manufacturing Order from the fields in the formulation form
#
#        product_reqd_vals = self.pool.get('formula.c1').browse(cr, uid, ids, context=context)
#        bom_lp = self.pool.get('mrp.bom').search(cr, uid, [('product_id', '=', product_reqd_vals.product_lp_variant.id)], context=context)
#        mo_lp = self.pool.get('mrp.production').search(cr, uid, [('product_id', '=', product_reqd_vals.product_lp_variant.id)], context=context)
#        mo_premix = self.pool.get('mrp.production').search(cr, uid, [('product_id', '=', product_reqd_vals.product_premix_variant.id)], context=context)
#
#        if mo_lp and mo_premix:
#            raise osv.except_osv(_('Warning!'), _('Manufacturing Order of the product already exists !!'))
#
#        if not product_reqd_vals.product_lp_variant.id:
#            raise osv.except_osv(_('Warning!'), _('You cannot create Manufacturing Order without Product and BOM !!!!'))
#
#        else:
#
#            res = {
#                'product_id': product_reqd_vals.product_lp_variant.id,
#                'bom_id': bom_lp[0],
#                'product_uom': 1,
#            }
#            new_id = self.pool.get('mrp.production').create(cr, uid, res, context=context)
#            # print new_id
#
#            bom_premix = self.pool.get('mrp.bom').search(cr, uid, [('product_id', '=', product_reqd_vals.product_premix_variant.id)], context=context)
#            print "\n\n\nbom_premix",bom_premix
#            res1 = {
#                'product_id': product_reqd_vals.product_premix_variant.id,
#                'bom_id': bom_premix,
#                'product_uom': 1,
#            }
#            new_id1 = self.pool.get('mrp.production').create(cr, uid, res1, context=context)
#            # print new_id1
#
#        mo_ids = {'mo_lp': new_id, 'mo_premix': new_id1}
#        return mo_ids

    def _get_formula_ids(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('mrpformul00').browse(cr, uid, ids, context=context):
            result[line.formula_id.id] = True
        return result.keys()

    def _formula_cost(self, cr, uid, ids, field_name, arg, context=None):
        formula = self.browse(cr, uid, ids)
        res = {}
        cost_calculation = 0.0
        for formula in self.browse(cr, uid, ids, context=context):
            for line in formula.line:
                cost_calculation += line.cost_calculation
            res[formula.id] = cost_calculation
        return res

    _columns = {

        'is_ul':fields.boolean("is UL"),
        'cost_date':fields.datetime("Cost Date ",readonly=True),
        'count':fields.integer("NUmero Rvicion",readonly=True),
        'name': fields.char('Nombre Formula', size=20, required=True),
        'usuario': fields.many2one('res.users','Responsable'),
        'familia': fields.many2one('family', 'Familia',  required=True, help='Seleccione o cree la familia a la que pertenece la formula'),
        'date': fields.datetime('Fecha', size=30, help='Indique la fecha'),
        'line': fields.one2many('mrpformul00','formula_id','Componentes Formulacion'),
        'cod_formula' : fields.char('N°', size=20,readonly=True),
        'state': fields.selection([('Confirmed','Formulacion'),('Reformulacion','Reformulacion'),('enviadorefor','Formula Hitorica'),('mo_created', 'MO Created'),('formulaenviar','Formula a Enviar'),('Pruebas','Pruebas'),('revisado','Formula Revisado'),('L','Listo/Produción')],'Estado',readonly=True),
        'process': fields.char('Presentacion',size=20),
        'total': fields.function(_total,type='float',string='Total kg'),
        'total_pv': fields.function(_totalpventa,type='float',string='Total P.Venta'),
        'total_tpv1': fields.function(_totaltpv1,type='float',string='Total PZC1'),
        'total_tpv2': fields.function(_totaltpv2,type='float',string='Total PZC2'),
        'costototal': fields.function(_costo,type='float',string='Costo Producto',digits=(16,4)),
        'costototal_indirecto': fields.function(_costo_indirecto,type='float',string='Total Costo Indirecto',digits=(16,4)),
        'convert': fields.function(_convertkg, type='float', string='Equivalente grs',),
        'n_cantidad':fields.float('Cantidad kg',help='indique la cantidad en kg', required=True),
        'totalP': fields.function(_totalporcentaje, type='float',string='Total %'),
        'n_total': fields.float('Total %', help='indique la cantidad total enporcentaje', required=True),
        '_Notas0': fields.text('Comentario', help="Escribe un comentario"),
        '_cliente': fields.many2one('res.partner', string='Cliente',domain=[('customer','=',True)]),
        '_Fecha': fields.date('Fecha',size=30,help=' indique la fecha'),
        '_aplicacion': fields.char('Aplicacion',size=50, help='Aplicacion'),
        '_proceso': fields.selection([('Injection','Injection'),('Compresion','Compresion'),('otros','otros')],'Proceso Moldeo',help="Proceso de Moldeo"),
        'tamano': fields.char('Tamaño Extrusion',size=50),
        'Densidad': fields.float('Densidad (grms/cm3)'),
        'Encogimiento': fields.float('Encogimiento (inch/Lineal)',digits=(16,4)),
        'curados': fields.char('Tiempo de Curado (seg)',size=20),
        'Dureza': fields.integer('Dureza BARCOL',size=30),
        'Flujo': fields.char('Tiempo de Produccion',size=20),
        '_Notas': fields.text('Mezcla 1', help="Escribe un comentario"),
        '_Notas2': fields.text('Mezcla 2', help="Escribe un comentario"),
        '_Notas3': fields.text('Mezcla 3', help="Escribe un comentario"),
        'mescla4': fields.text('Mezcla 4', help="Escribe un comentario"),

        'notas_real': fields.text('Mezcla 1', help="Escribe un comentario"),
        'notas2_real': fields.text('Mezcla 2', help="Escribe un comentario"),
        'notas3_real': fields.text('Mezcla 3', help="Escribe un comentario"),
        'mescla4_real': fields.text('Mezcla 4', help="Escribe un comentario"),

        'Primer_Ciclo': fields.char('Primer Ciclo (min/seg)',size=20),
        'Segundo_Ciclo': fields.char('Segundo Ciclo (min/seg)',size=20),
        'Tercer_Ciclo': fields.char('Tercer Ciclo (min/seg)', size=20),
        'cuarto_ciclo': fields.char('Cuarto Ciclo (min/seg)', size=20),
        'product_user_id': fields.many2one('res.users','Elaboró'),
        'product_user2_id': fields.many2one('res.users','Revisó'),
        'product_user3_id': fields.many2one('res.users','Aprobó'),
        'product_color': fields.many2one('productcolor','Color Producto'),

        'F1': fields.char('Valor Unidad',size=50),
        'F2': fields.char('Valor Unidad',size=50),
        'F3': fields.char('Valor Unidad',size=50),
        'F4': fields.char('Valor Unidad',size=50),

        'ME1': fields.selection([('ASTM','ASTM'),('ISO','ISO')],'Norma'),
        'ME2': fields.selection([('ASTM','ASTM'),('ISO','ISO')],'Norma'),
        'ME3': fields.selection([('ASTM','ASTM'),('ISO','ISO')],'Norma'),
        'ME4':fields.selection([('ASTM','ASTM'),('ISO','ISO'),('UL','UL')],'Norma'),

        'U1': fields.char('Numero',size=20),
        'U2': fields.char('Numero',size=20),
        'U3': fields.char('Numero',size=20),
        'U4': fields.char('Numero',size=20),

        'M1': fields.char('Valor Unidad',size=50),
        'M2': fields.char('Valor Unidad',size=50),
        'M3': fields.char('Valor Unidad',size=50),
        'M4': fields.char('Valor Unidad',size=50),

        'ME01': fields.selection([('ASTM','ASTM'),('ISO','ISO')],'Norma'),
        'ME02': fields.selection([('ASTM','ASTM'),('ISO','ISO')],'Norma'),
        'ME03': fields.selection([('ASTM','ASTM'),('ISO','ISO')],'Norma'),
        'ME04': fields.selection([('ASTM','ASTM'),('ISO','ISO')],'Norma'),

        'U01': fields.char('Numero',size=20),
        'U02': fields.char('Numero',size=20),
        'U03': fields.char('Numero',size=20),
        'U04': fields.char('Numero',size=20),

        'E1': fields.char('Valor Unidad',size=50),
        'E2': fields.char('Valor Unidad',size=50),
        'E3': fields.char('Valor Unidad',size=50),

        'ME001': fields.selection([('ASTM','ASTM'),('ISO','ISO')],'Norma'),
        'ME002': fields.selection([('ASTM','ASTM'),('ISO','ISO')],'Norma'),
        'ME003': fields.selection([('ASTM','ASTM'),('ISO','ISO')],'Norma'),

        'U001': fields.char('Numero',size=20),
        'U002': fields.char('Numero',size=20),
        'U003': fields.char('Numero',size=20),
        'idcreado':fields.integer('Id creado'),
        'idcreado_local':fields.many2one('formula.c1','Id creado'),
        'real1':fields.char('Real',size=20),
        'real2':fields.char('Real',size=20),
        'real3':fields.char('Real',size=20),
        'real4':fields.char('Real',size=20),
        'real5':fields.char('Real',size=20),
        'real6':fields.char('Real',size=20),
        'real7':fields.char('Real',size=20),
        'real8':fields.char('Real',size=20),
        'real9':fields.char('Real',size=20),
        'real10':fields.char('Real',size=20),
        'real11':fields.char('Real',size=20),
        'tiempo1':fields.char('Real',size=10),
        'tiempo2':fields.char('Real',size=10),
        'tiempo3':fields.char('Real',size=10),
        'tiempo4':fields.char('Real',size=10),
        'durbarcol':fields.integer('Real'),
        'ticurado':fields.char('Real',size=10,maxlength="10"),
        'tidencidad':fields.float('Real'),
        'tiencogimiento':fields.related('real3',type='char',relation='formula.c1',string='Real'),
        ####
        'dur_noma':fields.selection([('ASTM','ASTM'),('ISO','ISO')],'Norma'),
        'dur_num':fields.char('Numero',size=10),
        'dur_valor':fields.char('Valor Unidad',size=10),
        'dur_real':fields.char('Real',size=10),
	    'product_id': fields.many2one('product.product'),
        'product_lp_variant': fields.many2one('product.product', string='Product LP'),
        'product_premix_variant': fields.many2one('product.product', string='Product Premix'),
        'product_type': fields.selection([('bmc', 'BMC'),('smc', 'SMC'),
                                          ('internal','Internal')], 'Final Product Type'),
        'final_product_id': fields.many2one('product.product', string = 'Final Product'),
        'final_premix_id': fields.many2one('product.product', string = 'Final Premix'),
        'lp_product_qty': fields.float(string = 'LP Product QTY',help='This will create to help mrp'),
        'mo_refrence': fields.many2one('master.mrp', string = 'MO Refrence',help='This will create to help mrp'),
        'formula_cost': fields.function(_formula_cost,digits_compute=dp.get_precision('Account'),type='float',string='Formula Cost',
            store={
               'formula.c1': (lambda self, cr, uid, ids, c={}: ids, ['line'], 10),
                'mrpformul00': (_get_formula_ids, ['cantidadcoste', 'cost_calculation', 'cantidadproduct'], 10),
            }, help="The total amount."),

    }

    _defaults = {
        'count':0,
        'curados':'00:00',
        'Flujo':'00:00',
        'usuario': lambda self, cr, uid, c: uid,
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'n_total':lambda *a: 100,
        'cod_formula':'Formula N°',
        'state': lambda *a: 'Confirmed',
        'cost_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        # 'U1':'Barcol',
        # 'U3':'in/in',
        # 'U01':'psi',
        # 'U02':'psi',
        # 'U03':'psi',
        # 'U04':'ftlb/in',
        # 'U001':'vpm',
        # 'U002':'seg',
        # 'U003':'seg',
        'Primer_Ciclo':'00:00',
        'Segundo_Ciclo':'00:00',
        'Tercer_Ciclo':'00:00',
        'cuarto_ciclo':'00:00',
        'tiempo1':'00:00',
        'tiempo2':'00:00',
        'tiempo3':'00:00',
        'tiempo4':'00:00',
        'ticurado':'00:00',
        'n_cantidad':'1',
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('cod_formula','/')=='/':
            vals['cod_formula'] = self.pool.get('ir.sequence').get(cr, uid, 'code-formula') or '/'
        # print vals
        summation = 0
        values = vals.get('line')
        # if not values:
        #     raise osv.except_osv(_('Warning!'), _('You can not create MO without ingredients !!!!'))
        if values:
            for i in values:
                per = i[2]['calculate_porcentaje']
                summation += per
                if summation > 100:
                    raise osv.except_osv(_('Warning!'), _('Percentage total should not exceed 100 !!!!'))

        return super(_formula_c1, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        # print "uper vadi:::::::::::::::"
        super(_formula_c1, self).write(cr, uid, ids, vals, context=context)
        mrp_bro_rec = self.browse(cr, uid, ids)
        total = 0.0
        for rec in mrp_bro_rec.line:
            total = total + rec.calculate_porcentaje
#            if total > 100:
#                raise osv.except_osv(_('Warning!'), _('Percentage total should not exceed 100 !!!!'))
        return True

_formula_c1()


class mrpformula_r(osv.osv):
    _name = 'mrpformul00'
    _description = 'Formulas'

#    def _cost_write(self, cr, uid, ids, field_name, arg, context=None):
#        res = {}
#        for rec in self.browse(cr, uid, ids):
#            inv = self.pool.get('account.invoice').search(cr, uid, [('type', '=', 'in_invoice'), ('state', '=', 'open')], limit=1)
#            supp_inv_line = self.pool.get('account.invoice.line').search(cr, uid, [('product_id', '=', rec.producto.id), ('invoice_id','=',inv)], limit=1)
#            # print "\n\n\nsupp_inv_line", supp_inv_line
#            if supp_inv_line:
#                supp_inv_rec = self.pool.get('account.invoice.line').browse(cr, uid, supp_inv_line)
#                # print "\n\n\nsupplier invoice rex", supp_inv_rec, supp_inv_rec.price_unit, rec, rec.cantidadproduct
#                rates_per_kg = (supp_inv_rec.price_unit * rec.cantidadproduct)
#                # print "\n\n\nthe cantidad cost is ::::>>>>>>>>>>>..", rates_per_kg
#                res[rec.id] = rates_per_kg
#        return res

    def create(self, cr, uid, vals, context=None):
        product_tmpl_obj = self.pool.get("product.template")
        product_obj = self.pool.get("product.product")
        res_currency_obj = self.pool.get('res.currency')
        cost_date = vals.get('cost_date')
        if not context:
            context = {}
        context = context.copy()
        context.update({'date':cost_date })
        product = product_obj.browse(cr, uid, vals.get('producto'))
        current_value = product_tmpl_obj.get_history_price(cr, uid, product.product_tmpl_id.id, 1, date=cost_date, context=context)
        usd_currency = res_currency_obj.search(cr, uid,[('name', '=', 'USD')], context=context)
        mxn_currency = res_currency_obj.search(cr, uid,[('name', '=', 'MXN')], context=context)
        if mxn_currency:
            mxn_currency = res_currency_obj.browse(cr, uid, mxn_currency[0])
            usd_currency = res_currency_obj.browse(cr, uid, usd_currency[0])
            usd_value = res_currency_obj.compute(cr, uid, mxn_currency.id, usd_currency.id, current_value,  round=True, context=context)
            vals.update({'cantidadcoste':usd_value})
        return super(mrpformula_r, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        for line in self.browse(cr, uid, ids):
            product_id = vals.get('producto', False)
            if not product_id:
                product_id = line.producto.id
            product_tmpl_obj = self.pool.get("product.template")
            product_obj = self.pool.get("product.product")
            product = product_obj.browse(cr, uid, product_id)
            res_currency_obj = self.pool.get('res.currency')
            current_value = product_tmpl_obj.get_history_price(cr, uid, product.product_tmpl_id.id, 1, date=line.cost_date, context=context)
            usd_currency = res_currency_obj.search(cr, uid,[('name', '=', 'USD')], context=context)
            mxn_currency = res_currency_obj.search(cr, uid,[('name', '=', 'MXN')], context=context)
            context = context.copy()
            context.update({'date':line.cost_date })
            if mxn_currency:
                mxn_currency = res_currency_obj.browse(cr, uid, mxn_currency[0])
                usd_currency = res_currency_obj.browse(cr, uid, usd_currency[0])
                usd_value = res_currency_obj.compute(cr, uid, mxn_currency.id, usd_currency.id, current_value,  round=True, context=context)
                vals.update({'cantidadcoste':usd_value})
        return super(mrpformula_r, self).write(cr, uid, ids, vals, context=context)

    def _calculate_porcentaje(self, cr, uid, ids, field_name, arg, context=None):
       res = {}
       for linea in self.browse(cr, uid, ids):
           if linea.formula_id:
               if linea.formula_id.n_total:
                   res[linea.id] = (linea.calculate_porcentaje * linea.formula_id.convert / linea.formula_id.n_total)/ 1000
       return res

#    def _calculate_coste(self, cr, uid, ids, field_name, arg, context=None):
#        records = self.browse(cr, uid, ids, context=context)
#        por = {}
#        # for r in records:
#        #     print " r is :::::::::::::::::::>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", r, r.id, r.cantidadproduct, r.costo
#        #     por[r.id] = (r.cantidadproduct * r.costo)
#        #     print "RESULTADO??????????????????????////////////", por, por[r.id]
#        # return por

    def onchange_form_costind(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)
        por = {}
        for r in records:
            por[r.id] = (r.cantidadcoste * 0.12)
            # print "RESULTADO", por
        return por

#    def onchange_producto(self, cr, uid, ids, product_id, context=None):
#        if not product_id:
#            return {}
#        values = {}
#        product_id = self.pool.get('product.product').browse(cr, uid, product_id)
##        get_history_price(product_id.product_tmpl_id, company_id, date=None)
#        if product_id:
#            values.update({'cantidadcoste': product_id.standard_price})
#        return {'value': values}

    def costo_total_imput(self, cr, uid, ids, field_name, arg, context=None):
        records = self.browse(cr, uid, ids)
        por = {}
        for r in records:
            por[r.id] = (r.cantidadcoste + r.costoindi)
            # print "RESULTADO", por
        return por

    def _cost_calculation(self, cr, uid, ids, field_name, arg, context=None):
        lines = self.browse(cr, uid, ids)
        ress = {}
        for line in lines:
            ress[line.id] = line.cantidadproduct * line.cantidadcoste
        return ress

    _columns = {
       'cost_calculation': fields.function(_cost_calculation,type='float',string='Total Cost'),
       'formula_id':fields.many2one('formula.c1','ID Referencia'),
       'cost_date':fields.related('formula_id','cost_date', type='datetime',relation='formula.c1', string='Cost date'),
       'Ref': fields.related('producto', 'default_code', type='char',relation='product.product', string='Referencia',readonly=True),
       'producto': fields.many2one('product.product', 'Producto', required=True),
       'product_uom': fields.related('producto', 'uom_id', type='many2one',relation='product.uom', string='Unidad de medida', readonly=True),
       'cantidadproduct': fields.function(_calculate_porcentaje,type='float', string='Cantidad Producto',digits=(16,10)),
       'calculate_porcentaje':fields.float('%',digits=(16,10),required=True),
       'product_color': fields.related('producto', 'colors', type='many2one',relation='productcolor', string='Color Producto', readonly=True),
       'costo': fields.related('producto', 'standard_price', digits_compute= dp.get_precision('standard_price'), type='float',relation='product.product', string='Costo',store=True),
       'cantidadcoste': fields.float(string='Costo producto'),
       'costoindi':fields.function(onchange_form_costind,digits=(16,4),type='float',string='Indirecto'),
       'costotal':fields.function(costo_total_imput,digits=(16,4),type='float',string='Costo Indirecto'),
       'p_venta':fields.float('P.VENTA'),
       'pzc1':fields.related('producto','pzc1',type='float',relation='product.product',string='PZC1'),
       'pzc2':fields.related('producto','pzc2',type='float',relation='product.product',string='PZC2'),
       'coment': fields.text('OBSERVACIONES', help="Escribe un comentario"),
       'state':fields.related('formula_id','state',type='selection',relation='formula.c1',string='state',selection=[('Confirmed','Formulacion'),('Reformulacion','Reformulacion'),('enviadorefor','Formula Hitorica'),('formulaenviar','Formula a Enviar'),('Pruebas','Pruebas'),('revisado','Formula Revisado'),('L','Listo/Produci�n')]),
       'indice':fields.related('producto','indice',type='char',relation='product.product',string='Indice',store=True),
       'premix': fields.boolean('Premix'),
#       'rates_per_kg': fields.function(_cost_write, digits=(16, 4), type='float', string='Product Cost'),
    }
    _order = "indice asc"
    #_order = "producto asc"
mrpformula_r()


class familias(osv.osv):
    _name = 'family'
    _columns = {
       'name': fields.char('Familias',size=30),
    }
familias()


class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'form_ids': fields.one2many('formula.c1', 'product_id', string='product'),
        'pzc1':fields.float('PZC1'),
        'pzc2':fields.float('PZC2'),
    }
product_product()


# class mrp_bom_replica(osv.osv):
#     _inherit = "mrp.bom"
#
#     def write(self, cr, uid, ids, vals, context=None):
#         print "vals are as ????>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>================", vals
#         super(mrp_bom_replica, self).write(cr, uid, ids, vals, context=context)
#
#     def _calculate_total_quantity(self, cr, uid, ids, field_name, arg, context=None):
#         mrp_bom_list = self.pool.get('mrp.bom').browse(cr, uid, ids, context=context)
#         print " the mrp bom list is >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>=====================", mrp_bom_list
#         for x in mrp_bom_list:
#             print "x is >>>>>>>>>>>>>>>>>>>>>>===============", x.name
#             if "-Premix" in x.name:
#                 print " Hello You are in the right loop .......", x.bom_line_ids
#                 mrp_bomline_ids_list = self.pool.get('mrp.bom.line').(cr, uid,[('product_id', '=', )], context=context)
#                 # for i in x.bom_line_ids:
#                 #     print i['product_qty']
#
#
#             # mrp_bom_object = self.pool.get("mrp.bom").browse(cr, uid, x, context=context)
#         #     print " MRP object id as follows :::>>>>>>>>>>>>>>>>===============================", mrp_bom_object
#         #     for i in mrp_bom_object:
#         #         print i.bom_line_ids
#
#     _columns = {
#             'calculated_quantity': fields.function(_calculate_total_quantity, digits=(16, 4), type='float', string='Total Product Quantity')
#     }
#
# mrp_bom_replica()
#

class formula_product_history(osv.osv):
    _name = "formula.product.history"
    
    _columns = {
        'set_datetime': fields.datetime('Date'),
        'formula_id':fields.many2one('formula.c1', 'Formula ref'),
        'product_id': fields.many2one('product.product','Responsable'),
    }
formula_product_history()
