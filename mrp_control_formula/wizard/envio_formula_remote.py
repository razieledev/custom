# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv, orm
import xmlrpclib


class envio_formula_remote(osv.osv_memory):
    _name = 'envio.formula.remote' 

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(envio_formula_remote, self).default_get(cr, uid, fields, context=context)
        prod_obj = self.pool.get('formula.c1')
        prod = prod_obj.browse(cr, uid, context.get('active_id'), context=context)
        if 'name' in fields:
            res.update({'name': prod.name,'idformula':prod.id,'count':prod.count,'cod_formula':prod.cod_formula})
        return res

    def action_envioxmlrpc(self, cr, uid, ids,formula, context=None):
        wizard = self.browse(cr,uid,ids[0],context=context)
        idsformu=wizard.idformula.id
        formula_obj  = self.pool.get('formula.c1')
        ###Parametros de conexion
        login = uid
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
         ##cliente
        if wizard.idformula._cliente.name:
          args = [('name', '=',wizard.idformula._cliente.name)]
          idpartner = sock.execute(destinobd, conection, destinopasword, 'res.partner', 'search', args)
          if idpartner:
            partner_id=idpartner[0]
          elif not idpartner:
            raise osv.except_osv(("No es posible encontar en la otra base de datos el Cliente:"),str(args))
        else:
          partner_id=False

        ###lineas
        linesformula =wizard.idformula.line
        if linesformula:
            for idlines in linesformula:
                product_ids=idlines.producto.name
                porcentaje=idlines.calculate_porcentaje
                ingredentes= [('name', '=',product_ids)]
                idingredientes = sock.execute(destinobd, conection, destinopasword, 'product.product', 'search', ingredentes)
                if idingredientes:
                    ngredientes_ids=idingredientes[0]
                elif not idingredientes:
                     raise osv.except_osv(("No es posible encontar en la otra base de datos el producto con nombre:"),str(ingredentes))
        elif not linesformula:
            ingredentes = ''
            raise osv.except_osv(("La formula no contiene ningun Ingrediente:"), str(ingredentes))
            linesformula=[]
        ##Familia
        if wizard.idformula.familia.name:
          arg_familia = [('name', '=', wizard.idformula.familia.name)]
          idfamily = sock.execute(destinobd, conection, destinopasword, 'family', 'search', arg_familia)
          if idfamily:
            family_id = idfamily[0]
          elif not idfamily:
            namefami=wizard.idformula.familia.name
            valuen_family = {'name': namefami}
            create_id = sock.execute(destinobd, conection,destinopasword,'family','create',valuen_family)
            family_id = create_id
            #raise osv.except_osv(("No es posible encontar en la otra base de datos La Familia:"),str(arg_familia))
        else:
          family_id=False
        ##nombre
        name=wizard.idformula.name
        revision=wizard.idformula.count
        ##color
        if wizard.idformula.product_color.name:
          color_name= [('name', '=',wizard.idformula.product_color.name)]
          search_id= sock.execute(destinobd, conection, destinopasword, 'productcolor', 'search', color_name)
          if search_id:
            id_color=search_id[0]
          elif not search_id:
            namecolor=wizard.idformula.product_color.name
            valuen_color={
                'name':namecolor,
            }
            create_idcolor = sock.execute(destinobd, conection,destinopasword,'productcolor','create',valuen_color)
            id_color=create_idcolor
            #raise osv.except_osv(("No es posible encontar en la otra base de datos el Color:"),str(color_name))
        else:
          id_color=False
        ##process
        process=wizard.idformula.process
        n_cantidad=wizard.idformula.n_cantidad
        n_total=wizard.idformula.n_total
        idformula=wizard.idformula.id
        ##responsable
        if wizard.idformula.usuario.name:
          responsable_name= [('name', '=',wizard.idformula.usuario.name)]
          search_id= sock.execute(destinobd, conection, destinopasword, 'res.users', 'search', responsable_name)
          if search_id:
            id_responsable=search_id[0]
          elif not search_id:
            raise osv.except_osv(("No es posible encontar en la otra base de datos EL responsable:"),str(responsable_name))
        else:
          id_responsable=False

        ##elaboro
        if wizard.idformula.product_user_id.name:
          elaboroname= [('name', '=',wizard.idformula.product_user_id.name)]
          search_id= sock.execute(destinobd, conection, destinopasword, 'res.users', 'search', elaboroname)
          if search_id:
            id_elaboro=search_id[0]
          elif not search_id:
            raise osv.except_osv(("No es posible encontar en la otra base de datos el (Elaboro):"),str(elaboroname))
        else:
          id_elaboro=False
        ##Aprobo
        if wizard.idformula.product_user3_id.name:
          aproboname= [('name', '=',wizard.idformula.product_user3_id.name)]
          search_id= sock.execute(destinobd, conection, destinopasword, 'res.users', 'search', aproboname)
          if search_id:
            id_aprobo=search_id[0]
          elif not search_id:
            raise osv.except_osv(("No es posible encontar en la otra base de datos el (Aprobo):"),str(aproboname))
        else:
          id_aprobo=False
        ##Pestaña Datos
        aplicacion=wizard.idformula._aplicacion
        tamano=wizard.idformula.tamano
        Densidad=wizard.idformula.Densidad
        Encogimiento=wizard.idformula.Encogimiento
        proceso=wizard.idformula._proceso
        curados=wizard.idformula.curados
        Dureza=wizard.idformula.Dureza
        ##Pestaña Elaboracion
        Primer_Ciclo=wizard.idformula.Primer_Ciclo
        Segundo_Ciclo=wizard.idformula.Segundo_Ciclo
        Tercer_Ciclo=wizard.idformula.Tercer_Ciclo
        cuarto_ciclo=wizard.idformula.cuarto_ciclo
        ##Pestaña Elaboracion Reviso
        if wizard.idformula.product_user2_id.name:
          revisoname= [('name', '=',wizard.idformula.product_user2_id.name)]
          search_id= sock.execute(destinobd, conection, destinopasword, 'res.users', 'search', revisoname)
          if search_id:
            id_reviso=search_id[0]
          elif not search_id:
            raise osv.except_osv(("No es posible encontar en la otra base de datos el (Pestaña Elaboracion Campo(Reviso)):"),str(wizard.idformula.product_user2_id.name))
        else:
          id_reviso=False
        Notas=wizard.idformula._Notas
        Notas2=wizard.idformula._Notas2
        Notas3=wizard.idformula._Notas3
        mescla4=wizard.idformula.mescla4
        ##Pestaña Propiedades Fisicas
        ME1=wizard.idformula.ME1
        ME2=wizard.idformula.ME2
        ME3=wizard.idformula.ME3
        ME4=wizard.idformula.ME4
        U1=wizard.idformula.U1
        U2=wizard.idformula.U2
        U3=wizard.idformula.U3
        U4=wizard.idformula.U4
        F1=wizard.idformula.F1
        F2=wizard.idformula.F2
        F3=wizard.idformula.F3
        F4=wizard.idformula.F4
        dur_noma=wizard.idformula.dur_noma
        dur_num=wizard.idformula.dur_num
        dur_valor=wizard.idformula.dur_valor
        #dur_real=wizard.idformula.dur_real
        ##Pestaña Propiedades mecanicas
        ME01=wizard.idformula.ME01
        ME02=wizard.idformula.ME02
        ME03=wizard.idformula.ME03
        ME04=wizard.idformula.ME04
        U01=wizard.idformula.U01
        U02=wizard.idformula.U02
        U03=wizard.idformula.U03
        U04=wizard.idformula.U04
        M1=wizard.idformula.M1
        M2=wizard.idformula.M2
        M3=wizard.idformula.M3
        M4=wizard.idformula.M4
        ##Pestaña Propiedades Electricas
        ME001=wizard.idformula.ME001
        ME002=wizard.idformula.ME002
        ME003=wizard.idformula.ME003
        U001=wizard.idformula.U001
        U002=wizard.idformula.U002
        U003=wizard.idformula.U003
        E1=wizard.idformula.E1
        E2=wizard.idformula.E2
        E3=wizard.idformula.E3
        #raise osv.except_osv(("notas"),str(ME3))
        #####Inicia envio REMOTP##
        value_formula = {
            ###From 1
            '_cliente':partner_id,
            'familia':family_id,
            'product_color':id_color,
            'name':name,
            'process':process,
            'usuario':id_responsable,
            'n_cantidad':n_cantidad,
            'product_user_id':id_elaboro,
            'product_user3_id':id_aprobo,
            'n_total':n_total,
            'count':revision,
            'state':'Pruebas',
            'idrecibido':idformula,
            ##Datos
            '_aplicacion':aplicacion,
            'tamano':tamano,
            'Densidad':Densidad,
            'Encogimiento':Encogimiento,
            '_proceso':proceso,
            'curados':curados,
            'Dureza':Dureza,
            ##Pestaña Elaboracion
            'Primer_Ciclo':Primer_Ciclo,
            'Segundo_Ciclo':Segundo_Ciclo,
            'Tercer_Ciclo':Tercer_Ciclo,
            'cuarto_ciclo':cuarto_ciclo,
            '_Notas':Notas,
            '_Notas2':Notas2,
            '_Notas3':Notas3,
            'mescla4':mescla4,
            'product_user2_id':id_reviso,
            ##Pestaña Propiedades
            #Fisicas
            'ME1':ME1,
            'ME2':ME2,
            'ME3':ME3,
            'ME4':ME4,
            'U1':U1,
            'U2':U2,
            'U3':U3,
            'U4':U4,
            'F1':F1,
            'F2':F2,
            'F3':F3,
            'F4':F4,
            'dur_noma':dur_noma,
            'dur_num':dur_num,
            'dur_valor':dur_valor,
            ###Mecanica
            'ME01':ME01,
            'ME02':ME02,
            'ME03':ME03,
            'ME04':ME04,
            'U01':U01,
            'U02':U02,
            'U03':U03,
            'U04':U04,
            'M1':M1,
            'M2':M2,
            'M3':M3,
            'M4':M4,
            ###Electrica
            'ME001':ME001,
            'ME002':ME002,
            'ME003':ME003,
            'U001':U001,
            'U002':U002,
            'U003':U003,
            'E1':E1,
            'E2':E2,
            'E3':E3,
            }

        creteremote_id = sock.execute(destinobd, conection, destinopasword, 'formula.c1', 'create', value_formula)

        idenvio =creteremote_id
        #linesformula =wizard.idformula.line
        for idlines in linesformula:
            product_ids=idlines.producto.name
            porcentaje=idlines.calculate_porcentaje
            ingredentes= [('name', '=',product_ids)]
            idingredientes = sock.execute(destinobd, conection, destinopasword, 'product.product', 'search', ingredentes)
            if idingredientes:
               ingredientes_ids=idingredientes[0]
            elif not idingredientes:
                raise osv.except_osv(("No es posible encontar en la otra base de datos el producto con nombre:"),str(ingredentes))
            valune_lines={
                'formula_id':idenvio,
                'producto':ingredientes_ids,
                'calculate_porcentaje':porcentaje,
            }
            new_lines = sock.execute(destinobd, conection,destinopasword,'mrpformul00','create',valune_lines)
        cr.execute("update formula_c1 set idcreado='"+str(creteremote_id)+"',state='Pruebas' where id=%s",(idsformu,))
        return True
            
    _columns = {
        'name': fields.char('Nombre', size=64),
        'cod_formula': fields.char('N°', size=20, readonly=True),
        'idformula': fields.many2one('formula.c1', 'formula'),
        'count': fields.integer("NUmero Rvicion", readonly=True),
    }
envio_formula_remote()
