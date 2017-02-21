from openerp import models, fields, api
from openerp.osv import osv
from openerp.tools.translate import _


class product_product(models.Model):

    _inherit = 'product.product'

    shared_product_id = fields.Integer(string = 'Shared Product Id')
    is_international = fields.Boolean(string = 'Is International')
    tipo = fields.Selection([('R','R'), ('IC', 'IC'), ('CN', 'CN'), ('CF', 'CF')], help="This field is used for sending "
                                                                                        "raw material to WC")

    @api.model
    def create(self, vals):
        "overriding create to include shared product id through sequence"
        if not vals: vals = {}
        # Restricting the creation of product_product through template to assign Shared product Id.
        if not vals.get('product_tmpl_id', False):
            raise osv.except_osv(_('Warning!'), _('Please create Product through Product Template.'))
        tmp_id = vals.get('product_tmpl_id', False)
        tmp_brw = self.env['product.template'].browse(tmp_id)
        # if template is Formula bring product sequence for formula
        seq = 0
        if not tmp_brw.product_type:
            raise osv.except_osv(_('Warning!'), _('Please enter Product Type!'))
        if tmp_brw.product_type == 'miselaneous':
            return super(product_product, self).create(vals=vals)

        if tmp_brw.formula:
            seq = self.env['ir.sequence'].next_by_code('formula.shared.id')
        else:
            type = tmp_brw.product_type
            if type in ('smc', 'bmc', 'premix'):
                seq = self.env['ir.sequence'].next_by_code('final.shared.id')
            elif type in ('otros', 'empaque'):
                seq = self.env['ir.sequence'].next_by_code('otros.empaque.shared.id')
            else:
                seq = self.env['ir.sequence'].next_by_code('%s.shared.id'%(type))

        vals.update({'shared_product_id': seq,
                                })
        return super(product_product, self).create(vals=vals)

    @api.one
    def export_raw_material(self):
        '''Format to be send:
        {"Identificador":2000056,"codigo":"RP0002","desc":"Resina S342","tipo":"R"}

        :return:
        '''
        if not self.product_type:
            raise osv.except_osv(_('Warning'), _('If this is a Raw Material then select Product type as Raw material.'))
        if not self.tipo:
            raise osv.except_osv(_('Warning'), _('Please enter Tipo.'))
        if not self.default_code:
            raise osv.except_osv(_('Warning'), _('Please enter Internal reference.'))
        data = {'Identificador': self.shared_product_id, 'codigo': self.default_code, 'desc': self.name, 'tipo': self.tipo}
        # weigh_center = self.pool.get('weigh.center')
        weigh_center = self.env['weigh.center']
        # weigh_id = weigh_center.get_add_rm_ws_id(self._cr, self._uid, self._context)
        weigh_id = weigh_center.get_add_rm_ws_id()
        if not weigh_id:
            raise osv.except_osv(_('Error!'), _('No Add Raw Material Configuration/URL defined or Active.'))
        # return True
        # context = context.update({'is_not_json': False})
        if weigh_id:
            # weigh_center.send_data(self._cr, self._uid, weigh_id, data, self._context)
            weigh_center.browse(weigh_id).send_data(data = data)

class stock_move(models.Model):

    _inherit = 'stock.move'
    is_international = fields.Boolean(related='product_id.is_international', string = 'Is International', store=True)
