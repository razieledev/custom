import requests
import json
from openerp.osv import osv, fields
from openerp.tools.translate import _


class weigh_center(osv.Model):
    """
        This class have configuration parameters to connect to weight center and
        associated methods.
    """
    _name = 'weigh.center'
    _columns = {
        'name': fields.char('Name', required = 1),
        'url': fields.char('URL', required = 1),
        'active': fields.boolean('Active'),
        # 'add_formula': fields.boolean('AddFormula'),
        'type': fields.selection([('add_production', 'Add Production'), ('add_formula', 'Add Formula'),
                                  ('add_raw_material', 'Add Raw Material')])
    }

    def get_mrp_web_service_id(self, cr, uid, context = None):
        'This function returns the ID of Web Service used to take MRP Production requests'
        ws_ids =  self.search(cr, uid, [('active', '=', True), ('type', '=', 'add_production')])
        return ws_ids and ws_ids[0]

    def get_add_formula_web_service_id(self, cr, uid, context = None):
        'This function returns the ID of Web Service used to send Formula requests'
        ws_ids =  self.search(cr, uid, [('active', '=', True), ('type', '=', 'add_formula')])
        return ws_ids and ws_ids[0]

    def get_add_rm_ws_id(self, cr, uid, context = None):
        'This function returns the ID of Web Service used to send Raw material requests'
        ws_ids =  self.search(cr, uid, [('active', '=', True), ('type', '=', 'add_raw_material')])
        return ws_ids and ws_ids[0]

    def send_data(self, cr, uid, ids, data = {}, context = None):
        if context == None: context = {}
        if isinstance(ids, (int, long)): ids = [ids]
        if not data:
            return {'error': True, 'message' : 'No data to be sent'}
        # print 'data+++++++++',json.dumps(data)
        # erere
#        data1 = {'Product':'SBT20
        # erer00-B001', 'ProductType':'BMC',
#                'ProductQty':'360','Mixer':'B01','Packing':'MASA',
#                'ProductionDate':'10/11/2015','Batches':'1',
#                'BatchWeight':'360','BatchesDesc':'B4150182,B4150183,B4150184',
#                'Premix':'1','PremixDesc':'D001,D002,D003','Identifier':'ODOOID',
#                'POCustomer':'ODOOPOCUSTOMER','MOrder':'ODOOMORDER'}
#         json_data = data
#         if not context or context.get('is_not_json', False) == True:
#             json_data = json.dumps(data)
#         data = {"customer": 1, "Formula": "LP-tmc-7000-t001,3000001,3000000", "version": 0,
#                 "bom_lines": "AD0001,100001,25.0,RE0008,800007,25.0,MI0005,600005,50.0"}
#         data = '{"Formula":"SBT4000-B004,3000001,3000000", "bom_lines":"RP0002,1,13.41,AD0009,100009,10.15,AD0029,100029,0.5,CA0002,200001,0.2,CA0003,200002,0.2,IN0004,300003,0.02,DE0001,400000,1,PI0001,500000,0.008,MI0005,600004,61.512,RE0006,800005,13","customer":1,"version":12}'
        for wc_conf in self.browse(cr, uid, ids):
            headers = {'Content-type': 'application/json','Accept':'text/plain'}
            #headers = {'Content-Type': 'application/jsonrequest', 'type': "json", 'url': "ProductionService.asmx/AddProductionWS"}
#            "http://189.211.180.26:8088"
#             print "json.dumps(data)+++",json.dumps(data)
            try:
                res = requests.post(wc_conf.url,headers = headers, data = json.dumps(data))
                # json.dumps(data)
            except Exception, e:
                # res = {'error':True ,'message':e}
                raise osv.except_osv(_('Error!'), _('"%s"'%(e)))
                # return res
            print "response",res.text
            print "data json", json.dumps(data)
            return res
