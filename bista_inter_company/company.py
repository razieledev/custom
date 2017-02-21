from openerp import api, fields, models, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class ResCompany(models.Model):

    _inherit = "res.company"

    property_stock_account_input = fields.Many2one('account.account', string='Stock Input Account')
    property_stock_account_output = fields.Many2one('account.account', string='Stock Output Account')
    property_stock_valuation_account_id = fields.Many2one('account.account', string='Stock Valuation Account')
    property_stock_journal = fields.Many2one('account.journal', string='Stock Journal')
    property_account_income = fields.Many2one('account.account', string='Product Income Account')
    property_account_expense = fields.Many2one('account.account', string='Product Expensse Account')


class stock_quant(models.Model):

    _inherit = "stock.quant"

    def _get_accounting_data_for_valuation(self, cr, uid, move, context=None):
        context.update({'import_comp': move.company_id.id,
                        'default_company_id':context.get('force_company')})
        res = super(stock_quant,self)._get_accounting_data_for_valuation(cr, uid, move, context=context)
        return res


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.model
    def get_product_accounts(self, product_id):
        product_obj = self.browse(product_id)
        if product_obj.valuation == 'real_time' and self._context.get('import_comp'):
            company = self.env['res.company'].browse(self._context.get('import_comp'))
            stock_input_acc = company.property_stock_account_input and company.property_stock_account_input.id or False
            stock_output_acc = company.property_stock_account_output and company.property_stock_account_output.id or False
            account_valuation = company.property_stock_valuation_account_id and company.property_stock_valuation_account_id.id or False
            journal_id = company.property_stock_journal and company.property_stock_journal.id or False
            return {
                'stock_account_input': stock_input_acc,
                'stock_account_output': stock_output_acc,
                'stock_journal': journal_id,
                'property_stock_valuation_account_id': account_valuation
                }

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    def _choose_account_from_po_line(self, cr, uid, po_line, context=None):
        order = self.pool.get('purchase.order.line').browse(cr, uid, po_line.id).order_id
        company = self.pool.get('res.company').browse(cr, uid, order.company_id.id)
        fiscal_obj = self.pool.get('account.fiscal.position')
        property_obj = self.pool.get('ir.property')
        if po_line.product_id:
            acc_id = po_line.product_id.property_account_expense.id
            if not acc_id:
                acc_id = po_line.product_id.categ_id.property_account_expense_categ.id or company.property_account_expense and company.property_account_expense.id
            if not acc_id:
                raise Warning(_('Error!'), _('Define an expense account for this product: "%s" (id:%d).') % (po_line.product_id.name, po_line.product_id.id,))
        else:
            acc_id = property_obj.get(cr, uid, 'property_account_expense_categ', 'product.category', context=context).id
        fpos = po_line.order_id.fiscal_position or False
        return fiscal_obj.map_account(cr, uid, fpos, acc_id)

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        """Prepare the dict of values to create the new invoice line for a
           sales order line. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record line: sale.order.line record to invoice
           :param int account_id: optional ID of a G/L account to force
               (this is used for returning products including service)
           :return: dict of values to create() the invoice line
        """
        order = self.browse(cr, uid, line.id).order_id
        company = self.pool.get('res.company').browse(cr, uid, order.company_id.id)
        res = {}
        if not line.invoiced:
            if not account_id:
                if line.product_id:
                    account_id = line.product_id.property_account_income.id
                    if not account_id:
                        account_id = line.product_id.categ_id.property_account_income_categ.id or company.property_account_income and company.property_account_income.id
                    if not account_id:
                        raise Warning(_('Error!'),
                                _('Please define income account for this product: "%s" (id:%d).') % \
                                    (line.product_id.name, line.product_id.id,))
                else:
                    prop = self.pool.get('ir.property').get(cr, uid,
                            'property_account_income_categ', 'product.category',
                            context=context)
                    account_id = prop and prop.id or False
            uosqty = self._get_line_qty(cr, uid, line, context=context)
            uos_id = self._get_line_uom(cr, uid, line, context=context)
            pu = 0.0
            if uosqty:
                pu = round(line.price_unit * line.product_uom_qty / uosqty,
                        self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
            fpos = line.order_id.fiscal_position or False
            account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, account_id)
            if not account_id:
                raise Warning(_('Error!'),
                            _('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
            res = {
                'name': line.name,
                'sequence': line.sequence,
                'origin': line.order_id.name,
                'account_id': account_id,
                'price_unit': pu,
                'quantity': uosqty,
                'discount': line.discount,
                'uos_id': uos_id,
                'product_id': line.product_id.id or False,
                'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
            }
        return res

class stock_move(models.Model):
    _inherit = 'stock.move'

    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        company = self.pool.get('res.company').browse(cr, uid, move.company_id.id)
        fp_obj = self.pool.get('account.fiscal.position')
        # Get account_id
        fp = fp_obj.browse(cr, uid, context.get('fp_id')) if context.get('fp_id') else False
        name = False
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = move.product_id.property_account_income.id
            if not account_id:
                account_id = move.product_id.categ_id.property_account_income_categ.id or company.property_account_income and company.property_account_income.id
            if move.procurement_id and move.procurement_id.sale_line_id:
                name = move.procurement_id.sale_line_id.name
        else:
            account_id = move.product_id.property_account_expense.id
            if not account_id:
                account_id = move.product_id.categ_id.property_account_expense_categ.id or company.property_account_expense and company.property_account_expense.id
        fiscal_position = fp or partner.property_account_position
        account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)

        # set UoS if it's a sale and the picking doesn't have one
        uos_id = move.product_uom.id
        quantity = move.product_uom_qty
        if move.product_uos:
            uos_id = move.product_uos.id
            quantity = move.product_uos_qty

        taxes_ids = self._get_taxes(cr, uid, move, context=context)

        return {
            'name': name or move.name,
            'account_id': account_id,
            'product_id': move.product_id.id,
            'uos_id': uos_id,
            'quantity': quantity,
            'price_unit': self._get_price_unit_invoice(cr, uid, move, inv_type),
            'invoice_line_tax_id': [(6, 0, taxes_ids)],
            'discount': 0.0,
            'account_analytic_id': False,
        }

class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None):
        context = self._context
        company_id = company_id if company_id is not None else context.get('company_id', False)
        company = self.env['res.company'].browse(company_id)
        self = self.with_context(company_id=company_id, force_company=company_id)
        if not partner_id:
            raise except_orm(_('No Partner Defined!'), _("You must first select a partner!"))
        if not product:
            if type in ('in_invoice', 'in_refund'):
                return {'value': {}, 'domain': {'uos_id': []}}
            else:
                return {'value': {'price_unit': 0.0}, 'domain': {'uos_id': []}}

        values = {}

        part = self.env['res.partner'].browse(partner_id)
        fpos = self.env['account.fiscal.position'].browse(fposition_id)

        if part.lang:
            self = self.with_context(lang=part.lang)
        product = self.env['product.product'].browse(product)

        values['name'] = product.partner_ref
        if type in ('out_invoice', 'out_refund'):
            account = product.property_account_income or product.categ_id.property_account_income_categ or company.property_account_income
        else:
            account = product.property_account_expense or product.categ_id.property_account_expense_categ or company.property_account_expense
        account = fpos.map_account(account)
        if account:
            values['account_id'] = account.id

        if type in ('out_invoice', 'out_refund'):
            taxes = product.taxes_id or account.tax_ids
            if product.description_sale:
                values['name'] += '\n' + product.description_sale
        else:
            taxes = product.supplier_taxes_id or account.tax_ids
            if product.description_purchase:
                values['name'] += '\n' + product.description_purchase

        fp_taxes = fpos.map_tax(taxes)
        values['invoice_line_tax_id'] = fp_taxes.ids

        if type in ('in_invoice', 'in_refund'):
            if price_unit and price_unit != product.standard_price:
                values['price_unit'] = price_unit
            else:
                values['price_unit'] = self.env['account.tax']._fix_tax_included_price(product.standard_price, taxes, fp_taxes.ids)
        else:
            values['price_unit'] = self.env['account.tax']._fix_tax_included_price(product.lst_price, taxes, fp_taxes.ids)

        values['uos_id'] = product.uom_id.id
        if uom_id:
            uom = self.env['product.uom'].browse(uom_id)
            if product.uom_id.category_id.id == uom.category_id.id:
                values['uos_id'] = uom_id

        domain = {'uos_id': [('category_id', '=', product.uom_id.category_id.id)]}

        company = self.env['res.company'].browse(company_id)
        currency = self.env['res.currency'].browse(currency_id)

        if company and currency:
            if company.currency_id != currency:
                values['price_unit'] = values['price_unit'] * currency.rate

            if values['uos_id'] and values['uos_id'] != product.uom_id.id:
                values['price_unit'] = self.env['product.uom']._compute_price(
                    product.uom_id.id, values['price_unit'], values['uos_id'])

        return {'value': values, 'domain': domain}

