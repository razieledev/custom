# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
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

{
    'name': 'MRP Bom Formula ',
    'version': '1.0',
    'author': 'Bista Solutions.',
    'category': 'Manufacturing',
    'description': """
    This module adds product price and stock to bom view
    """,
    'website': 'http://www.bistasolutions.com/',
    'depends': ['base', 'mrp', 'product_color', 'bista_mrp_batch', 'product'],#,'product_color'
    'data': [
        'security/formula_security.xml',
        'security/ir.model.access.csv',
        'wizard/envio_formula_remote_view.xml',
        'wizard/wizard_formula_production_view.xml',
        'formula_view.xml',
        'mrp_report.xml',
        'conector_view.xml',
        'master_mrp.xml',
        'product_product.xml',
        'lp_formula_sequence.xml',
        'ir_conf_data.xml',
         ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


   
 
