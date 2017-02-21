from openerp import models, api

# class procurement_order(models.Model):
#
#     _inherit = 'procurement.order'
#
#     @api.cr_uid_ids_context
#     def make_po(self, cr, uid, ids, context=None):
#         """
#         Stopping the flow of MTO and Buy in case of Confirming MO.
#         :param cr:
#         :param uid:
#         :param ids:
#         :param context:
#         :return:
#         """
#         print "in make po for MO+++++++++++++++++++++",
#
#         res = {}
#         for procurement in self.browse(cr, uid, ids, context=context):
#             # Just oing in this way as found that when proc created from MO does not have Group Id
#             # To be improved in future
#             if not procurement.group_id:
#                 print "no proc group id+++++++++++++"
#                 res[procurement.id] = False
#                 print "breaking the make PO flow+++++++++++++++++"
#                 return res
#             else:
#                 return super(procurement_order, self).make_po(cr, uid, ids, context=context)
#
