from openerp import models, fields
from openerp import api
from openerp import workflow, fields


class mrp_production(models.Model):
    _inherit = 'mrp.production'
    
    master_id = fields.Many2one('master.mrp', 'MO')

    @api.multi
    def action_production_end(self):
        """ Changes production state to Finish and writes finished date."""
        for production in self:
            master = production.master_id if production.master_id else False
            batch_states = []
            if master:
                batch_states = [batch.state for batch in master.batch_ids if batch.id not in self._ids ]
            print "set(batch_states)+++", set(batch_states)
            print "(len(set(batch_states)) == 1 and  'done' in set(batch_states))",(len(set(batch_states)) == 1 and  'done' in set(batch_states)),'done' in set(batch_states)
            print "(len(set(batch_states)) > 1 and set(batch_states) in ['done', 'cancel'])",(len(set(batch_states)) > 1 and set(batch_states) in ['done', 'cancel']), set(batch_states) in ['done', 'cancel']
            if (len(set(batch_states)) == 1 and  'done' in set(batch_states)): 
                master.write({'state': 'done'})
            elif len(set(batch_states)) > 1 :
                
                states = [False for state in batch_states if state not in ['done', 'cancel'] ]
                print "in elif++++++", states
                if not set(states):
                    master.write({'state': 'done'})
                
        return super(mrp_production, self).action_production_end()


    @api.multi
    def confirm_check(self):
        print"===self-------",self
        #this method confirms the batches and checks availability for raw materials

        for batch in self:
            # if self._context.get('check', False):
            #     if batch.state == 'cancel':
            #         return {'error': 'Cannot Procced as the Batch %s is in cancelled state'%(self.name)}
            if batch.state in ('cancel', 'ready'): continue
            if batch.state == 'draft':
                workflow.trg_validate(batch._uid, 'mrp.production', batch.id, 'button_confirm', batch._cr)
                # batch.signal_workflow('button_confirm')
                # batch.action_confirm()
            # compues_company = self.env['res.company'].search([('name', '=', 'Compuestos SMC Mexico SA de CV' )])
            # batch.with_context(force_company = compues_company.id).action_assign()
            batch.action_assign()
            print"====batch.action_assign()batch.action_assign()=======",batch.action_assign()
#            batch.with_context(force_company = compues_company.id)
#            batch.action_assign()

        return True
