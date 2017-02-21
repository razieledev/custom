# -*- encoding: utf-8 -*- 
from openerp.osv import fields, osv, orm
import xmlrpclib


class envio_formula_remote(osv.osv_memory):

    _name = 'envio.production'

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(envio_formula_remote, self).default_get(cr, uid, fields, context=context)
        prod_obj = self.pool.get('formula.c1')
        prod = prod_obj.browse(cr, uid, context.get('active_id'), context=context)
        if 'name' in fields:
            res.update({'name': prod.name,'nombre_enviar':prod.name,'idformula':prod.id})
        return res

    def action_envioxmlrpc_production(self, cr, uid, ids,formula, context=None):
        wizard          = self.browse(cr,uid,ids[0],context=context)
        idsformu=wizard.idformula.id
        formula_obj  = self.pool.get('formula.c1')
        ###Parametros de conexion
        login=uid
        user_id = self.pool.get('res.users').browse(cr, uid, login, context=context) 
        user_login=user_id.login
        model_conec = self.pool.get('openerp.rpc').search(cr, uid, [('state', '=', 'conectado')])
        if not model_conec:
          raise osv.except_osv(("Error de Conexion Verifique la configuracion"),str(model_conec)) 
        resu=model_conec[0]
        conect_obj = self.pool.get('openerp.rpc').browse(cr, uid, resu, context=context)
        destinobd=conect_obj.db_destino
        destinouser=conect_obj.user_destino
        destinopasword=conect_obj.pass_destino
        ipdestion=conect_obj.host_destino
        sock_common = xmlrpclib.ServerProxy ('http://'+str(ipdestion)+':8069/xmlrpc/common')
        conection = sock_common.login(destinobd, destinouser, destinopasword)
        sock = xmlrpclib.ServerProxy('http://'+str(ipdestion)+':8069/xmlrpc/object')
        #raise osv.except_osv(("Id Formula"),str(idsformu))
        #producto uom
        if wizard.uom.name:
            unidadmedida= [('name', '=',wizard.uom.name)]
            iduom = sock.execute(destinobd, conection, destinopasword, 'product.uom', 'search', unidadmedida)
            if iduom:
                uom_id=iduom[0]
            elif not iduom:
                raise osv.except_osv(("No es posible encontar el color"),str(unidadmedida))
        else:
          uom_id=False
        #Categoria del producto
        categ_id=[('name','=','Saleable')]
        idvender = sock.execute(destinobd, conection, destinopasword, 'product.category', 'search', categ_id)
        id_categ=idvender[0]
        sale_ok=True
        tipo='product'
        procure_method='make_to_order'
        supply_method='produce'
        name_product=wizard.nombre_enviar
        #color
        if wizard.idformula.product_color.name:
            #raise osv.except_osv(("color"),str(wizard.idformula.product_color.name))
            color=[('name','=',wizard.idformula.product_color.name)]
            idcolor = sock.execute(destinobd, conection, destinopasword, 'productcolor', 'search', color)
            if idcolor:
                color_id=idcolor[0]
            elif not idcolor:
                raise osv.except_osv(("No es posible encontar el color"),str(color))
        else:
          color_id=False

        if wizard.idformula.product_color.name:
            name=wizard.nombre_enviar+' '+wizard.idformula.product_color.name
        elif not wizard.idformula.product_color.name:
            name=wizard.nombre_enviar 

        ###lineas
        linesingredientes =wizard.idformula.line
        if linesingredientes:
            for idlines in linesingredientes:
                product_ids=idlines.producto.name
                cantidad=idlines.cantidadproduct 
                if not cantidad:
                    raise osv.except_osv(("Esta enviado el ingrediente con cantidad 0.0"),str(product_ids))
                elif cantidad:
                    porcentaje=idlines.cantidadproduct 
                ingredentes= [('name', '=',product_ids)]
                idingredientes = sock.execute(destinobd, conection, destinopasword, 'product.product', 'search', ingredentes)
                if idingredientes:
                    ngredientes_ids=idingredientes[0]
                elif not idingredientes:
                    raise osv.except_osv(("No es posible encontar en la otra base de datos el producto con nombre:"),str(ingredentes))
        elif not linesingredientes:
            raise osv.except_osv(("La formula no contiene Ningun Ingrediente:"),str(ingredentes))
            linesingredientes=[]
        #raise osv.except_osv(("holas"),str(name))
        value_product = {
            'name':name,
            'categ_id':id_categ,
            'sale_ok':sale_ok,
            'type':tipo,
            'uom_po_id':uom_id,
            'uom_id':uom_id,
            'procure_method':procure_method,
            'supply_method':supply_method,
            'colors':color_id,
            'hr_expense_ok':False,
            'purchase_ok':False,
            'default_code':name_product,
        }
        crete_product_id= sock.execute(destinobd, conection,destinopasword,'product.product','create',value_product)
        idproduct_generado =crete_product_id
        value_bom_id={
            'product_id':idproduct_generado,
            'product_uom':uom_id,
            'product_qty':1,
            'type':'normal',
            'name':name_product,
            'code':name_product,
        }
        bom_id_generado = sock.execute(destinobd, conection,destinopasword,'mrp.bom','create',value_bom_id)
        bom_id=bom_id_generado
        for idlines in linesingredientes:
            product_ids = idlines.producto.name
            porcentaje = idlines.cantidadproduct
            ingredentes = [('name', '=', product_ids)]
            idingredientes = sock.execute(destinobd, conection, destinopasword, 'product.product', 'search', ingredentes)
            if idingredientes:
                ingredientes_ids = idingredientes[0]
            elif not idingredientes:
                ingredientes_ids = []
            valune_lines = {
                'bom_id': bom_id,
                'product_id': ingredientes_ids,
                'product_qty': porcentaje,
                'product_uom': uom_id,
            }
            bom_lines_ids = sock.execute(destinobd, conection,destinopasword,'mrp.bom','create',valune_lines)
        #raise osv.except_osv(("holas"),str(bom_lines_ids))
        cr.execute("update formula_c1 set state='L' where id=%s",(idsformu,))
        formula_obj = self.pool.get('formula.c1')
        formula_ids = formula_obj.search(cr,uid,[('state','=','revisado')])
        return{
            'domain': "[('id','in',["+','.join(map(str,formula_ids))+"])]",
            'name': ('Formulas'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'formula.c1',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
            
    _columns = {
        'idformula': fields.many2one('formula.c1','Formula',required=True),
        'name': fields.char('Nombre',size=64),
        'nombre_enviar': fields.char('Enviar Con Nombre',size=64, required=True),
        'uom': fields.many2one('product.uom','Unidad de Medida',required=True),
    }
envio_formula_remote()
