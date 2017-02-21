# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import api
from openerp import models, fields
import logging
_logger = logging.getLogger(__name__)


class assign_pd_cove(models.TransientModel):
    _name = 'assign.pd.cove'
    _description = 'Assign Pedimentos and Cove'
    
    pedimentos_id = fields.Many2one('pedimentos', string = 'Pedimento No.')
    cove = fields.Char(string = 'Cove')
    
    @api.one
    def assign_pd_cove(self):
        picking_ids, po_ids, so_ids, po = [], [], [], False
        active_id = self.env.context('active_id')
        po_obj = self.env['purchase.order']
        so_obj = self.env['sale.order']
        picking_obj = self.env['stock.picking']
        picking = picking_obj.browse(active_id)
        if picking.origin:
            po_ids = po_obj.search([('name','=', picking.origin)])
        po = po_ids[0] if po_ids else False
        if po.ref_po_id:
            so_ids = so_obj.search([('ref_po_id', '=', po.ref_po_id.id), ('company_id', '=', picking.company_id.id)])
        so = so_ids[0] if so_ids else False
        picking_ids.append(picking.id)
