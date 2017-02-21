from openerp import models, fields, api
import datetime
from datetime import datetime

from openerp import tools

#this py not used for pdf report
class sale_order_report(models.Model):
    _name = 'sale.order.report'
    _auto = False
    # _table = 'sale_order_report'
#    _order = 'date asc'

    customer_id = fields.Many2one('res.partner', 'Customer')
    sale_order_id = fields.Many2one('sale.order', 'Sale Order')
    product_id = fields.Many2one('product.product', 'Product')
    formula_id = fields.Many2one('formula.c1', 'Rev No')
    vol_kg = fields.Float('VOLUME (KGS)')
    sell_price = fields.Float('Selling Price/KG')
    formula_cost = fields.Float('Cost/KG', default = 0)
    sales_usd = fields.Float('Total Sales', default = 0, readonly=True, compute='_compute_sale_price')
    rm_cost = fields.Float('Total Cost', default = 0, readonly=True, compute='_compute_rm_cost')
    sales_rm = fields.Float('SALES/RM', default = 0, readonly=True, compute='_compute_sales_rm')
    sale_date = fields.Date('Sales Date')
    sale_month = fields.Integer('Sales Month')
    sale_year = fields.Integer('Sales Year')

    @api.one
    def _compute_sale_price(self):
        self.sales_usd = self.sell_price * self.vol_kg

    @api.one
    def _compute_rm_cost(self):
        self.rm_cost = self.formula_cost * self.vol_kg

    @api.one
    def _compute_sales_rm(self):
        if self.rm_cost == 0.0:
            rm_cost = 1
        else:
            rm_cost = self.rm_cost
        self.sales_rm = self.sales_usd / rm_cost


    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        res = super(sale_order_report, self).read_group(cr, uid, domain, fields, groupby, offset=offset, limit=limit, context=context, orderby=orderby, lazy=lazy)
        if ('sales_usd') in fields:
            for record in res:
                if '__domain' in record:
                    records = self.search(cr, uid, record['__domain'], context=context)
                    usd_value = 0.0
                    for sale_report in self.browse(cr, uid, records, context=context):
                        usd_value += sale_report.sales_usd
                    record['sales_usd'] = usd_value
        if ('rm_cost') in fields:
            for record in res:
                if '__domain' in record:
                    records = self.search(cr, uid, record['__domain'], context=context)
                    rm_cost = 0.0
                    for sale_report in self.browse(cr, uid, records, context=context):
                        rm_cost += sale_report.rm_cost
                    record['rm_cost'] = rm_cost
        if ('sales_rm') in fields:
            for record in res:
                if '__domain' in record:
                    records = self.search(cr, uid, record['__domain'], context=context)
                    usd_value = 0.0
                    rm_cost = 0.0
                    sales_rm = 0.0
                    for sale_report in self.browse(cr, uid, records, context=context):
                        sales_rm += sale_report.sales_rm
                    record['sales_rm'] = sales_rm
        return res



    def init(self, cr):
        tools.drop_view_if_exists(cr, 'sale_order_report')
        print "in init++++++++"
        cr.execute("""
                  CREATE OR REPLACE VIEW sale_order_report AS (
                      SELECT
                        U.id AS id,
                        U.customer_id AS customer_id,
                        U.sale_order_id AS sale_order_id,
                        U.product_id AS product_id,
                        fph.formula_id AS formula_id,
                        U.vol_kg AS vol_kg,
                        U.sell_price AS sell_price,
                        fc.formula_cost AS formula_cost,
                        cast(U.date_order AS date) AS sale_date,
                        to_char(U.date_order, 'MM') :: Integer AS sale_month,
                        to_char(U.date_order, 'YYYY') :: Integer AS sale_year

                      FROM
                        (SELECT
                          row_number() OVER () AS id,
                          so.partner_id AS customer_id,
                          sl.order_id AS sale_order_id,
                          sl.product_id AS product_id,
                          max(fph.id) AS fph_id,
                          sl.product_uom_qty AS vol_kg,
                          sl.price_unit AS sell_price,
                          so.date_order AS date_order

                        FROM
                            sale_order_line sl INNER JOIN sale_order so ON sl.order_id=so.id
                            LEFT OUTER JOIN formula_product_history fph ON fph.product_id=sl.product_id
                        WHERE
                            so.state NOT IN ('draft', 'cancel') AND fph.set_datetime <= so.date_order
                        GROUP BY
                            so.partner_id,
                            sl.order_id,
                            sl.product_id,
                            sl.product_uom_qty,
                            sl.price_unit,
                            so.date_order) AS U
                        INNER JOIN
                        formula_product_history AS fph ON fph.id = U.fph_id
                        INNER JOIN
                        formula_c1 AS fc ON fph.formula_id = fc.id
                            )
                    """ )

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
#        sale_report_ids = self.pool.get('sale.order.report.wizard').browse(cr, uid, context.get('active_id'))
#        for sale_report in sale_report_ids:
#            from_date = sale_report.from_date
#            to_date = sale_report.to_date
#            context.update({'from_date': from_date})
#            context.update({'to_date': to_date})
#
#            if context.get('from_date',False):
#                args.append(['sale_date', '>=', context['from_date']])
#
#            if context.get('to_date',False):
#                args.append(['sale_date','<=', context['to_date']])

        return super(sale_order_report, self).search(cr, uid, args, offset, limit, order, context, count)
        # cr.execute("""CREATE OR REPLACE VIEW sale_order_report AS (
        # SELECT
        # row_number() OVER () as id,
        # A.customer_id as customer_id,
        # A.sale_order_id as sale_order_id,
        # A.product_id as product_id,
        # A.formula_id as formula_id,
        # A.vol_kg as vol_kg,
        # A.sell_price as sell_price
        #
        # FROM (SELECT
        # rp.id as customer_id,
        # sl.order_id as sale_order_id,
        # sl.product_id as product_id,
        # fph.formula_id as formula_id,
        # sl.product_uom_qty as vol_kg,
        # sl.price_unit as sell_price,
        # MAX(fph.set_datetime)
        # from
        # sale_order_line sl inner join sale_order so on sl.order_id=so.id
        # left outer join res_partner rp on sl.order_partner_id=rp.id
        # left outer join formula_product_history fph on fph.product_id=sl.product_id
        # where so.state not in ('draft', 'cancel') and fph.set_datetime <= so.date_order
        # and rp.customer = true
        # GROUP BY rp.id, sl.order_id, sl.product_id,fph.formula_id,sl.product_uom_qty,sl.price_unit) AS A,
        # (SELECT
        #  rp.id as customer_id,
        #  sl.order_id as sale_order_id,
        #  sl.product_id as product_id,
        #  fph.formula_id as formula_id,
        #  sl.product_uom_qty as vol_kg,
        #  sl.price_unit as sell_price,
        #  MAX(fph.set_datetime)from
        # sale_order_line sl inner join sale_order so on sl.order_id=so.id
        # left outer join res_partner rp on sl.order_partner_id=rp.id
        # left outer join formula_product_history fph on fph.product_id=sl.product_id
        # where so.state not in ('draft', 'cancel') and fph.set_datetime <= so.date_order
        # and rp.customer = true
        # GROUP BY rp.id, sl.order_id, sl.product_id,fph.formula_id,sl.product_uom_qty,sl.price_unit) AS B
        # WHERE A.customer_id=B.customer_id
        # AND A.sale_order_id=B.sale_order_id
        # AND A.product_id=B.product_id
        #  AND A.MAX>B.MAX
        # )""")
        # cr.execute("""
        #     CREATE OR REPLACE VIEW sale_order_report AS (
        #         WITH sl_fph AS(
        #             select sl.id, sl.product_id, MAX(fph.id) as fph_id
        #             FROM sale_order as so
        #             LEFT OUTER JOIN sale_order_line as sl ON sl.order_id = so.id
        #             LEFT OUTER JOIN formula_product_history as fph ON sl.product_id = fph.product_id
        #             WHERE so.date_order >= fph.set_datetime
        #
        #             GROUP BY sl.id, sl.product_id
        #         )
        #
        #     )"""
        # )
        # cr.execute("""
        #           CREATE OR REPLACE VIEW sale_order_report AS (
        #
        #               SELECT
        #                   row_number() OVER () AS id,
        #                   U.customer_id AS customer_id,
        #                   U.sale_order_id AS sale_order_id,
        #                   U.product_id AS product_id,
        #                   7 AS formula_id,
        #                   U.vol_kg AS vol_kg,
        #                   U.sell_price AS sell_price
        #                 FROM
        #                     (SELECT
        #                   row_number() OVER () AS id,
        #                   so.partner_id AS customer_id,
        #                   sl.order_id AS sale_order_id,
        #                   sl.product_id AS product_id,
        #                   max(fph.id) AS formula_id,
        #                   sl.product_uom_qty AS vol_kg,
        #                   sl.price_unit AS sell_price
        #                 FROM
        #                     sale_order_line sl INNER JOIN sale_order so ON sl.order_id=so.id
        #                     LEFT OUTER JOIN formula_product_history fph ON fph.product_id=sl.product_id
        #                 WHERE
        #                     so.state NOT IN ('draft', 'cancel') AND fph.set_datetime <= so.date_order
        #                 GROUP BY
        #                     so.partner_id,
        #                     sl.order_id,
        #                     sl.product_id,
        #                     sl.product_uom_qty,
        #                     sl.price_unit) AS U
        #
        #                 INNER JOIN
        #
        #                     (SELECT
        #                   row_number() OVER () AS id,
        #                   so.partner_id AS customer_id,
        #                   sl.order_id AS sale_order_id,
        #                   sl.product_id AS product_id,
        #                   max(fph.id) AS formula_id,
        #                   sl.product_uom_qty AS vol_kg,
        #                   sl.price_unit AS sell_price
        #                 FROM
        #                     sale_order_line sl INNER JOIN sale_order so ON sl.order_id=so.id
        #                     LEFT OUTER JOIN formula_product_history fph ON fph.product_id=sl.product_id
        #                 WHERE
        #                     so.state NOT IN ('draft', 'cancel') AND fph.set_datetime <= so.date_order
        #                 GROUP BY
        #                     so.partner_id,
        #                     sl.order_id,
        #                     sl.product_id,
        #                     sl.product_uom_qty,
        #                     sl.price_unit) AS V
        #
        #                 ON
        #                     U.customer_id = V.customer_id AND
        #                     U.sale_order_id = V.sale_order_id AND
        #                     U.product_id = V.product_id AND
        #                     U.formula_id = V.formula_id AND
        #                     U.vol_kg = V.vol_kg AND
        #                     U.sell_price = V.sell_price
        #                     )
        #             """ )
        # fph.formula_id,
         # and fph.set_datetime <= so.date_order
        # GROUP BY rp.id, sl.order_id, sl.product_id,fph.formula_id,sl.product_uom_qty,sl.price_unit
