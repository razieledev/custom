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

import logging
import xml.etree.ElementTree as ET
from .report_to_file import ReportToFile
from openerp.addons.account_financial_report_webkit.report.trial_balance import TrialBalanceWebkit

logger = logging.getLogger(__name__)


class TrialBalanceXML(TrialBalanceWebkit):
    """
    Class to generate and export the trial balance in xml format
    """
    def generate_report(self):
        """
        Creates the trial balance in XML format
        """
        import tempfile
        from datetime import datetime
        from openerp.tools import float_round as round 
        
        # Get decimal precision from configuration for SAT
        precision_obj = self.pool.get('decimal.precision')
        dp = precision_obj.precision_get(self.cursor, self.uid, 'SAT')
        
        period = self._get_info(self.datas, 'period_from', 'account.period')
        time_period = datetime.strptime(period.date_start, "%Y-%m-%d")
        Etree = ET.ElementTree()
        balanza = ET.Element('BCE:Balanza')
        #namespace   
        balanza.set("xsi:schemaLocation", 
                    "www.sat.gob.mx/esquemas/ContabilidadE/1_1/BalanzaComprobacion http://www.sat.gob.mx/esquemas/ContabilidadE/1_1/BalanzaComprobacion/BalanzaComprobacion_1_1.xsd")
        balanza.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        balanza.set("xmlns:BCE", "www.sat.gob.mx/esquemas/ContabilidadE/1_1/BalanzaComprobacion")

        balanza.set('Version', '1.1')
        balanza.set('RFC', self.localcontext['company'].partner_id.vat_split)
        balanza.set('Mes', str(time_period.month).rjust(2, '0'))
        balanza.set('Anio', str(time_period.year))
        balanza.set('TipoEnvio', self.datas['type_send'])
        # If type_send equals to "C" puts the value of the "stop_period" field
        # as last modification of trial balance
        if self.datas['type_send'] == "C":
            balanza.set('FechaModBal', self.datas['last_modification'])

        Etree._setroot(balanza)
        for account in self.objects:
            # Verify if account has a valid fields "to_display"
            # and "sat_group_id", if no skips the account
            # code migrate time condition = if not account.to_display and not account.sat_group_id:
            if not account.sat_group_id:
                continue
            cuenta = ET.SubElement(balanza, 'BCE:Ctas')
            cuenta.set("NumCta", account.code)
            #befor code migration uncommented below one line
#             cuenta.set("SaldoIni", str(round(account.init_balance,dp)))
            cuenta.set("Debe", str(round(account.debit,dp)))
            cuenta.set("Haber", str(round(account.credit, dp)))
            cuenta.set("SaldoFin", str(round(account.balance, dp)))

        # Write data into temporal file
        with tempfile.NamedTemporaryFile(delete=False) as report:
            Etree.write(report.name, encoding='UTF-8')
            fname = report.name

        return fname

ReportToFile(
    'report.account.account_report_trial_balance_xml',
    'account.account', parser=TrialBalanceXML
)
