# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@vauxoo.com
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

{
    "name" : "Bista Invoice report smc",
    "version" : "1.0",
    "sequence" : 1,
    "author" : "Bista Solutions",
    "category" : "Localization/Mexico",
    "description" : """This module add a report for purchase orders
    """,
    "website" : "http://www.bistasolutions.com/",
    "license" : "AGPL-3",
    "depends" : [
        "purchase",
        "account_move_report",
        "stock_account",
        "account",
        "mrp_control_formula",
    ],
    "demo" : [],
    "data" : [
        "report_paperformat.xml",
        "invoice_report_qweb.xml",
        "report_menus.xml",
        "report/invoice_report_view_qweb.xml",
        "wizard/sale_order_report_wizard_view.xml",
        "sale_order_report_view.xml",
        "report_agedpartnerbalance.xml",
#        "journal_view.xml",
    ],
    "installable" : True,
}
