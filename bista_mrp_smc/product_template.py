from openerp.osv import osv, fields


class product_template(osv.Model):

    _inherit = 'product.template'

    def cal_packaging(self,cr,uid,ids,field,args,context=None):
        res = {}
       
        brw_rec=self.browse(cr,uid,ids[0])
        
        
        if field=='total_weight':
            total_weight=brw_rec.weight_per_box*brw_rec.box_per_pallet
            res[brw_rec.id]=total_weight
        if field=='packing_box' and brw_rec.weight_per_box*brw_rec.box_per_pallet:
                ans=brw_rec.per_box/(brw_rec.weight_per_box*brw_rec.box_per_pallet)
                res[brw_rec.id]=ans
        if field=='packing_pallet' and brw_rec.weight_per_box*brw_rec.box_per_pallet:
                ans=brw_rec.per_pallet/(brw_rec.weight_per_box*brw_rec.box_per_pallet)
                res[brw_rec.id]=ans  
        if field=='packing_bag' and brw_rec.weight_per_box*brw_rec.box_per_pallet:
                ans=brw_rec.per_bag/(brw_rec.weight_per_box*brw_rec.box_per_pallet)
                res[brw_rec.id]=ans 
        if field=='packing_box_label' and brw_rec.weight_per_box*brw_rec.box_per_pallet:
                ans=brw_rec.per_box_label/(brw_rec.weight_per_box*brw_rec.box_per_pallet)
                res[brw_rec.id]=ans 
        if field=='packing_etiqueta_de_tarima' and brw_rec.weight_per_box*brw_rec.box_per_pallet:
                ans=brw_rec.per_etiqueta_de_tarima/(brw_rec.weight_per_box*brw_rec.box_per_pallet)
                res[brw_rec.id]=ans 
        if field=='packing_cinta_p_caja' and brw_rec.weight_per_box*brw_rec.box_per_pallet:
                ans=brw_rec.per_cinta_p_caja/(brw_rec.weight_per_box*brw_rec.box_per_pallet)
                res[brw_rec.id]=ans 
        if field=='packing_playo' and brw_rec.weight_per_box*brw_rec.box_per_pallet:
                ans=brw_rec.per_playo/(brw_rec.weight_per_box*brw_rec.box_per_pallet)
                res[brw_rec.id]=ans 
        if field=='packing_esquineros' and brw_rec.weight_per_box*brw_rec.box_per_pallet:
                ans=brw_rec.per_esquineros/(brw_rec.weight_per_box*brw_rec.box_per_pallet)
                res[brw_rec.id]=ans 
                
        

        return res

    def _get_product_type(self, cr, uid, context = None):
        "This function will return list of tuples for all categories mapped to product_type"
        category_obj = self.pool.get('product.category')
        cr.execute("select distinct parent_id from product_category")
        fetch_parents = cr.fetchall()
        parent_ids = [tup[0] for tup in fetch_parents if tup[0] is not None]
        cr.execute("select distinct id from product_category")
        fetch_all = cr.fetchall()
        all_ids = [tup_all[0] for tup_all in fetch_all if tup_all[0] is not None]
        final_child_ids = list(set(all_ids) - set(parent_ids))
        return [(categ.name.lower(), categ.name) for categ in category_obj.browse(cr, uid, final_child_ids)]
        # print "ftetch++++",fetch
        # stock_qty = fetch and fetch[0] or False

        
    _columns = {
        'product_type': fields.selection([('bmc', 'BMC'),('smc', 'SMC'),('premix', 'Premix'),('packaging','Packaging'),
                                          ('internal','Internal'),('resinas','Resinas'),('aditivos','Aditivos'),
                                          ('catalizadores','Catalizadores'), ('inhibidores','Inhibidores'),
                                          ('desmoldantes','Desmoldantes'), ('pigmentos', 'Pigmentos'),
                                          ('cargas_minerales','Cargas Minerales'), ('aditivos_especiales','Aditivos Especiales'),
                                          ('refuerzos','Refuerzos'), ('otros','Otros'), ('empaque', 'Empaque'), ('miselaneous','Miselaneous')],
                                         'Product Type'),
        # 'product_type': fields.selection(_get_product_type, 'Product Type'),
        'pres_id':fields.many2one('presentation','Presentation Type'),
        
        'weight_per_box':fields.float('Material/Caja (kg)'),
        'box_per_pallet':fields.integer('Cajas/Tarima'),
        'total_weight':fields.function(cal_packaging,string="Material/Tarima(kg)",type="float"),
        
        'per_box':fields.integer('Caja / Box'),
        'per_pallet':fields.integer('Tarima / Pallet'),
        'per_bag':fields.integer('Bolsa / Bag'),
        'per_box_label':fields.integer('Etiqueta de caja'),
        'per_etiqueta_de_tarima':fields.integer('Etiqueta de tarima'),
        'per_cinta_p_caja':fields.integer('Cinta p. caja (m)'),
        'per_playo':fields.integer('Playo (m)'),
        'per_esquineros':fields.integer('Esquineros'),
        
        'packing_box':fields.function(cal_packaging,string="Empaque/caja",type="float", digits = (16, 4)),
        'packing_pallet':fields.function(cal_packaging,string="Empaque/pallet",type="float", digits = (16, 4)),
        'packing_bag':fields.function(cal_packaging,string="Empaque/bolso",type="float", digits = (16, 4)),
        'packing_box_label':fields.function(cal_packaging,string="Empaque/etiqueta de la caja",type="float", digits = (16, 4)),
        'packing_etiqueta_de_tarima':fields.function(cal_packaging,string="Empaque/etiqueta_de_tarima",type="float", digits = (16, 4)),
        'packing_cinta_p_caja':fields.function(cal_packaging,string="Empaque/cinta_p_caja",type="float", digits = (16, 4)),
        'packing_playo':fields.function(cal_packaging,string="Empaque/playo",type="float", digits = (16, 4)),
        'packing_esquineros':fields.function(cal_packaging,string="Empaque/esquineros",type="float", digits = (16, 4)),
        
        
        'pack_product_id':fields.many2one('product.product',string="Packaging Product"),

        'is_dropshipping': fields.boolean('Is Dropshipping', help="Set this for Salebale product so by selecting this product"
                                                                  "in Sale order Line , Dropshipping route gets automatically selected.")

       }
