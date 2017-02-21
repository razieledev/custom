from openerp import models, fields, api


class stock_production_lot(models.Model):
    _inherit = 'stock.production.lot'

    name = fields.Char('Name')
    date = fields.Date('Date')
    exp_date = fields.Date('Expiry Date')
    picking_id = fields.Many2one('stock.picking', 'Picking')
    inspector = fields.Many2one('res.partner', 'Name of Inspector')
#    inspector = fields.Char('Name of Inspector')
    supplier_ref = fields.Char('Supplier Ref.')
    lote = fields.Char('Supplier Batch ID')
    note = fields.Text('Notes')
    obs = fields.Text('Observation')
    de_material = fields.Text('USO ECLUSIVO DE MATERIAL')
    label = fields.Boolean('Label Printed')
    company_id = fields.Many2one('res.company', 'Company')
    header = fields.Selection([('prod_proceso','PRODUCTO EN PROCESO'),('materia_prima',' MATERIA PRIMA')])

    _defaults = {
        'name': '/',
    }

    @api.model
    def create(self, vals):
        print"selffffffffffffffffff",self
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('stock.production.lot') or '/'
        return super(stock_production_lot, self).create(vals)

    @api.one
    def serial_revision(self):
        serial_revision_id = self.env['serial.revision'].search([])[0]
        if serial_revision:
            return int(serial_revision_id.serial_revision)

    @api.model
    def search(self,args, offset=0, limit=0, order=None,count=False):
        "Bringing the order from view's action - context "
        if self._context.get('order'): order = self._context.get('order')
        return super(stock_production_lot, self).search(
            args, offset=offset, limit=limit, order=order,
           count=count)


class serial_revision(models.Model):
    '''This holds the revision number to be printed on Labels'''
    _name = 'serial.revision'

    serial_revision = fields.Char('Revision')
