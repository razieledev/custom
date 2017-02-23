from openerp import models, fields, api, exceptions

class mrp_production(models.Model):
    _inherit = 'mrp.production'

    #Product Related Fields
    preform_id = fields.Many2one(related='product_id.preform_id')
    product_color = fields.Many2one(related='preform_id.color_id')
    product_cuello = fields.Many2one(related='preform_id.cuello_id')
    product_peso_gr = fields.Float(related='preform_id.peso_gr')

    product_resina = fields.Char(related='product_id.resina')
    product_height = fields.Float(related='product_id.height')
    product_volume = fields.Float(related='product_id.volume')
    bottles_per_hour = fields.Float(related='product_id.bottles_per_hour')

    #calculation MO

    total_hours = fields.Float('Total De Horas', compute = 'compute_total_hours', store = True)
    total_shifts = fields.Float('Total De Turnos', compute = 'compute_total_shifts', store = True)
    total_days = fields.Float('Total Days', compute = 'compute_total_days', store = True)

    @api.depends('product_qty')
    def compute_total_hours(self):
        for mo in self:
            mo.total_hours =  mo.product_qty/mo.bottles_per_hour if mo.bottles_per_hour > 0 else 0

    @api.depends('total_hours')
    def compute_total_shifts(self):
        for mo in self:
            mo.total_shifts = mo.total_hours/7.5

    @api.depends('total_shifts')
    def compute_total_days(self):
        for mo in self:
            mo.total_days = mo.total_shifts/2