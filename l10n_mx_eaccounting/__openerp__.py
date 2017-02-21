# -*- encoding: utf-8 -*-
# ##########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Authors: Openpyme (<http://openpyme.mx>)
#
#
#    Coded by: Salvador Martínez (chavamm.83@gmail.com)
#              Miguel Angel Villafuerte Ojeda (mikeshot@gmail.com)
#              Luis Felipe Lores Caignet (luisfqba@gmail.com)
#              Agustín Cruz Lozano (agustin.cruz@openpyme.mx)
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
    "name": "Mexico eAccounting",
    "version": "0.1",
    "depends": [
        "account",
        "l10n_mx",
        "l10n_mx_base_vat_split",
        "account_chart_report",
        "account_financial_report_webkit",
        "bista_l10n_mx",
    ],
    'category': 'Mexico',
    "description": """
Mexico eAccounting Module
=========================

This module enabled the eAccounting as required by SAT
    """,
    'author': 'Openpyme.mx',
    "website": "http://www.openpyme.mx",
    'data': [
        "wizard/account_report_chart_of_account.xml",
        "wizard/trial_balance_wizard_xml_view.xml",
        "wizard/journal_entries_wizard_xml_view.xml",
        "wizard/account_auxiliary_wizard_xml_view.xml",
        "wizard/menu_eaccounting.xml",
    ],
    'installable': True,
    'active': False,
}
