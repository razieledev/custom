from openerp import models, fields, api
import datetime


class product_template(models.Model):

    _inherit = 'product.template'

    formula = fields.Boolean(string='Formula')
    

class product_product(models.Model):

    _inherit = 'product.product'

    formula_id = fields.Many2one('formula.c1', 'Revision')


#price_history_obj.create(cr, uid, {
#            'product_template_id': product_tmpl_id,
#            'cost': value,
#            'company_id': company_id,
#        }, context=context)


    @api.model
    def create(self, vals):
        res = super(product_product, self).create(vals)
        if vals and (vals.get('formula_id')):
            hist_obj = self.env['formula.product.history']
            hist_vals = {
                    'set_datetime': (datetime.datetime.now()),
                    'formula_id': res.formula_id,
                    'product_id': res.id,
                }
            hist_obj.create(hist_vals)
        return res

    @api.multi
    def write(self, vals):
        print "in write+++++++++++product+idddd++++++++vals", self.id,vals
        res = super(product_product, self).write(vals)
        hist_obj = self.env['formula.product.history']
        # giving prefrence to vals coming formula
        formula = (vals and (vals.get('formula_id'))) or self.formula_id
        if not isinstance(formula, (int, long)): formula = formula.id
        if formula:
            hist_vals = {
                    'set_datetime': (datetime.datetime.now()),
                    'formula_id': formula,
                    'product_id': self.id,
                }
            hist_obj.create(hist_vals)
        return res