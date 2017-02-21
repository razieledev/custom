from openerp.osv import osv
from openerp.tools.translate import _
import datetime


class master_mrp(osv.Model):

    _inherit = ['master.mrp', 'mail.thread']

    def get_sudo_batches(self, cr, uid, batches, context):
        "FOr Manual MO, sudo batches are requied. Hence this function will return the sudo batches in required format"
        sudo_batches = []
        print "batches+++++++",batches
        for batch in range(0,batches):
            sudo_batches += [str(self.pool.get('ir.sequence').next_by_code(cr, uid,'sudo.machine.code',context)),
                             str(self.pool.get('ir.sequence').next_by_code(cr, uid,'sudo.machine.count.code',context))]

            # sudo_batches += str(self.pool.get('ir.sequence').next_by_code(cr, uid,'sudo.machine.code',context)) + ',' + '1' + ','
        return ','.join(sudo_batches) or False

    def export_mo(self, cr, uid, ids, context = None):
        """
        Bringing data in format below and posting it to weigh center app.
        {'Product':'SBT2000-B001', 'ProductType':'BMC',
        'ProductQty':'360','Mixer':'B01','Packing':'MASA',
        'ProductionDate':'10/11/2015','Batches':'1',
        'BatchWeight':'360','BatchesDesc':'B4150182,B4150183,B4150184',
        'Premix':'1','PremixDesc':'D001,D002,D003','Identifier':'ODOOID',
        'POCustomer':'ODOOPOCUSTOMER','MOrder':'ODOOMORDER'}
        """
        if isinstance(ids, (int, long)): ids = [ids]
        data_dict = {}
        for mo in self.browse(cr, uid, ids):
            batches, premixes,premixes_manual, default_mixer = [], [],[], ""
            manual = context.get('manual_mo_flow',False)
            if not mo.product_id: raise osv.except_osv(_('Warning!'), _('No Product defined on MO.') )
            if not mo.product_id.shared_product_id: raise osv.except_osv(_('Warning!'), _('No Unique Product ID defined for MO Product.') )
            if not mo.product_type: raise osv.except_osv(_('Warning!'), _('No Product type defined on MO.') )
            if not mo.product_qty: raise osv.except_osv(_('Warning!'), _('No Product quantity defined on MO.') )


            if not mo.date_planned: raise osv.except_osv(_('Warning!'), _('No Scheduled Date defined on MO.') )
            if not mo.batches: raise osv.except_osv(_('Warning!'), _('Number of Batches not defined on MO.') )
            if not mo.batch_qty: raise osv.except_osv(_('Warning!'), _('No Batch Weight defined on MO.') )
            if not mo.batch_ids: raise osv.except_osv(_('Warning!'), _('No Batches created for MO.') )
            if not manual:
                if not mo.pres_id: raise osv.except_osv(_('Warning!'), _('No Presentation defined on MO.') )
#                if not mo.sale_id: raise osv.except_osv(_('Warning!'), _('No Sale Order defined on MO.') )
                if not mo.machine_id: raise osv.except_osv(_('Warning!'), _('No Machine defined on MO.') )
            if mo.premix_product_id and not mo.premix_product_id.shared_product_id : raise osv.except_osv(_('Warning!'), _('No Unique Product ID defined for Premix Product.') )
            for batch in mo.batch_ids:
#                segregating mo batches and premixes on the basis of machine or disperser
                if batch.machine_id:
#                    batches.append([batch.name, batch.id])
                    batches += [str(batch.name), str(batch.id)]
#                     batches += batch.name + "," + str(batch.id) + ","
                if batch.disperser_id:
#                    premixes.append([batch.name, batch.id])
                    premixes += [str(batch.name), str(batch.id)]
#                     premixes += batch.name + "," + str(batch.id) + ","
            #     in case of Manual MO putting all the batches in premixes
                if manual:
                    # premixes_manual += (batch.name + "," + str(batch.id) + ",")
                    premixes_manual += [str(batch.name), str(batch.id)]
            if manual:
                default_mixer = self.pool.get('machine').search(cr, uid, [('use_default', '=', True)])
                if not default_mixer:
                    raise osv.except_osv(_('Warning!'), _('Please Select B0 as Default Mixer') )
                if isinstance(default_mixer, (list, tuple)): default_mixer = default_mixer[0]
                default_mixer = self.pool.get('machine').browse(cr, uid,default_mixer).code
                data_dict.update({
                    'Mixer': default_mixer or '' ,
                    'Disperser': mo.disperser_id and mo.disperser_id.code or '',
                    'BatchesDesc': self.get_sudo_batches(cr, uid, mo.batches, context),
                    'PremixDesc': ','.join(premixes_manual),
                    'Premix': mo.batches,
                    'PremixWeight': 0,
                    'PremixTotalWeight': 0,

                })
            else:
                # "In case of normal Master MO"
                data_dict.update({
                    'Mixer': mo.machine_id and mo.machine_id.code ,
                    'Disperser': mo.disperser_id and mo.disperser_id.code if mo.premix_product_id else '',
                    'BatchesDesc': ','.join(batches),
                    'PremixDesc': ','.join(premixes) if mo.premix_product_id else '',
                    'Premix': mo.tanks if mo.premix_product_id else '',
                    'PremixWeight': mo.tank_weight if mo.premix_product_id else '',
                    'PremixTotalWeight': mo.total_premix_weight if mo.premix_product_id else '',
                })

            data_dict.update({
            'Product': mo.product_id.name + ',' + str(mo.product_id.shared_product_id),
            'ProductType':  mo.product_type and mo.product_type.upper(),
            'ProductQty': mo.product_qty,
            'Packing': mo.pres_id and mo.pres_id.code or '',
            'ProductionDate': datetime.datetime.strptime(mo.date_planned,'%Y-%m-%d %H:%M:%S').date().strftime('%d/%m/%Y'),
            'Batches': mo.batches,
            'BatchWeight': mo.batch_qty,
#            'Identifier': [mo.name, mo.id],
            'SOCustomer':  (mo.sale_id and mo.sale_id.name + "," + str(mo.sale_id.id)) or '',
            'MOrder': mo.name + "," + str(mo.id),
            })
            # print "data dict manual+++++++",data_dict
            weigh_center = self.pool.get('weigh.center')
            weigh_id = weigh_center.get_mrp_web_service_id(cr, uid, context)
            if not weigh_id:
                raise osv.except_osv(_('Error!'), _('No WC Configuration/URL defined or Active.'))
            res = weigh_center.send_data(cr, uid, weigh_id, data_dict)
            # if isinstance(res, dict) and res.get('error', False):
            #     raise osv.except_osv(_('Error!'), _('"%s".') % res.get('message', ''))
            return res









