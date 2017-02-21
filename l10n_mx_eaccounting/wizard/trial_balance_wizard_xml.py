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

from openerp.osv import orm, osv, fields
from openerp.tools.translate import _


class trial_balance_wizard_xml(orm.TransientModel):
    _inherit = 'trial.balance.webkit'

    def validate_vat(self, cr, uid, ids, context=None):
        """
        Validates that the company has VAT configured properly
        """
        company_id = self.pool.get('res.company')._company_default_get(
            cr, uid, object='trial.balance.webkit', context=context
        )
        company = self.pool.get('res.company').browse(
            cr, uid, company_id, context=context
        )

        vat_split = company.partner_id.vat_split

        if not vat_split:
            return False
        return True

    def get_last_journal_entrie(
        self, cr, uid, ids, period_id, type_send, context=None
    ):
        """
        This function gets the last date of journal entrie for specific period
        """
        res = {}
        res['value'] = {}
        if type_send == 'C':
            period = self.pool.get('account.period').browse(
                cr, uid, period_id, context=context)

            cr.execute('''
                SELECT max(date)
                FROM account_move
                WHERE account_move.period_id = %s
                ''' % period.id)
            for i in cr.fetchall():
                last_date = i[0]

            res['value'] = {'last_modification': last_date}

        return res

    def xml_export(self, cr, uid, ids, context=None):
        """
        This function validates and prepares the report
        for XML export
        """
        # As inherited report, it needs a initial and final
        # period to generate the report, the user only select
        # the final period and this equals the initial period
        # to the selection
        res = self.browse(cr, uid, ids, context=context)[0]
        period_from = res.period_to
        self.write(
            cr, uid, ids,
            {'period_from': period_from.id},
            context=context
        )

        if not self.validate_vat(cr, uid, ids, context=context):
            raise osv.except_osv(
                _('Error'),
                _('Not found information for VAT of Company.\n'
                  'Verify that the configuration of VAT is correct!')
            )

        return self.check_report(cr, uid, ids, context=context)

    _columns = {
        'type_send': fields.selection(
            [('N', 'Normal'),
             ('C', 'Complementaria')],
            'Type Send', required=True,
        ),
        'last_modification': fields.date('Last Modification',),
    }

    _defaults = {
        'type_send': 'N',
    }

    def default_get(self, cr, uid, fields, context=None):
        """
        This function establishes the filter of the report as 'filter_period'
        (as it is an inherited report)
        """
        data = super(trial_balance_wizard_xml, self).default_get(
            cr, uid, fields, context=context
        )

        data.update({'filter': 'filter_period'})
        return data

    def change_fiscalyear_id(
        self, cr, uid, ids, fiscalyear_id=False, context=None
    ):
        """
        Update the period in the wizard based on the fiscal year
        """
        res = {}
        res['value'] = {}
        if fiscalyear_id:
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON
                               (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               ORDER BY p.date_start ASC
                               LIMIT 1) AS period_start''' % fiscalyear_id)
            periods = [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 0:
                res['value'] = {'period_to': periods[0]}
        return res

    def build_report_name(self, cr, uid, ids, data, context=None):
        """
        Builds the name of report
        """
        from datetime import datetime
        res = self.read(cr, uid, ids, context=context)[0]
        period_id = res['period_to'][0]
        period_date = datetime.strptime(
            self.pool.get('account.period').browse(
                cr, uid, period_id).date_stop, "%Y-%m-%d"
        )
        company_id = self.pool.get('res.company')._company_default_get(
            cr, uid, object='trial.balance.webkit', context=context
        )
        company = self.pool.get('res.company').browse(
            cr, uid, company_id, context=context
        )
        vat_split = company.partner_id.vat_split

        report_name_sat = ''.join([
            vat_split,
            str(period_date.year),
            str(period_date.month).rjust(2, '0'),
            'B',
            data['type_send']]
        )
        return report_name_sat

    def _print_report(self, cr, uid, ids, data, context=None):
        context = context or {}
        if context.get('xml_export'):
            data = self.pre_print_report(cr, uid, ids, data, context=context)
            res = self.browse(cr, uid, ids, context=context)[0]
            data['type_send'] = res.type_send
            data['last_modification'] = res.last_modification
            report_name = self.build_report_name(cr, uid, ids, data)
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.account_report_trial_balance_xml',
                'datas': data,
                'name': report_name,
                'context': {
                    'FileExt': 'xml',
                    'compress': True,
                    'FileName': report_name
                }
            }
        else:
            return super(trial_balance_wizard_xml, self)._print_report(
                cr, uid, ids, data, context=context
            )
