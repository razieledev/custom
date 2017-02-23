from openerp import models, fields, api, exceptions

class Color(models.Model):
    _name = 'color'

    code = fields.Char('Color Code')
    name = fields.Char('Color')

class Cuello(models.Model):
    _name = 'cuello'

    code = fields.Char('Cuello Code')
    name = fields.Char('Cuello')

class BottleModel(models.Model):
    _name = 'bottle.model'
    code = fields.Char('Model Code')
    name = fields.Char('Molde')


class product_product(models.Model):
    _inherit = 'product.product'

    #fields for Raw material i.e Preforms
    color_id = fields.Many2one('color', string = 'Color')
    cuello_id = fields.Many2one('cuello', string = 'Cuello')
    peso_gr = fields.Float('Peso gr.')

    # fields for Salebale products i.e Bottles
    bottle_model = fields.Many2one('bottle.model', string = 'Molde')
    preform_id = fields.Many2one('product.product', 'Preform')
    preform_color = fields.Many2one(related='preform_id.color_id')
    preform_cuello = fields.Many2one(related='preform_id.cuello_id')
    preform_peso_gr = fields.Float(related='preform_id.peso_gr')
    resina = fields.Char('Resina')
    height = fields.Float('Altura(mm)', help='Height Of bottle')
    partner_id = fields.Many2one('res.partner', 'Product Partner')

    #For MRP
    bottles_per_hour = fields.Float('Bottelas Por Hora')

    @api.multi
    def generate_reference(self):
        if not self.partner_id:
            raise exceptions.Warning('Please select Customer for the Product.')

        if not self.partner_id.product_code:
            raise exceptions.Warning('Please enter Product Code to be used for Customer.')
        if not self.bottle_model:
            raise exceptions.Warning('Please enter Molde No.')
        if not self.preform_id:
            raise exceptions.Warning('Please select the Preform.')
        if not self.preform_color:
            raise exceptions.Warning('Please enter Color of Preform')
        if not self.preform_cuello:
            raise exceptions.Warning('Please enter Cuello of Preform')
        if not self.preform_peso_gr:
            raise exceptions.Warning('Please enter Preform Peso Gr.')
        if not self.resina:
            raise exceptions.Warning('Please enter Resina for Product.')
        self.default_code = '-'.join([self.partner_id.product_code, self.bottle_model.code + self.preform_cuello.code,
                unicode(self.volume)+self.preform_color.code+unicode(self.preform_peso_gr)+
                                      self.resina, unicode(self.height)])





