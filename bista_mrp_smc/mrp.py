from openerp.osv import osv, fields
from openerp.tools.translate import _


class mrp_production(osv.Model):
    _inherit = 'mrp.production'

    _columns = {
        'machine_id': fields.many2one('machine','Machine'),
        'disperser_id': fields.many2one('disperser','Disperser'),
        'select_send': fields.boolean(string = 'Send', help = 'Select this field to mark Batch to be sent to WC.'),
    #            'machine': fields.selection([('b1', 'B1'),('b2', 'B2'),('b3', 'B3'),
#                                        ('b4', 'B4'),('b5', 'B5'),('s1', 'S1'),
#                                        ('s2', 'S2'),
#                                        ], 'Machine')
        }
    _defaults = {
        'name': '/',
    }
    # _sql_constraints = []
    
    def create(self, cr, uid, vals, context = None):

            # Handles Premixes, batches and extra MO and their sequences.

        # If the batch is created from master then only apply rules for Premix and batches
        # This context 'has_master' is passed from Button Create Batches on Master Mo to diffrentiate between Manual and Normal flow.
        if context.get('has_master', False):
            if context.get('premix', False):
                disperser=self.pool.get('master.mrp').browse(cr, uid, vals['master_id']).disperser_id.id
                if not disperser:
                    raise osv.except_osv(_('Warning!'), _('Cannot create Batch as no Disperser is  is selected in MO for premix product') )
                disperser_brw=self.pool.get('disperser').browse(cr,uid,disperser)
                vals.update({'name': self.pool.get('ir.sequence').next_by_code(cr, uid,'%s.machine.code'%(disperser_brw.code),context),
                             'disperser_id': disperser   })

            else:
                machine = vals.get('machine_id', False)
                if not machine and vals.get('master_id', False):
                    machine = self.pool.get('master.mrp').browse(cr, uid, vals.get('master_id')).machine_id.id

                if not machine:
                    raise osv.except_osv(_('Warning!'), _('Cannot create Batch as no Machine is selected in MO'))
                machine_brw=self.pool.get('machine').browse(cr,uid,machine)
                vals.update({'name': self.pool.get('ir.sequence').next_by_code(cr, uid,'%s.machine.code'%(machine_brw.code),context),
                                'machine_id': machine})
        # In case batches are created manually
        else:
            disperser=self.pool.get('master.mrp').browse(cr, uid, vals['master_id']).disperser_id.id
            if not disperser:
                raise osv.except_osv(_('Warning!'), _('Cannot create Batch as no Disperser is selected in MO.') )
            # disperser_brw=self.pool.get('disperser').browse(cr,uid,disperser)
            # seq_name = self.pool.get('ir.sequence').next_by_code(cr, uid,'manual.machine.code',context) or False
            # if seq_name:
            #     seq_name_lst = list(seq_name)
            #     seq_name_lst.insert(0,'A')
            #     seq_name = ''.join(seq_name_lst)
            vals.update({'name': self.pool.get('ir.sequence').next_by_code(cr, uid,'manual.machine.code',context) or False})
        
        return super(mrp_production, self).create(cr, uid, vals, context)


class stock_move(osv.Model):

    _inherit = 'stock.move'

    _columns = {
            'indice': fields.related('product_id', 'indice', type='char', relation='product.product', string='Indice', store=True),
        }

    _order = "indice asc"

class mrp_bom(osv.osv):

    _inherit = 'mrp.bom'

    _columns = {
            'rev_no': fields.char('Revision No'),
        }
