from openerp.osv import fields, osv

class procurement_order(osv.osv):
    _inherit = 'procurement.order'


    def _get_po_line_values_from_proc(self,cr, uid, procurement, partner, company, schedule_date, context):
        res = super(procurement_order,self)._get_po_line_values_from_proc(cr, uid, procurement, partner, company, schedule_date, context = context)

        res.update({'product_packaging': context.get('product_packaging', False),
                        'packaging_qty': context.get('packaging_qty', False)})

        return res