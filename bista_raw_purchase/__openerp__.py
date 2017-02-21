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
    "name": "Odoo (v8) Purcahse SMC",
    "version": "1.0",
    "depends": [
                'bista_mrp_smc',
                'purchase',
                'account',
                ],
    "author": "Bista Solutions",
    "description": """
                    This module fulfills the purchase flow requirement for SMC.
                    """,
    "website": "http://www.bistasolutions.com",
    "category": "MRP/Application",
    "data": [
                "security/ir.model.access.csv",
                # "product_data.xml",
                "pedimentos_view.xml",
                "account_invoice_view.xml",
                "purchase_view.xml",
                "sale_order_view.xml",
                "stock_view.xml",
                "account_invoice_view.xml",
                "wizard/monthly_invoice_wizard_view.xml",
                "wizard/stock_valuation_history_view.xml",
#                "report/print_barcode.xml",
            ],
    "auto_install": False,
    "application": True,
    "installable": True,
}
