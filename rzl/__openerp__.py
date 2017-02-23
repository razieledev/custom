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

{
    'name': 'Raziele customization',
    'version': '1.0',
#    'category': 'Hidden',
    # 'summary': 'Quotation, Sale Orders, Delivery & Invoicing Control',
    'description': """Raziele Customization""",
    'author': 'Shadail',
    # 'website': 'https://www.odoo.com/page/warehouse',
    'depends': ['sale_stock','inter_company_rules'],
    'data': [
        'security/ir.model.access.csv',
        'packaging/sale_view.xml',
        'views/product.xml',
        'views/partner_view.xml',
        'mrp/mrp_view.xml',
    ],
    'demo': [],


    'installable': True,
    'auto_install': False,
}
