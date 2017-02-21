# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (c) 2012 MKI - http://www.mikrointeracciones.com.mx
#    All Rights Reserved.
#    info@mikrointeracciones.com.mx
############################################################################
#    Coded by: richard (ricardo.gutierrez@mikrointeracciones.com.mx)
############################################################################
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
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp


class laboratory_order(osv.osv):
    _name = 'laboratory.order'

    def mymod_confirmed(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'Confirmed' }, context=None)
        return True

    def mymod_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'cancel' },context=None)
        return True

    def mymod_voldraft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'draft' }, context=None)
        return True

    def mymod_test(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'test' }, context=None)
        return True
   
    def mymod_produce(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'produce' }, context=None)
        return True

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'laboratory.order') or '/'
        return super(laboratory_order, self).create(cr, uid, vals, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'date': fields.date.context_today(self, cr, uid, context=context),
            'state': 'draft',
            
            'client': '',
            'name': self.pool.get('ir.sequence').get(cr, uid, 'laboratory.order'),
        })
        return super(laboratory_order, self).copy(cr, uid, id, default, context=context)    

    def button_dummy(self, cr, uid, ids, context=None):
        return True 

    _columns = {
        'state': fields.selection([('draft','Borrador'),('Confirmed','Laboratorio'),('test','Pruebas'),('produce','Producir'),('cancel','Cancelado')],'Estado',readonly=True),
        'name' : fields.char('Order Laboratory', size=64, readonly=True),
        'client': fields.many2one('res.partner','Cliente', requiered = True),
        'project': fields.many2one('account.analytic.account','Projecto No.', help='Indique el projecto para la orden', required = True),
        'date': fields.date('Fecha enterado', help='Indique la fecha para la orden', requiered = True),
        'users': fields.many2one('res.users','Solicitante', required=True),
        'formula': fields.char('Formula No.', size=64, help='Escriba la formula para orden de formulacion'),
        'prev_muestra': fields.char('Previa muestra lab', size=64, help='Escriba la formula para orden de formulacion'),
        'product_qty': fields.float('Cantidad muestra', required=True, help="Indique la cantidad de muestra", digits_compute=dp.get_precision('muestra')),
        'product_uom': fields.many2one('product.uom', 'Unidad de medida', required=True, help="Unidad de medida para la muestra"),
        'color': fields.many2one('productcolor','Color',help='Indique el color de muestra para la orden'),
        'presentation': fields.char('Presentacion', size=30, help='Escriba el tipo presentacion de la muestra'),
        'lot1': fields.char('Embarque 1', size=30, help='Escriba o selecciones el lote 1 de donde se toma la muestra'),
        'lot2': fields.char('Embarque 2', size=30, help='Escriba o selecciones el lote 2 de donde se toma la muestra'),
        'lot3': fields.char('Embarque 3', size=30, help='Escriba o selecciones el lote 3 de donde se toma la muestra'),
        'datasheet_no': fields.char('Ficha de tecnica No.', size=30, help='Indique el numero de ficha tecnica'),
        'result': fields.text('Resultados', size=30, help='Describe los resultado obtenidos'),
        'quantity_d': fields.char('Cantidad muestra', size=30, help='Indique la cantidad de muestra para la orden'),
        'presentation_d': fields.char('Presentacion', size=30, help='Escriba el tipo presentacion de la muestra'),
        'date_required':fields.date('Fecha de entrega', help='Indique la fecha a entregar'),
        'packing': fields.char('Presentacion', size=30, help='Escriba el tipo presentacion de la muestra'),
        'charge': fields.char('Con o sin cargo', size=50, help='Escriba el tipo de cargo'),
        'document' : fields.char('calidad', size=50, help='Indica el documento a enviar al cliente'),
        'test': fields.char('Pruebas', size=50, help='Pruebas realizadas antes del envio'),
        'molding_plates1': fields.char('Molde 1', size=50, help='Molde para identificar que no exixte contaminancion'),
        'molding_plates2': fields.char('Molde 2', size=50, help='Molde para identificar el tono de la muestra sea el standar'),
        'pick_up': fields.char('Recoleccion', size=50, help='Indique la muestra sera recolentada por el cliente'),
        'payment_shipping': fields.char('Pago de envio', size=50, help='Idicar si el elvio sera pagado por el cliente'),
        'box_type': fields.char('D3', size=50, help='Idicar si la caja es seca o refriguerada'),
        'thermometer': fields.char('D4', size=50, help='Indicar si necesita enviar termometro para el monitorear la tenperatura'),
        'contact': fields.many2one('res.partner','Contacto', size=50, help='Selecciones el contacto de la empresa cliente'),
        'addrees': fields.char('Direccion', size=50, help=''),
        'description': fields.text('Descripcion', size = 50, help='Descripcion de la muestra, incluye informacion detallada'),
        'formulae': fields.char('No Formula', size = 50, help='Formula'),
    }

    _defautl = {
        'state': lambda *a: 'draft', 
        'date': fields.date.context_today,
    }

laboratory_order()
