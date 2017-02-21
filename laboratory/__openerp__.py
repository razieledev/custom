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
    'name': 'Laboratory',
    'version': '1.0',
    'author': 'Bista Solutions',
    'website': 'http://www.bistasolutions.com/',
    'summary': '',
    'description': """
Order Laboratory
================================================================================
Este módulo se encarga de gestionar las ordes de laboratorio para su producción.
    """,
    'depends': ['base', 'stock'],
    'category':'',
    # 'sequence':'',
    'data': [
        'security/laboratory_security.xml',
        'security/ir.model.access.csv',
        'laboratory_view.xml',
        'laboratory_report.xml',
        ],
    'init_xml': [],
    'demo_xml': [],
    'update_xml': [],
    'license': 'Other OSI approved licence',
    'installable': False,
    'auto_install': False,
    'active': False,
}