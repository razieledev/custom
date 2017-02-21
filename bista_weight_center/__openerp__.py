# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    OML : Openerp Mexican Localization
#    Copyleft (Cl) 2008-2021 Vauxoo, C.A. (<http://vauxoo.com>)
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Odoo (v8) Weigh Machine Integration SMC",
    "version": "1.0",
    "depends": [
                'bista_mrp_smc',
                'stock',
                ],
    "author": "Bista Solutions",
    "description": """
                    This module integrates Odoo MO with Weigh Machine Application of SMC.
                    """,
    "website": "http://www.bistasolutions.com",
    "category": "MRP/Application",
    "data": [
                "security/ir.model.access.csv",
                'sequence/sequence_data.xml',
                "weigh_center.xml",
                "master_mrp_view.xml",
                "product_view.xml",
                "wc_request.xml",
                "stock_view.xml",
                "formula_view.xml",
            ],

    "auto_install": False,
    "application": True,
    "installable": True,
}
