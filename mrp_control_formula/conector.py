# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.osv import fields, osv, orm
import xmlrpclib


class openerp_rpc(osv.osv):
    _name = 'openerp.rpc'
    _description = 'Conector RPC'

    def action_disconected(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, { 'state' : 'desconectado' }, context=None)
        return True

    def action_conectar(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids, context=context):
            try:
                dbname=this.db_destino
                username=this.user_destino
                pwd=this.pass_destino
                ipdestino=this.host_destino 
                sock_common = xmlrpclib.ServerProxy ('http://'+str(ipdestino)+':8069/xmlrpc/common')
                print "\n\n\nsock_common", sock_common
                conection = sock_common.login(dbname, username, pwd)
                #raise osv.except_osv(("notas"),str(conection))
                sock = xmlrpclib.ServerProxy('http://'+str(ipdestino)+':8069/xmlrpc/object')
                print "\n\n\nsock", sock
                if conection:
                    self.write(cr, uid, ids, {'state':'conectado' }, context=None)
                elif not conection:
                    self.write(cr, uid, ids, {'state':'desconectado' }, context=None)
                    pass
            except Exception, e:
                raise osv.except_osv(("Tiene un Dato Incorrector , Verifique Sus Datos"),str(e))
            finally:
                pass
        return True

    _columns = {
        'host_destino':fields.char('IP Destino',size=64),
        'db_destino':fields.char('Base de Datos',size=64,required=True),
        'user_destino':fields.char('Usuario',size=64,required=True),
        'pass_destino':fields.char('Password',size=64,required=True),
        'state':fields.selection([('desconectado','desconectado'),('conectado','conectado')],'Estado'),

    }
    _defaults = {
              'state': lambda *a: 'desconectado',
              }
openerp_rpc()
