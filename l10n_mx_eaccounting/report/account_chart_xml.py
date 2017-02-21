# -*- encoding: utf-8 -*-
# ##########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
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

import xml.etree.cElementTree as ET
from .report_to_file import ReportToFile
from openerp.addons.account_chart_report.report.chart_of_accounts import AccountChar
from datetime import datetime


class AccountChartXml(ReportToFile):
    """
    Class to generate and export the account chart in xml format
    """

    def __init__(
        self, name, table, rml=False, parser=False, header=True, store=False
    ):
        super(AccountChartXml, self).__init__(
            name, table, rml, parser, header, store
        )

    def generate_report(self, parser, data, objects):
        import tempfile
        Etree = ET.ElementTree()

        acc_lst = parser.get_lst_account(
            parser.cr, parser.uid, data["form"]["id_account"],
            parser.actual_context
        )
        period_id = data["form"]["period_id"][0]

        period_obj = self.pool['account.period']
        period = period_obj.browse(
            parser.cr, parser.uid, period_id,
            context=parser.actual_context
        )
        time_period = datetime.strptime(period.date_start, "%Y-%m-%d")

        month = str(time_period.month).rjust(2, '0')
        year = str(time_period.year)

        catalogo = ET.Element('catalogocuentas:Catalogo')
        #namespace        
        catalogo.set("xsi:schemaLocation", 
                    "www.sat.gob.mx/esquemas/ContabilidadE/1_1/CatalogoCuentas http://www.sat.gob.mx/esquemas/ContabilidadE/1_1/CatalogoCuentas/CatalogoCuentas_1_1.xsd")
        catalogo.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        catalogo.set("xmlns:catalogocuentas", "www.sat.gob.mx/esquemas/ContabilidadE/1_1/CatalogoCuentas")
        
        catalogo.set("Version", "1.1")
        catalogo.set("RFC", parser.company.partner_id.vat_split)
        catalogo.set("Mes", month)
        catalogo.set("Anio", year)

        Etree._setroot(catalogo)

        # Debemos quitar la primer cuenta del listado,
        # ya que es la que engloba a todo el plan contable
        del acc_lst[0]

        for acc in acc_lst:
            # Solo se consideran las cuentas que tengan catálogo agrupador,
            # de esa forma se pueden omitir algunas cuentas del reporte
            if acc.sat_group_id:
                cuenta = ET.SubElement(catalogo, 'catalogocuentas:Ctas')
                # Codigo agrupador poner el Codigo no el Nombre
                cuenta.set("CodAgrup", str(acc.sat_group_id.code))
                cuenta.set("NumCta", acc.code)
                cuenta.set("Desc", acc.name)
                if acc.parent_id and acc.level > 1:
                    cuenta.set("SubCtaDe", acc.parent_id.code)
                cuenta.set("Nivel", str(acc.level))
                cuenta.set("Natur", acc.nature)

        # Write data into temporal file
        with tempfile.NamedTemporaryFile(delete=False) as report:
            Etree.write(report.name, encoding='UTF-8')
            self.fname = report.name

        return

AccountChartXml(
    'report.account.chart.xml', 'account.account',
    parser=AccountChar
)
