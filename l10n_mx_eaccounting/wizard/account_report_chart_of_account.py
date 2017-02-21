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

from openerp.osv import fields, orm, osv
from openerp.tools.translate import _


class ChartOfAccountsReport(orm.TransientModel):
    _name = 'account.print.chart.accounts.report'

    _inherit = 'account.print.chart.accounts.report'
    _columns = {
        'period_id': fields.many2one(
            'account.period', 'Period',
            help=_('Select period for your chart report'),
            required=True
        ),
    }

    def validate_vat(self, cr, uid, ids, context=None):
        # Validates that the company has VAT configured properly
        company_id = self.pool.get('res.company')._company_default_get(
            cr, uid, object='account.print.chart.accounts.report',
            context=context
        )
        company = self.pool.get('res.company').browse(
            cr, uid, company_id, context=context
        )

        vat_split = company.partner_id.vat_split

        return vat_split or False

    def default_get(self, cr, uid, fields, context=None):
        """
        This function load in the wizard,
        the current period
        """
        import datetime

        comp = self.pool.get('res.company')
        company_id = comp._company_default_get(
            cr, uid,
            'account.print.chart.accounts.report', context=context
        )

        data = super(ChartOfAccountsReport, self).default_get(
            cr, uid, fields, context=context
        )
        time_now = datetime.date.today()

        period_id = self.pool.get('account.period').search(
            cr, uid,
            [('date_start', '<=', time_now),
             ('date_stop', '>=', time_now),
             ('company_id', '=', company_id)]
        )
        if period_id:
            data.update({'period_id': period_id[0]})
        return data

    def build_report_name(self, cr, uid, ids, data, context=None):
        """
        Builds the name of report
        """
        from datetime import datetime
        res = self.read(cr, uid, ids, context=context)[0]
        period_id = res['period_id'][0]
        period_date = datetime.strptime(
            self.pool.get('account.period').browse(
                cr, uid, period_id
            ).date_stop, "%Y-%m-%d"
        )
        company_id = self.pool.get('res.company')._company_default_get(
            cr, uid, object='account.print.chart.accounts.report',
            context=context
        )
        company = self.pool.get('res.company').browse(
            cr, uid, company_id, context=context
        )
        vat_split = company.partner_id.vat_split

        report_name_sat = ''.join([
            vat_split,
            str(period_date.year),
            str(period_date.month).rjust(2, '0'),
            'CT'
        ])
        return report_name_sat

    def generate_xml_report(self, cr, uid, ids, data, context=None):
        if not self.validate_vat(cr, uid, ids, context=context):
            raise osv.except_osv(
                _('Error'),
                _('Not found information for VAT of Company.\n'
                  'Verify that the configuration of VAT is correct!')
            )
        else:
            res = self.read(cr, uid, ids, context=context)[0]
            account_id = res["chart_account_id"][0]
            period_id = res["period_id"]

            data["form"] = {"id_account": account_id, "period_id": period_id}
            report_name = self.build_report_name(cr, uid, ids, data)
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.chart.xml',
                'datas': data,
                'name': report_name,
                'context': {
                    'FileExt': 'xml',
                    'compress': True,
                    'FileName': report_name
                }
            }
