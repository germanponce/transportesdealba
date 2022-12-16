# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WobinMovesAdvSetLines(models.Model):
    _name = 'wobin.moves.adv.set.lines'
    _description = 'Wobin Moves Advances Settlements Lines'
    _inherit = ['mail.thread', 'mail.activity.mixin']     
                                                                

    check_selection = fields.Boolean(string=' ')
    operator_id     = fields.Many2one('res.partner',string='Operator', ondelete='cascade')
    trip_id         = fields.Many2one('wobin.logistics.trips', string='Trip', ondelete='cascade')
    advances_ids             = fields.One2many('wobin.advances', 'mov_lns_ad_set_id', string='Related Advances', ondelete='cascade')#, compute='set_advances', store=True)
    comprobations_ids        = fields.One2many('wobin.comprobations', 'mov_lns_ad_set_id', string='Related Comprobations', ondelete='cascade')#, compute='set_comprobations', store=True)
    advances_sum_amount      = fields.Float(string='Advances', digits=(15,2), compute='_set_advances_sum_amount', store=True)
    comprobations_sum_amount = fields.Float(string='Comprobations', digits=(15,2), compute='_set_comprobations_sum_amount', store=True)
    amount_to_settle      = fields.Float(string='Amount to Settle', digits=(15,2), compute='set_amount_to_settle', store=True)
    settled               = fields.Boolean(string='Move Settled')      
    #flag_pending_process  = fields.Boolean(string='Pending Process', compute='set_flag_pending_process')    
    advance_id        = fields.Many2one('wobin.advances')
    comprobation_id   = fields.Many2one('wobin.comprobations')
    settlement_id     = fields.Many2one('wobin.settlements')
    settlement_aux_id = fields.Many2one('wobin.settlements', string='Settlement')
    settlements_ids   = fields.One2many('wobin.settlements', 'mov_lns_ad_set_id', compute='set_settlements_ids', store=True)    
    total_settlement  = fields.Float(string='Total of Settlement $', digits=(15,2), compute='set_total_settlement', store=True)
    state             = fields.Selection(selection = [('pending', 'Pending'),
                                                      ('ready', 'Ready to settle'),
                                                      ('settled', 'Settled'),
                                                     ], string='State', readonly=True, copy=False, tracking=True, default='pending', compute='set_state_settlement', store=True)        
    company_id = fields.Many2one('res.company', default=lambda self: self.env['res.company']._company_default_get('wobin_ant_liq'))

    #@api.one
    #def set_settler(self):
    #    settlement_recordsets = self.env['wobin.settlements'].search([('operator_id', '=', self.operator_id.id)])


    
    #@api.one
    @api.depends('settlement_aux_id')
    def set_total_settlement(self):
        for rec in self:
            rec.total_settlement = rec.settlement_aux_id.total_settlement


    
    #@api.one
    @api.depends('settlement_aux_id')
    def set_state_settlement(self):
        for rec in self:
            rec.state = rec.settlement_aux_id.state



    #@api.one
    @api.depends('settlement_aux_id')
    def set_settlements_ids(self):
        for rec in self:
            list_settlements = self.env['wobin.settlements'].search([('id', '=', rec.settlement_aux_id.id)]).ids 
            rec.settlements_ids = [(6, 0, list_settlements)]



    @api.depends('advances_ids')
    def _set_advances_sum_amount(self):
        for rec in self:
            sum_amount = sum(line.amount for line in rec.advances_ids)
            rec.advances_sum_amount = sum_amount  
            rec.update({'advances_sum_amount': sum_amount})                   



    @api.depends('comprobations_ids')
    def _set_comprobations_sum_amount(self):     
        for rec in self: 
            sum_amount = sum(line.amount for line in rec.comprobations_ids)
            rec.comprobations_sum_amount = sum_amount
            self.write({'comprobations_sum_amount': sum_amount})            
              


    """
    @api.model 
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(WobinMovesAdvSetLines, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'advances_sum_amount' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_due = 0.0
                    for record in lines:
                        if not record.settlement_aux_id:
                            total_due += record.advances_sum_amount
                    line['advances_sum_amount'] = total_due        
        if 'comprobations_sum_amount' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_due = 0.0
                    for record in lines:
                        total_due += record.comprobations_sum_amount
                    line['comprobations_sum_amount'] = total_due
        if 'amount_to_settle' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_due = 0.0
                    for record in lines:
                        total_due += record.amount_to_settle
                    line['amount_to_settle'] = total_due                    
        return res
    """
                
    

    #@api.one    
    @api.depends('advances_sum_amount', 'comprobations_sum_amount')
    def set_amount_to_settle(self):
        for rec in self:
            if rec.settled: 
                rec.amount_to_settle = None                      
            else:
                rec.amount_to_settle = self.comprobations_sum_amount - self.advances_sum_amount