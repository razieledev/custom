from openerp.osv import osv, fields


class machine(osv.Model):
    _name = 'machine'
    _columns = {
            'name': fields.char('Name',size=125),
            'code': fields.char('Code'),
            'product_type': fields.selection([('bmc', 'BMC'),('smc', 'SMC'),('premix', 'Premix'),('packaging','Packaging'),
                                              ('internal', 'Internal')], 'Product Type'),
            'use_default': fields.boolean('Use Default'),
        
        }
