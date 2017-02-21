# -*- coding: utf-8 -*-
from openerp import models, fields, api, _



class SaleOrderReportWizard(models.TransientModel):
    _name = 'sale.order.report.wizard'
    _description = 'Sale Order Report'

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    monthwise = fields.Boolean('Monthwise')

    @api.multi
    def get_report(self):
#        cntx = "{'search_default_group_by_product': True, 'search_default_group_by_customer': True, \
#               'from_date': %s, 'to_date': %s}"%(self.from_date, self.to_date)
        
        
        if self.monthwise:
#            context = "{'search_default_group_by_sale_year': True,'search_default_group_by_sale_month': True, \
#                   'search_default_group_by_product': True, 'search_default_group_by_customer': True, \}"
            context = self._context.copy()
            context.update({'search_default_group_by_product': True, 'search_default_group_by_customer': True,
                            'search_default_group_by_sale_year': True,'search_default_group_by_sale_month': True})
        else:
            context = self._context.copy()
            context.update({'search_default_group_by_product': True, 'search_default_group_by_customer': True})

        reads = self.read(['from_date', 'to_date'])[0]
        from_date = reads['from_date']
        to_date = reads['to_date']
        domain = []
        if from_date:
            domain.append(('sale_date', '>=', from_date))
        if to_date:
            domain.append(('sale_date', '<=',  to_date))
        return {
            'name': _("Sale Order Report"),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'sale.order.report',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
            'domain': domain
        }

