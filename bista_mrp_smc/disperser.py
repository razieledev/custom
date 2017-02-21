from openerp.osv import osv, fields

class disperser(osv.Model):
    _name = 'disperser'
    _columns = {
            'name':fields.char('Name',size=125),
            'code':fields.char('Code',size=125),
            'product_type': fields.selection([('bmc', 'BMC'),('smc', 'SMC'),('premix', 'Premix'),('packaging','Packaging')], 'Product Type')
        
        }
