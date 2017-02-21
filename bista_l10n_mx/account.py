# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Authors: Openpyme (<http://openpyme.mx>)
#
#    Coded by: Salvador Martínez (chavamm.83@gmail.com)
#              Miguel Angel Villafuerte Ojeda (mikeshot@gmail.com)
#              Luis Felipe Lores (luisfqba@gmail.com)
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
from openerp.osv import osv, fields
from openerp.tools.translate import _


class account_account_sat_group(osv.Model):
    _name = 'account.account.sat_group'

    _columns = {
        'code': fields.char('Code', 50),
        'name': fields.char('Name', 50),
        'level': fields.integer('Level', ),
        'sat_group_parent_id': fields.many2one(
            'account.account.sat_group', string=_('SAT Group Parent')
        ),
    }


class account_account_template(osv.Model):
    _inherit = 'account.account.template'

    def _get_account_vals(
        self, cr, uid, template, account_template, code_digits,
        acc_template_ref, company_id, level_ref, tax_ids, context=None
    ):
        """
        This method calculate vals for accounts from templates.
        Used in this way allows l10n modules to extend and add
        new values to accounts as needed on each country

        :param chart_template_id: id of the chart template chosen in the wizard
        :param tax_template_ref: Taxes templates reference for write taxes_id in account_account.
        :paramacc_template_ref: dictionary with the mappping between the account templates and the real accounts.
        :param code_digits: number of digits got from wizard.multi.charts.accounts, this is use for account code.
        :param company_id: company_id selected from wizard.multi.charts.accounts.
        :returns: return acc_template_ref for reference purpose.
        :rtype: dict
        """
        if context is None:
            context = {}
        obj_acc = self.pool.get('account.account')
        company_name = self.pool.get('res.company').browse(
            cr, uid, company_id, context=context
        ).name
        code_main = account_template.code and len(account_template.code) or 0
        code_acc = account_template.code or ''
        if(code_main > 0 and code_main <= code_digits
           and account_template.type != 'view'
           ):
            code_acc = str(code_acc) + (str('0' * (code_digits - code_main)))
        parent_id = account_template.parent_id and ((account_template.parent_id.id in acc_template_ref) and acc_template_ref[account_template.parent_id.id]) or False
        # the level as to be given as well at the creation time, because of
        # the defer_parent_store_computation in context.
        # Indeed because of this, the parent_left and parent_right are
        # not computed and thus the child_of operator does not return
        # the expected values, with result of having the level field not
        # computed at all.
        if parent_id:
            level = parent_id in level_ref and level_ref[parent_id] + 1 or obj_acc._get_level(cr, uid, [parent_id], 'level', None, context=context)[parent_id] + 1
        else:
            level = 0
        vals = {
            'name': (template.account_root_id.id == account_template.id) and company_name or account_template.name,
            'currency_id': account_template.currency_id and account_template.currency_id.id or False,
            'code': code_acc,
            'type': account_template.type,
            'user_type': account_template.user_type and account_template.user_type.id or False,
            'reconcile': account_template.reconcile,
            'shortcut': account_template.shortcut,
            'note': account_template.note,
            'financial_report_ids': account_template.financial_report_ids and [(6, 0, [x.id for x in account_template.financial_report_ids])] or False,
            'parent_id': parent_id,
            'tax_ids': [(6, 0, tax_ids)],
            'company_id': company_id,
            'level': level,
            'nature': account_template.nature,
            'sat_group_id': account_template.sat_group_id.id,
        }
        return vals

    def generate_account(
        self, cr, uid, chart_template_id, tax_template_ref,
        acc_template_ref, code_digits, company_id, context=None
    ):
        """
        This method for generating accounts from templates.

        :param chart_template_id: id of the chart template chosen in the wizard
        :param tax_template_ref: Taxes templates reference for write taxes_id
                                 in account_account.
        :paramacc_template_ref: dictionary with the mappping between the
                                account templates and the real accounts.
        :param code_digits: number of digits got from wizard.multi.charts.accounts
                            this is use for account code.
        :param company_id: company_id selected from wizard.multi.charts.accounts.
        :returns: return acc_template_ref for reference purpose.
        :rtype: dict
        """
        if context is None:
            context = {}
        obj_acc = self.pool.get('account.account')
        template = self.pool.get('account.chart.template').browse(
            cr, uid, chart_template_id, context=context
        )
        # deactivate the parent_store functionnality on account_account
        # for rapidity purpose
        ctx = context.copy()
        ctx.update({'defer_parent_store_computation': True})
        level_ref = {}
        children_acc_criteria = [('chart_template_id', '=', chart_template_id)]
        if template.account_root_id.id:
            children_acc_criteria = ['|'] + children_acc_criteria + ['&', ('parent_id', 'child_of', [template.account_root_id.id]), ('chart_template_id', '=', False)]
        children_acc_template = self.search(
            cr, uid,
            [('nocreate', '!=', True)] + children_acc_criteria, order='id'
        )
        for account_template in self.browse(
            cr, uid, children_acc_template, context=context
        ):
            # skip the root of COA if it's not the main one
            if (template.account_root_id.id == account_template.id) and template.parent_id:
                continue
            tax_ids = []
            for tax in account_template.tax_ids:
                tax_ids.append(tax_template_ref[tax.id])

            vals = self._get_account_vals(
                cr, uid, template, account_template, code_digits,
                acc_template_ref, company_id, level_ref, tax_ids, context
            )
            new_account = obj_acc.create(cr, uid, vals, context=ctx)
            acc_template_ref[account_template.id] = new_account
            level_ref[new_account] = vals['level']

        # reactivate the parent_store functionnality on account_account
        obj_acc._parent_store_compute(cr)
        return acc_template_ref
