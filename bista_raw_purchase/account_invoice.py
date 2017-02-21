from openerp import models, fields, api, _
from openerp.exceptions import Warning


class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"
    
    lot_id = fields.Many2one('stock.production.lot', string='Lot Id')
    pedimentos_id = fields.Many2one('pedimentos', string='Pedimentos')
    
    
class account_invoice(models.Model):

    _inherit = "account.invoice"

    stock_move_ids = fields.One2many('stock.move', 'inv_id', string='Stock Moves')
    inv_sent = fields.Boolean('Sent')
    inv_sent_date = fields.Date('Inv Sent Date')

    # @api.multi
    # def invoice_validate(self):
    #     """ Validated invoice generate cross invoice base on company rules """
    #     for invoice in self:
    #         if invoice.company_emitter_id.mexican_localization:
    #             user_com = self.env['res.users'].browse(self._uid).company_id
    #             if not invoice.company_emitter_id.id == user_com.id:
    #                 raise Warning(_("Please change current login user's company as per the invoice company"))
    #     return super(account_invoice, self).invoice_validate()
