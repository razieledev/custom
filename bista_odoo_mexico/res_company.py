############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields


class res_company(osv.Model):
    _inherit = 'res.company'

    _columns = {
        'mexican_localization': fields.boolean('Apply Mexican Localization'),
        'is_manufacturing_company': fields.boolean('Is Manufacturing Company'),
    }
    
    def onchange_mexican_localization(self, cr, uid, ids, localization, context=None):
        if isinstance(ids, (int,long)): ids = [ids]
        companies = self.browse(cr, uid, ids)
        val = False
        if localization:
            for company in companies:
                val = True if company.currency_id and company.currency_id.name == 'MXN' else False
        return {'value': {'mexican_localization': val}}