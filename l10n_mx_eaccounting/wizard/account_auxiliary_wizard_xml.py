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

import re
from openerp.osv import fields, orm
from openerp.tools.translate import _


class AccountAuxiliaryWizardXml(orm.TransientModel):
    """
    Almost copy exactly the general_ledger_wizard class form Webkit Reports
    because if try to inherit the class openerp could find all the fields
    needed for render the view
    """
    _inherit = "account.common.account.report"
    _name = "account.auxiliary.wizard.xml"

    def _get_account_ids(self, cr, uid, context=None):
        res = False
        if context.get('active_model', False) == 'account.account' \
                and context.get('active_ids', False):
            res = context['active_ids']
        return res

    _columns = {
        'period_id': fields.many2one(
            'account.period', 'Period',
            help=_('Select period for your chart report'),
            required=True
        ),
        'type_request': fields.selection(
            [('AF', 'Control act'),
             ('FC', 'Certifying audit'),
             ('DE', 'Return'),
             ('CO', 'Write off')],
            'Type of request', required=True
        ),
        'order_num': fields.char('Order number', size=13),
        'pro_num': fields.char('Procedure number', size=10),
        'account_ids': fields.many2many(
            'account.account', string='Filter on accounts',
            help="""Only selected accounts will be printed. Leave empty to
                    print all accounts."""
            ),
    }

    _defaults = {
        'account_ids': _get_account_ids,
    }

    def _check_fiscalyear(self, cr, uid, ids, context=None):
        obj = self.read(
            cr, uid, ids[0], ['fiscalyear_id', 'filter'], context=context)
        if not obj['fiscalyear_id'] and obj['filter'] == 'filter_no':
            return False
        return True

    def _check_order_num(self, cr, uid, ids, context=None):
        res = self.read(cr, uid, ids, context=context)[0]
        if res["order_num"] and res['type_request'] in ['AF', 'FC']:
            patron_order_num = re.compile('[A-Z]{3}[0-6][0-9][0-9]{5}(/)[0-9]{2}')
            match_order_num = patron_order_num.match(res["order_num"])
            if not match_order_num:
                return False
        return True

    def _check_pro_num(self, cr, uid, ids, context=None):
        res = self.read(cr, uid, ids, context=context)[0]
        if res["pro_num"] and res['type_request'] in ['DE', 'CO']:
            patron_pro_num = re.compile('[0-9]{10}')
            match_pro_num = patron_pro_num.match(res["pro_num"])
            if not match_pro_num:
                return False
        return True

    def _check_accounts(self, cr, uid, ids, context=None):
        """
        Checks that the user selects an account to be included on the report
        """
        res = self.read(cr, uid, ids, context=context)[0]
        if not res['account_ids']:
            return False
        return True

    _constraints = [
        (_check_fiscalyear,
         'When no Fiscal year is selected, you must choose to filter by \
         periods or by date.', ['filter']),
        (_check_order_num,
         'Order number not valid.\nVerify that the pattern is correct!',
         ['order_num']),
        (_check_pro_num,
         'Procedure number not valid.\nVerify that the pattern is correct!',
         ['pro_num']),
        (_check_accounts,
         'You must select an account to include in report!',
         ['account_ids']),
    ]

    def onchange_fiscalyear_id(
        self, cr, uid, ids, fiscalyear_id=False, context=None
    ):
        """
        Update the period in the wizard based on the fiscal year
        """
        res = {}
        res['value'] = {}
        if fiscalyear_id:
            period = False
            cr.execute('''
                SELECT * FROM (
                    SELECT p.id
                    FROM account_period p
                    LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                    WHERE f.id = %s AND p.special = False
                    ORDER BY p.date_start ASC
                    LIMIT 1) AS period_start''' % fiscalyear_id)
            periods = [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 0:
                period = periods[0]
            res['value'] = {'period_id': period}
        return res

    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(AccountAuxiliaryWizardXml, self).pre_print_report(
            cr, uid, ids, data, context)
        # will be used to attach the report on the main account
        data['ids'] = [data['form']['chart_account_id']]
        vals = self.read(cr, uid, ids, ['account_ids'], context=context)[0]
        data['form'].update(vals)
        return data

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

        if not vat_split:
            raise orm.except_orm(
                _('Error'),
                _('Not found information for VAT of Company.\n'
                  'Verify that the configuration of VAT is correct!')
            )

        return

    def build_report_name(self, cr, uid, ids, data, context=None):
        """
        Builds the name of report
        """
        from datetime import datetime
        res = self.read(cr, uid, ids, context=context)[0]
        period_id = res['period_id'][0]
        period_date = datetime.strptime(
            self.pool.get('account.period').browse(
                cr, uid, period_id).date_stop, "%Y-%m-%d"
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
            'XC']
        )
        return report_name_sat

    def generate_xml_report(self, cr, uid, ids, data, context=None):
        self.validate_vat(cr, uid, ids, context=context)

        res = self.browse(cr, uid, ids, context=context)[0]
        report_name = self.build_report_name(cr, uid, ids, data)
        data['form'] = {
            'chart_account_id': res.chart_account_id.id,
            'fiscalyear_id': res.fiscalyear_id.id,
            'period_id': res.period_id.id,
            'date': res.period_id.date_start,
            'target_move': res.target_move,
            'type_request': res.type_request,
            'order_num': res.order_num,
            'pro_num': res.pro_num,
        }
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.auxiliar_ledger_xml',
            'datas': data,
            'name': report_name,
            'context': {
                'FileExt': 'xml',
                'compress': True,
                'FileName': report_name
            }
        }
