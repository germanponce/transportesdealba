# -*- coding: utf-8 -*-
from odoo import models, fields, api


class WobinMovesAdvSetLines(models.Model):
    _name = 'wobin.moves.adv.set.lines'
    _description = 'Wobin Líneas de Movimientos de Anticipos y Liquidaciones'
    _inherit = ['mail.thread', 'mail.activity.mixin']     
                                                                

    check_selection = fields.Boolean(string=' ')
    operator_id     = fields.Many2one('res.partner',
                                      string='Operador', 
                                      ondelete='cascade')
    trip_id         = fields.Many2one('wobin.logistics.trips', 
                                      string='Trip', 
                                      ondelete='cascade')
    advances_ids             = fields.One2many('wobin.advances', 'mov_ad_set_lns_id', 
                                               string='Anticipos Relacionados', 
                                               ondelete='cascade')
    comprobations_ids        = fields.One2many('wobin.comprobations', 'mov_ad_set_lns_id', 
                                               string='Comprobaciones Relacionadas', 
                                               ondelete='cascade')
    advances_sum_amount      = fields.Float(string='Anticipos', 
                                            digits=(15,2), 
                                            compute='_set_advances_sum_amount', 
                                            store=True)
    comprobations_sum_amount = fields.Float(string='Comprobaciones', 
                                            digits=(15,2), 
                                            compute='_set_comprobations_sum_amount') 
                                            #store=True)
    amount_to_settle  = fields.Float(string='Saldo a Liquidar', 
                                     digits=(15,2), 
                                     compute='_set_amount_to_settle', 
                                     store=True)
    settled           = fields.Boolean(string='Mov. Saldado')         
    settlement_id     = fields.Many2one('wobin.settlements',#Many2one field for 'possible_adv_set_lines_ids' One2many field in Settlements
                                        ondelete='cascade')
    settlement_aux_id = fields.Many2one('wobin.settlements',#Many2one field for 'settled_adv_set_lines_ids' One2many field in Settlements 
                                        string='Liquidación',
                                        ondelete='cascade')   
    total_settlement  = fields.Float(string='Total de Liquidación', 
                                     digits=(15,2), 
                                     compute='_set_total_settlement', 
                                     store=True)
    state_settlement  = fields.Selection(selection = [('pending', 'Pendiente'),
                                                      ('ready', 'Preparado para saldar'),
                                                      ('settled', 'Saldado')], 
                                         string='Estado', 
                                         readonly=True, 
                                         copy=False, 
                                         tracking=True, 
                                         default='pending', 
                                         related='settlement_aux_id.state', 
                                         store=True)  
    company_id        = fields.Many2one('res.company', 
                                        default=lambda self: self.env['res.company']._company_default_get('wobin_ant_liq'))



    @api.depends('advances_ids')
    def _set_advances_sum_amount(self):
        for rec in self:
            sum_amount = sum(line.amount for line in rec.advances_ids)
            rec.advances_sum_amount = sum_amount  
            #rec.update({'advances_sum_amount': sum_amount})                   


    
    #@api.depends('comprobations_ids')
    def _set_comprobations_sum_amount(self):     
        for rec in self: 
            sum_amount = sum(line.amount for line in rec.comprobations_ids)
            rec.comprobations_sum_amount = sum_amount
            #rec.write({'comprobations_sum_amount': sum_amount})



    @api.depends('advances_sum_amount', 'comprobations_sum_amount')
    def _set_amount_to_settle(self):
        for rec in self:
            if rec.settled: 
                rec.amount_to_settle = None                      
            else:
                rec.amount_to_settle = rec.comprobations_sum_amount - rec.advances_sum_amount



    @api.depends('settlement_aux_id')
    def _set_total_settlement(self):
        for rec in self:
            rec.total_settlement = rec.settlement_aux_id.total_settlement