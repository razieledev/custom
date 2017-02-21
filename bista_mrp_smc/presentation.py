from openerp.osv import osv, fields


class presentation(osv.Model):
    _name = 'presentation'
    _columns = {
            'type': fields.char('Name',size=125),
            'code': fields.char('Code',size=125),
            'product_type': fields.selection([('bmc', 'BMC'),('smc', 'SMC'),('premix', 'Premix'),('packaging','Packaging')], 'Product Type')
        
        }
    _rec_name = "type"