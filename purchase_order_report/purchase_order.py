from openerp import models, fields, api, _


class purchase_order(models.Model):
    _inherit = "purchase.order"

    frieght_forworder = fields.Many2one('res.partner', 'Frieght forworder')
    delivery_date = fields.Datetime('Delivery Date')

#    @api.multi
#    def get_company_address(self, company_type=''):
#        if not company_type:
#            return False
#        if company_type == 'inc':
#            company = self.env['res.company'].search([('name', '=', 'SMC Comp Inc (USA)')])
#        if company_type == 'mex':
#            company = self.env['res.company'].search([('name', '=', 'Compuestos SMC Mexico SA de CV')])
#            print"ccccccccccccc",company
#        return company