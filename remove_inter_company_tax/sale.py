from openerp import models, fields, api, _


class sale_order(models.Model):

    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        res_company = self.env['res.company']
        if 'partner_id' in vals:
            part = self.env['res.partner'].browse(vals.get('partner_id'))
            comp = self.env['stock.warehouse'].browse(vals.get('warehouse_id')).company_id
            if part.name == 'Compuestos SMC Mexico SA de CV' and comp.name == 'Productos Plasco SA de CV':
                inter_company = res_company.sudo().search([('partner_id', '=', part.id)])
                if inter_company and 'order_line' in vals:
                    for line in vals.get('order_line'):
                        if line[2].get('tax_id'):
                            line[2].update({'tax_id': []})
        return super(sale_order, self).create(vals)
   
    @api.multi
    def write(self, vals):
        res_company = self.env['res.company']
        for rec in self:
            if 'partner_id' in vals:
                part = self.env['res.partner'].browse(vals.get('partner_id'))
                if part.name == 'Compuestos SMC Mexico SA de CV' and rec.company_id.name == 'Productos Plasco SA de CV':
                    inter_company = res_company.sudo().search([('partner_id', '=', part.id)])
                    if inter_company:
                        if 'order_line' in vals:
                            for line in vals.get('order_line'):
                                if line[2]:
                                    line[2].update({'tax_id': [(6, 0, [])]})
                        else:
                            for line in rec.order_line:
                                if line.tax_id:
                                    line.tax_id = [(5, 0)]
        return super(sale_order, self).write(vals)
