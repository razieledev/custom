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
    "name": "Bista Mexico Accounting",
    "version": "2.1.0",
    "author": "Bista Solutions",
    "website": "http://www.bistasolutions.com",
    "category": "Localization/Account Charts",
    "description": """
Minimal accounting configuration for Mexico.
============================================
    """,
    "depends": [
        "account",
        "base_vat",
        "account_chart"
    ],
    "demo_xml": [],
    "data": [
        "data/account_group_code.xml",
        "data/bank_data.xml",
        "view/account_view.xml",
        "view/account_account_view.xml",
        "view/bank_view.xml",
        "security/ir.model.access.csv",
    ],
    "active": False,
    "installable": True,
}