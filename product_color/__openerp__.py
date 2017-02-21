# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
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
 
{
    'name': 'Producto Color',
    'version': '1.0',
    'description': '''
        Permite agregar al formulario producto el campo color
    ''',
    'author': 'Bista Solutions',
    'website': 'http://www.bistasolutions.com/',
    'category': 'Tools',
    'depends': [
            'product',
            'base',#Este modulo para instalarse debe tener el modulo base y product instalado
            'stock',
                ],
    'data':[
	        'security/ir.model.access.csv',
            'product_color_view.xml', #todos los archivos xml que posea nuestro modulo se debe de agregarse aqui
                ],
    'demo_xml': [
                        ],
    'update_xml': [
                        ],
    'active': False,
    'installable': True,
    'certificate' : True,
}
