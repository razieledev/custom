# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api
import openerp.addons.decimal_precision as dp


class product_template(models.Model):
    _inherit = 'product.template'

    @api.model
    def get_currency_id(self):
        mxn_currency = self.env['res.currency'].search([('name', '=', 'MXN')])[0]
        return mxn_currency

    @api.model
    def get_cost_currency_id(self):
        mxn_currency = self.env['res.currency'].search([('name', '=', 'MXN')])[0]
        return mxn_currency

    sale_price_currency_id = fields.Many2one(
        'res.currency', 'Sale Price Currency',
        required=True, default=get_currency_id,
        help="Currency used for the Currency List Price."
        )
    sale_price_on_list_price_type_currency = fields.Float(
        'Sale Price on List Price Currency',
        digits=dp.get_precision('Product Price'),
        compute='get_sale_price_on_list_price_type_currency',
        help="Base price on List Price Type currency at actual exchange rate",
        )
    list_price_type_currency_id = fields.Many2one(
        'res.currency',
        'List Price Type Currency',
        compute='get_sale_price_on_list_price_type_currency',
        )

    cost_price_currency_id = fields.Many2one(
        'res.currency', 'Cost Price Currency',
        required=True, default=get_cost_currency_id,
        help="Currency used for the Currency Cost Price."
        )
    cost_price_on_list_price_type_currency = fields.Float(
        'Cost Price on List Price Currency',
        digits=dp.get_precision('Product Price'),
        compute='get_cost_price_on_list_price_type_currency',
        help="Base price on Cost Price Type currency at actual exchange rate",
        )
    cost_price_type_currency_id = fields.Many2one(
        'res.currency',
        'Cost Price Type Currency',
        compute='get_cost_price_on_list_price_type_currency',
        )

    @api.one
    @api.depends('list_price', 'sale_price_currency_id')
    def get_sale_price_on_list_price_type_currency(self):
        to_currency = self.env['res.currency'].search([('name', '=', 'USD')])[0]
        self.list_price_type_currency_id = to_currency
        for product in self:
            if (
                    product.sale_price_currency_id and
                    product.sale_price_currency_id != to_currency
                    ):
                to_price = (
                    product.sale_price_currency_id.compute(
                        product.list_price, to_currency))
            else:
                to_price = product.list_price
            product.sale_price_on_list_price_type_currency = to_price

    def _price_get(self, cr, uid, products, ptype='list_price', context=None):
        if not context:
            context = {}
        res = super(product_template, self)._price_get(
            cr, uid, products, ptype=ptype, context=context)
        pricetype_obj = self.pool.get('product.price.type')
        if ptype == 'list_price':
            price_type_id = pricetype_obj.search(
                cr, uid, [('field', '=', ptype)])[0]
            price_type_currency_id = pricetype_obj.browse(
                cr, uid, price_type_id).currency_id.id
            for product in products:
                if product.sale_price_currency_id.id != price_type_currency_id:
                    res[product.id] = self.pool.get('res.currency').compute(
                        cr, uid, product.sale_price_currency_id.id,
                        price_type_currency_id, res[product.id],
                        context=context)
        if ptype == 'standard_price':
            price_type_id = pricetype_obj.search(
                cr, uid, [('field', '=', ptype)])[0]
            price_type_currency_id = pricetype_obj.browse(
                cr, uid, price_type_id).currency_id.id
            for product in products:
                if product.cost_price_currency_id.id != price_type_currency_id:
                    res[product.id] = self.pool.get('res.currency').compute(
                        cr, uid, product.cost_price_currency_id.id,
                        price_type_currency_id, res[product.id],
                        context=context)
        return res

    @api.one
    @api.depends('standard_price', 'cost_price_currency_id')
    def get_cost_price_on_list_price_type_currency(self):
        to_currency = self.env['res.currency'].search([('name', '=', 'USD')])[0]
        self.cost_price_type_currency_id = to_currency
        for product in self:
            if (
                    product.cost_price_currency_id and
                    product.cost_price_currency_id != to_currency
                    ):
                to_price = (
                    product.cost_price_currency_id.compute(
                        product.standard_price, to_currency))
            else:
                to_price = product.standard_price
            product.cost_price_on_list_price_type_currency = to_price

