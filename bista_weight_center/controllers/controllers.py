# -*- coding: utf-8 -*-
from openerp import http
from openerp.addons.web.http import request
from openerp.tools.translate import _


class my_controller(http.Controller):
    @http.route('/test', type='json', auth="none")
    def test(self, **kw):
        '''
        This method will automate the mrp flow by consuming the raw materials.
        Each Request entry will be stored in wc_request and proccessed.
        :param kw:
        :return:
        '''
        request._cr = request.registry.cursor()
        wc_req = request.registry['wc.request']
        # compues_user_ids = request.registry['res.users'].search(request._cr, 1, [('login', '=', 'compu_user')])
        #if wc user not found then using admin as wc user
        wc_user_id = 1
        # if compues_user_ids and isinstance(compues_user_ids, (list, tuple)):
        #     wc_user_id = compues_user_ids[0]

        # If this is a duplicate request directly return.
        dup_ids = wc_req.search(request._cr, wc_user_id,[('shared_product_id','=', kw.get('product_id', False)),
                                                ('product_qty', '=', kw.get('product_qty', 0)),
                                                ('batch_id', '=', kw.get('batch_id', False))])

        wc_id = wc_req.create(request._cr, 1, {'wc_id': kw.get('wc_id', False), 'shared_product_id': kw.get('product_id', False),
                                       'product_qty': kw.get('product_qty', 0), 'batch_id': kw.get('batch_id', False),
                                        'lot_name': kw.get('lot', '')})
        if dup_ids:
            wc_req.browse(request._cr, wc_user_id,wc_id).message_post(body=_('Duplicate Request'))
            wc_req.write(request._cr, wc_user_id,wc_id, {'state': 'cancel'})
            return True
        # return True
        context = {}
        context.update(kw)
        try:
            wc_req.run(request._cr, wc_user_id, wc_id, context = context)
        except Exception as e:
            wc_req.browse(request._cr, wc_user_id,wc_id).message_post(body=_(str(e)))
            wc_req.write(request._cr, wc_user_id,wc_id, {'state': 'exception'})
        # print "successfully completed request"
        return True


    @http.route('/Produce', type='json', auth="none")
    def Produce(self, **kw):
        '''
        This method will automate the mrp flow by Producing the Product.
        The Produce functionality of the MO will be fired when we receive the final finished qty request.
        :param kw:
        :return:
        '''
        request._cr = request.registry.cursor()
        fin_qt = request.registry['finished.qty']
        # compues_user_ids = request.registry['res.users'].search(request._cr, 1, [('login', '=', 'compu_user')])
        #if wc user not found then using admin as wc user
        wc_user_id = 1
        # if compues_user_ids and isinstance(compues_user_ids, (list, tuple)):
        #     wc_user_id = compues_user_ids[0]

        # If this is a duplicate request directly return.
        dup_ids = fin_qt.search(request._cr, wc_user_id,[('Idcontenedor', '=', kw.get('Idcontenedor', False)),
                                                          ('Lotes', '=', kw.get('Lotes', False)),
                                                          ('idlote', '=', kw.get('idlote', False)),
                                                          ('pesoneto', '=', kw.get('pesoneto', False)),
                                                           ('pesobruto', '=', kw.get('pesobruto', False)),
                                                            ('morden', '=', kw.get('morden', False)),
                                                            ('sorden', '=', kw.get('sorden', False)),
                                                            ('corden', '=', kw.get('corden', False)),
                                                            ('final', '=', kw.get('final', False)),
                                                            ('fecha', '=', kw.get('fecha', False)),
                                                            ('formulaid', '=', kw.get('formulaid', False)),
                                                            ('clienteid', '=', kw.get('clienteid', False)),
                                                            ('ul', '=', kw.get('ul', False)),
                                                         ('premix', '=', kw.get('premix', False))])
        print "kw+++++++", kw

        fin_id = fin_qt.create(request._cr, 1, {'Idcontenedor': kw.get('Idcontenedor', False),
                                              'Lotes': kw.get('Lotes', False),
                                              'idlote': kw.get('idlote', False),
                                              'pesoneto': kw.get('pesoneto', False),
                                               'pesobruto': kw.get('pesobruto', False),
                                               'morden': kw.get('morden', False),
                                                'sorden': kw.get('sorden', False),
                                                'corden': kw.get('corden', False),
                                                'final': kw.get('final', False),
                                                'fecha': kw.get('fecha', False),
                                                'formulaid': kw.get('formulaid', False),
                                                'clienteid': kw.get('clienteid', False),
                                                'ul': kw.get('ul', False),
                                                'premix': kw.get('premix', False)})
        if dup_ids:
            # fin_qt.browse(request._cr, wc_user_id,wc_id).message_post(body=_('Duplicate Request'))
            fin_qt.write(request._cr, wc_user_id,fin_id, {'state': 'cancel'})
            return True
        # return True

        # context = {}
        # context.update(kw)
        mo_obj = request.registry['master.mrp']
        mo_ids = mo_obj.search(request._cr, wc_user_id, [('name', '=', kw.get('morden', False))])
        if mo_ids:
            fin_qt.write(request._cr, wc_user_id,fin_id, {'master_mrp_id': mo_ids[0], 'state': 'assigned'})
        else:
            fin_qt.write(request._cr, wc_user_id,fin_id, {'state': 'unassigned'})
        context = {'premix': kw.get('premix', False)}

        # try:
        print "in try+++++++++++",kw.get('final', False), int(kw.get('final', False)) != 0
        if kw.get('final', False) and int(kw.get('final', False)) != 0:
            print "in final if++++++++++"
            mo_obj = request.registry['master.mrp']
            mo_obj.produce(request._cr, wc_user_id,mo_ids, context=context)
        # except Exception as e:
        #     mo_obj.browse(request._cr, wc_user_id,mo_ids[0]).message_post(body=_(str(e)))
        #     print "excepriton++",e
        # print "successfully completed request"
        return True

