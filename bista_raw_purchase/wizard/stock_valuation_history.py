from openerp import models, fields, api, _

class stock_history(models.Model):
    _inherit = 'stock.history'

#    conversion stock inventory to mxn to usd
    @api.one
    def _usd_inv_value(self):
        usd_currency = self.env['res.currency'].search([('name', '=', 'USD')])
        mxn_currency = self.env['res.currency'].search([('name', '=', 'MXN')])[0]
        self.usd_inv_value = mxn_currency.compute(self.inventory_value, usd_currency, round=True)

    usd_inv_value = fields.Float(compute='_usd_inv_value', string='USD IV Val')

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        res = super(stock_history, self).read_group(cr, uid, domain, fields, groupby, offset=offset, limit=limit, context=context, orderby=orderby, lazy=lazy)
        if 'usd_inv_value' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(cr, uid, line['__domain'], context=context)
                    usd_value = 0.0
                    for history_line in self.browse(cr, uid, lines, context=context):
                        usd_value += history_line.usd_inv_value
                    line['usd_inv_value'] = usd_value
        return res
