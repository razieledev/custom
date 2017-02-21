# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Authors: Openpyme (<http://openpyme.mx>)
#
#
#    Coded by: Salvador Martínez (chavamm.83@gmail.com)
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

from openerp.report.report_sxw import report_sxw
from openerp import pooler


def compress(file_temp, file_name, fext='txt', comp='zip'):
    """
    Helper function to compress file
    TODO: Add more compression methods
    """
    import tempfile
    import zipfile

    new_name = '.'.join([file_name, fext])

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        with zipfile.ZipFile(tmp, mode='w') as archive:
            archive.write(file_temp, arcname=new_name)

        output = tmp.name

    return output


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class ReportToFile(report_sxw):
    """
    Class for extend reporting engine to download any file

    """
    def create(self, cr, uid, ids, data, context=None):
        if not context:
            context = {}
        self.pool = pooler.get_pool(cr.dbname)
        self.cr = cr
        self.uid = uid
        self.parser_instance = self.parser(cr, uid, self.name2, context)
        objs = self.getObjects(cr, uid, ids, context)
        self.parser_instance.set_context(objs, data, ids, 'xml')

        _p = AttrDict(self.parser_instance.localcontext)

        # Create the report and get the filename where saved
        self.generate_report(_p, data, objs)

        fext = context['FileExt']

        # Call the function to zip the file
        if context.get('compress', False):
            self.fname = compress(
                self.fname, context.get('FileName', self.fname), fext,
                context.get('compression', 'zip')
            )
            fext = context.get('compression', 'zip')

        # Open the file and read its content
        with open(self.fname, 'r') as content:
            data = content.read()

        return (data, fext)

    def generate_report(self, parser, data, objects):
        """
        Override this method to create your file
        @param parser: dict parser object
        @param data: dict data collected from wizard to print report
        @param objects: list objects to process in report

        @return: path for temporal filename to download
        """
        self.fname = self.parser_instance.generate_report()
