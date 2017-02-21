from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp


class account_account(models.Model):

    _inherit = 'account.account'

    @api.multi
    @api.depends('debit', 'credit', 'balance')
    def _cal_debit_amt(self):
        account_move_line_obj = self.env['account.move.line']
        for rec in self:
            rec_lines = account_move_line_obj.search([('account_id', '=', rec.id), ('company_id','=', rec.company_id.id)])
            tot_deb = 0.0
            tot_cre = 0.0
            for move in rec_lines:
                if move.amount_currency > 0:
                    tot_deb += move.amount_currency
                elif move.amount_currency < 0:
                    tot_cre += move.amount_currency
            rec.cur_deb_amt = tot_deb
            rec.cur_cre_amt = tot_cre

    cur_deb_amt = fields.Float(string='Amount currency debit', readonly=True, compute='_cal_debit_amt')
    cur_cre_amt = fields.Float(string='Amount currency credit', readonly=True, compute='_cal_debit_amt')


class account_move(models.Model):

    _inherit = 'account.move'

    convert = fields.Boolean('covert')


class account_move_line(models.Model):

    _inherit = 'account.move.line'

    flag = fields.Boolean('Flag')
    amt_in_usd = fields.Float('Amt in USD', store=True,
                              digits=dp.get_precision('Product Price'),
                              compute='_cal_amt_in_usd')

    @api.multi
    @api.depends('debit', 'credit')
    def _cal_amt_in_usd(self):
        mxn_currency = self.env['res.currency'].search([('name', '=', 'MXN')])[0]
        usd_currency = self.env['res.currency'].search([('name', '=', 'USD')])[0]
        for rec in self:
            if rec.move_id and rec.move_id.state in 'draft':
                if rec.credit:
                    rec.amt_in_usd = -(mxn_currency.compute(rec.credit, usd_currency))
                if rec.debit:
                    rec.amt_in_usd = (mxn_currency.compute(rec.debit, usd_currency))

    @api.onchange('debit')
    def onchange_debit(self):
        res_currency_obj = self.env['res.currency']
        in_debit = self.debit
        usd_currency = res_currency_obj.search([('name', '=', 'USD')])
        out_currency = in_debit/usd_currency.rate_silent
        context = dict(self._context)
        line = context.get('line_id')
        if line and line[0]:
            if line[0][2]:
                if self.move_id.convert and not line[0][2].get('flag'):
                    self.debit = out_currency
                    self.flag = True
        elif self.move_id.convert:
            self.debit = out_currency
            self.flag = True

    @api.onchange('credit')
    def onchange_credit(self):
        res_currency_obj = self.env['res.currency']
        in_credit = self.credit
        usd_currency = res_currency_obj.search([('name', '=', 'USD')])
        out_currency = in_credit/usd_currency.rate_silent
        context = dict(self._context)
        line = context.get('line_id')
        if line and line[0]:
            if line[0][2]:
                if self.move_id.convert and not line[0][2].get('flag'):
                    self.credit = out_currency
                    self.flag = True
        elif self.move_id.convert:
            self.credit = out_currency
            self.flag = True