# left outer join product_product pp on sl.product_id=pp.id
#  left outer join formula_c1 fc on pp.formula_id=fc.id



        # print "cr fetch",None or cr.dictfetchall()

# GROUP BY rp.id, sl.order_id, sl.product_id,fph.formula_id,sl.product_uom_qty,sl.price_unit
#              sale_order_line sl inner join sale_order so on sl.order_id=so.id
#            left outer join product_product pp on sl.product_id=pp.id
#            left outer join formula_c1 fc on pp.formula_id=fc.id
#            left outer join res_partner rp on sl.order_partner_id=rp.id
#            left outer join formula_product_history fph on fph.product_id=pp.id
#            where  fph.set_datetime BETWEEN 2015-03-31 00:00:00 and 2017-03-31 00:00:00 and
#            so.state not in ('draft', 'cancel') and so.date_order BETWEEN 2015-03-31 00:00:00 and 2017-03-31 00:00:00
#            and rp.customer = true

#              MIN(id) as id,

              #              so.state as so_state,
#              sl.name,
#              pp.id,
#            fc1.final_product_id,
#            fph.formula_id,
            
#              select distinct rp.id as partner_id,sl.product_uom_qty,so.state as so_state,sl.name,sl.order_id,sl.price_unit,sl.product_id,pp.id,
#fc1.final_product_id,fph.formula_id,rp.customer, from
#sale_order_line sl inner join sale_order so on sl.order_id=so.id
#left outer join product_product pp on sl.product_id=pp.id
#left outer join formula_c1 fc on pp.formula_id=fc.id
#left outer join res_partner rp on sl.order_partner_id=rp.id
#left outer join formula_product_history fph on fph.product_id=pp.id
#where  fph.set_datetime BETWEEN set_datetime and set_datetime
#where so.state ilike 'done%'





