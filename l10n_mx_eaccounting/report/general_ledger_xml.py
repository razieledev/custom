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

import xml.etree.cElementTree as ET
from .report_to_file import ReportToFile
from openerp.report import report_sxw
from openerp import pooler
from openerp.addons.account_financial_report_webkit.report.common_reports import CommonReportHeaderWebkit


class GeneralLedgerXml(report_sxw.rml_parse, CommonReportHeaderWebkit):
    """
    Class to generate and export an auxiliar ledger as XML report
    """
    def __init__(self, cursor, uid, name, context):
        super(GeneralLedgerXml, self).__init__(
            cursor, uid, name, context=context
        )
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
        })

    def _get_parent(self, account):
        """
        Returns the first parent of the account that is grouped on SAT code
        This allow maintain consistency between SAT reports
        """
        while not account.sat_group_id:
            account = account.parent_id
        return account

    def set_context(self, objects, data, ids, report_type=None):
        """
        Populate a ledger_lines attribute on each browse record that will be
        used to generate the report, we are overriding the GeneralLedgerWebkit
        method to populate correct accounts using the SAT Code allowing
        consistency between all XML reports uploaded to SAT
        """
        new_ids = data['form']['account_ids'] or data['form']['chart_account_id']

        # Reading form
        main_filter = 'filter_period'
        target_move = self._get_form_param('target_move', data, default='all')
        start = self._get_info(data, 'period_id', 'account.period')
        stop = self._get_info(data, 'period_id', 'account.period')
        fiscalyear = self.get_fiscalyear_br(data)
        chart_account = self._get_chart_account_id_br(data)

        initial_balance = self.is_initial_balance_enabled(main_filter)
        initial_balance_mode = initial_balance \
            and self._get_initial_balance_mode(start) or False

        # Retrieving accounts
        accounts = self.get_all_accounts(new_ids, exclude_type=[])
        init_balance_memoizer = self._compute_initial_balances(
            accounts, start, fiscalyear
        )

        ledger_lines_memoizer = self._compute_account_ledger_lines(
            accounts, main_filter, target_move, start, stop
        )
        objects = []
        for account in self.pool.get('account.account').browse(
            self.cursor, self.uid, accounts
        ):
            # The account is grouped with a SAT Code so we add
            # account to repor
            if account.sat_group_id:
                account.ledger_lines = ledger_lines_memoizer.get(
                    account.id, []
                )
                account.init_balance = init_balance_memoizer.get(
                    account.id, {}
                )
                objects.append(account)
            # The account is not grouped on a SAT code,
            # we add the movements on first parent who is grouped
            # into a SAT code
            else:
                parent = self._get_parent(account)
                parent = [x for x in objects if x.id == parent.id][0]
                parent.ledger_lines += ledger_lines_memoizer.get(account.id, [])
                parent.init_balance['init_balance'] += init_balance_memoizer.get(
                    account.id, {}
                )['init_balance']

        self.localcontext.update({
            'fiscalyear': fiscalyear,
            'chart_account': chart_account,
            'initial_balance_mode': initial_balance_mode,
        })

        return super(GeneralLedgerXml, self).set_context(
            objects, data, new_ids, report_type=report_type
        )

    def _compute_account_ledger_lines(
        self, accounts_ids, main_filter, target_move, start, stop
    ):
        res = {}
        for acc_id in accounts_ids:
            move_line_ids = self.get_move_lines_ids(
                acc_id, main_filter, start, stop, target_move
            )
            if not move_line_ids:
                res[acc_id] = []
                continue

            lines = self._get_move_line_datas(move_line_ids)
            res[acc_id] = lines
        return res

    def generate_report(self):
        """
        Function that generate the XML structure for report
        """
        # Create main journal entries node
        from datetime import datetime
        time_period = datetime.strptime(
            self.datas['form']['date'], "%Y-%m-%d"
        )
        aux = ET.Element('AuxiliarCtas:AuxiliarCtas')
        #namespace        
        aux.set("xsi:schemaLocation", 
                "www.sat.gob.mx/esquemas/ContabilidadE/1_1/AuxiliarCtas http://www.sat.gob.mx/esquemas/ContabilidadE/1_1/AuxiliarCtas/AuxiliarCtas_1_1.xsd")
        aux.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        aux.set("xmlns:AuxiliarCtas", "www.sat.gob.mx/esquemas/ContabilidadE/1_1/AuxiliarCtas")
        
        aux.set('Version', '1.1')
        aux.set('RFC', self.localcontext['company'].partner_id.vat_split)
        aux.set('Mes', str(time_period.month).rjust(2, '0'))
        aux.set('Anio', str(time_period.year))
        aux.set('TipoSolicitud', self.datas["form"]["type_request"])
        if self.datas["form"]["order_num"]:
            aux.set('NumOrden', self.datas["form"]["order_num"])
        if self.datas["form"]["pro_num"]:
            aux.set('NumTramite', self.datas["form"]["pro_num"])
        # Start processing data
        for account in self.objects:
            if account.ledger_lines:
                cumul_balance = 0
                accNode = ET.SubElement(aux, 'AuxiliarCtas:Cuenta')
                accNode.set('NumCta', account.code)
                accNode.set('DesCta', account.name)
                accNode.set(
                    'SaldoIni', str(account.init_balance.get('init_balance', 0))
                )
                for line in account.ledger_lines:
                    cumul_balance += line.get('balance', 0)
                    label_elements = [line.get('lname', '')]
                    if line.get('invoice_number'):
                        label_elements.append("(%s)" % (line['invoice_number'],))
                    label = ' '.join(label_elements)
                    detail = ET.SubElement(accNode, 'AuxiliarCtas:DetalleAux')
                    detail.set('Fecha', line.get('ldate'))
                    detail.set('NumUnIdenPol', line.get('move_name'))
                    detail.set('Concepto', label)
                    detail.set('Debe', str(line.get('debit', 0.0)))
                    detail.set('Haber', str(line.get('credit', 0.0)))
                accNode.set('SaldoFin', str(cumul_balance))
        # Write data into temporal file
        Etree = ET.ElementTree(aux)
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as report:
            Etree.write(report.name, encoding='UTF-8')
            fname = report.name

        return fname

ReportToFile(
    'report.account.auxiliar_ledger_xml',
    'account.account', parser=GeneralLedgerXml
)
