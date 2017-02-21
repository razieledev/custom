from openerp.osv import fields, osv


class product_product(osv.osv):

    _name = 'product.product' # Aqui va el mismo nombre de la clase que se hereda

    _inherit = 'product.product' # Permite la herencia propiamente dicho del modulo product
 
    #Agregamos el campo color al formulario producto o a la tabla product_product
    _columns = {
                'colors': fields.many2one('productcolor', 'Color'),
                 'indice': fields.char('Indice', size=10),
        }

    _order = "indice asc"

product_product()


class R_color(osv.osv):

    _name = 'productcolor'

    _columns = {
        'name': fields.char('Color', size=50, help='Registre Color'),
    }

R_color()
