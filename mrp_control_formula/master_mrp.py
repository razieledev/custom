from openerp.osv import osv, fields


class master_mrp(osv.Model):
    _inherit = 'master.mrp'

    _columns = {
        'formula_id': fields.many2one('formula.c1', 'Revision'),
    }
