# -*- coding: utf-8 -*-
from openerp.osv import fields, osv


class facturae_config_settings(osv.osv_memory):
    _name = 'facturae.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company',),
        'module_l10n_mx_facturae': fields.boolean('Electronic Invoicing CFD',
                                                  help="""This installs the module electronic invoicing CFD"""),
        'module_l10n_mx_facturae_cbb': fields.boolean('Electronic Invoicing CBB',
                                                      help="""This installs the module electronic invoicing CBB"""),
        'module_l10n_mx_facturae_pac_sf': fields.boolean('Electronic Invoicing CFDI',
                                                         help="""This installs the module electronic invoicing CFDI"""),
        'email_tmp_id': fields.many2one('email.template', 'Email Template',
                                        help="""This email template will be assigned for electronic invoicing in your company"""),
        'temp_report_id': fields.many2one('ir.actions.report.xml', 'Report Template',
                                          help="""This report template will be assigned for electronic invoicing in your company"""),
        'mail_server_id': fields.many2one('ir.mail_server', 'Outgoing Mail Server',
                                          help="""This outgoing mail server will be assigned by your company"""),
    }

    def open_parameters_pac(self, cr, uid, ids, context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Parameters Pac',
            'view_mode': 'tree,form',
            'res_model': 'params.pac',
        }

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id

    _defaults = {
        'company_id': _default_company,
    }

    def get_default_email_tmp_id(self, cr, uid, fields, context=None):
        company_id = self.pool.get('res.users').browse(
            cr, uid, uid, context=context).company_id.id
        email_obj = self.pool.get('email.template')
        email_tmp_id = False
        dat = email_obj.search(
            cr, uid, [('model', 'like', 'account.invoice'), ('company_id', '=', company_id)])
        data = dat and dat[0] or False
        if data:
            email_tmp_id = email_obj.browse(cr, uid, data)
        return {'email_tmp_id': email_tmp_id and email_tmp_id.id or False, }
    
    def get_default_mail_server_id(self, cr, uid, fields, context=None):
        company_id = self.pool.get(
            'res.users')._get_company(cr, uid, context=context)
        mail_server_obj = self.pool.get('ir.mail_server')
        mail_server_id = mail_server_obj.search(
            cr, uid, [('company_id', '=', company_id),
            ('active', '=', True)], limit = 1)
        return {'mail_server_id': mail_server_id or False}

    def get_default_temp_report_id(self, cr, uid, fields, context=None):
        report_id = False
        temp_report_obj = self.pool.get('report.multicompany')
        temp_report_ids = temp_report_obj.search(
            cr, uid, [('model', '=', 'account.invoice')], limit=1)
        if temp_report_ids:
            report_id = temp_report_obj.browse(
                cr, uid, temp_report_ids)[0].report_id.id
        return {'temp_report_id': report_id or False}

    def create(self, cr, uid, values, context=None):
        confg_id = super(facturae_config_settings, self).create(
            cr, uid, values, context)
        print "in create+++++++++++++++"
        report_company_obj = self.pool.get('report.multicompany')
        email_obj = self.pool.get('email.template')
        if values.get('mail_server_id') and values.get('email_tmp_id') and values.get('temp_report_id'):
            confg_data = self.browse(cr, uid, confg_id, context=context)
            email_obj.write(cr, uid, [confg_data.email_tmp_id.id], {
                            'company_id': confg_data.company_id.id,
                            'mail_server_id': confg_data.mail_server_id.id,
                            'report_template': values.get('temp_report_id')},
                            context=context)
            report_company_obj.report_multicompany_create(
                cr, uid, values.get('temp_report_id'), values.get('company_id'), context=context)        
        return confg_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
