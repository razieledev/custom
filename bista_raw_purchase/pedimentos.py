from openerp.osv import osv, fields

class pedimentos(osv.Model):
    _name = 'pedimentos'
    _columns = {
            'name': fields.char('Name',size=125),
            'code': fields.char('Code',size=125),
        }
