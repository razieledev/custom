from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import models, fields, api, _
import time


class product_template(models.Model):
    _inherit = "product.template"

    @api.model
    def get_history_price(self, product_tmpl, company_id, date=None):
        if date is None:
            date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        price_history_obj = self.env['product.price.history']
        history_ids = price_history_obj.search([('product_template_id', '=', product_tmpl), ('datetime', '<=', date)], limit=1)
        if history_ids:
            return history_ids.read(['cost']) and history_ids.read(['cost'])[0]['cost'] or 0.0
        return 0.0
