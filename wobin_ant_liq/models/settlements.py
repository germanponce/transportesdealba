# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api


class WobinConcepts(models.Model):
    _name = 'wobin.concepts'
    _description = 'Wobin Concepts'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 

    name = fields.Char(string='Concept', track_visibility='always')
    account_account_id = fields.Many2one('account.account', string='Accounting Account', track_visibility='always', ondelete='cascade')
    credit_flag = fields.Boolean(string='Concept Set Like Credit')
    company_id = fields.Many2one('res.company', default=lambda self: self.env['res.company']._company_default_get('your.module'))



class WobinSettlements(models.Model):
    _name = 'wobin.settlements'
    _description = 'Wobin Settlements'
    _inherit = ['mail.thread', 'mail.activity.mixin']     


    @api.model
    def create(self, vals):  
        """This method intends to create a sequence for a given settlement"""
        #Change of sequence (if it isn't stored is shown "New" else e.g LIQ000005)  
        if vals.get('name', 'New') == 'New':
            sequence = self.env['ir.sequence'].next_by_code(
                'self.settlement') or 'New'
            vals['name'] = sequence                      
        return super(WobinSettlements, self).create(vals)



    name        = fields.Char(string="Settlement", readonly=True, required=True, copy=False, default='New', track_visibility='always')
    operator_id = fields.Many2one('res.partner',string='Operator', track_visibility='always', ondelete='cascade')
    date        = fields.Date(string='Date', track_visibility='always')
    attachments = fields.Many2many('ir.attachment', relation='settlements_attachment', string='Attachments', track_visibility='always')
    possible_adv_set_lines_ids = fields.One2many('wobin.moves.adv.set.lines', 'settlement_id', string='Possible Moves for operator')
    settled_adv_set_lines_ids  = fields.One2many('wobin.moves.adv.set.lines', 'settlement_aux_id', string='Settled Moves for operator', compute='_set_settled_lines', store=True)
    total_selected   = fields.Float(string='Total of Selected Rows $', digits=(15,2))
    total_settlement = fields.Float(string='Total of Settlement $', digits=(15,2))
    amount_to_settle = fields.Float(string='Amount to Settle $', digits=(15,2))
    state            = fields.Selection(selection = [('pending', 'Pending'),
                                                     ('ready', 'Ready to settle'),
                                                     ('settled', 'Settled'),
                                                ], string='State', required=True, readonly=True, copy=False, tracking=True, default='pending', track_visibility='always')    
    # Fields for analysis:
    advances_sum_amount   = fields.Float(string='Advances', digits=(15,2))
    comprobation_sum = fields.Float(string='Comprobations', digits=(15,2))
    btn_crt_payment    = fields.Boolean(compute="set_flag_btn_crt_payment", store=True, default=False)
    btn_mark_settle    = fields.Boolean(compute="set_flag_btn_mark_settle", store=True, default=False)
    btn_debtor_new_adv = fields.Boolean(compute="set_flag_btn_debtor_new_a", store=True, default=False)
    label_process      = fields.Text(string='')
    payment_related_id = fields.Many2one('account.payment', string='Related Payment', compute='set_related_payment', store=True)    
    advance_related_id = fields.Many2one('wobin.advances', string='Related Advance', compute='set_related_advance', store=True)    
    trips_related_ids  = fields.Many2many('wobin.logistics.trips')
    mov_lns_ad_set_id  = fields.Many2one('wobin.moves.adv.set.lines')
    company_id = fields.Many2one('res.company', default=lambda self: self.env['res.company']._company_default_get('wobin_ant_liq'))


    @api.onchange('operator_id')
    def onchange_adv_set_lines_ids(self):
        #Fill up one2many field with data for current operator and a given trip:
        ids_gotten = self.env['wobin.moves.adv.set.lines'].search([('operator_id', '=', self.operator_id.id), ('settled', '=', False)]).ids
        self.possible_adv_set_lines_ids = [(6, 0, ids_gotten)]                   



    @api.onchange('possible_adv_set_lines_ids')
    def _onchange_comprobation_lines_ids(self):     
        # Only sum up lines which are selected by user:
        sum_amount = sum(line.amount_to_settle for line in self.possible_adv_set_lines_ids if line.check_selection == True)
        # Assign to total selected:
        self.total_selected = sum_amount  
        self.total_settlement = sum_amount
        self.amount_to_settle = sum_amount

        sum_advances = sum(line.advances_sum_amount for line in self.possible_adv_set_lines_ids if line.check_selection == True)
        self.advances_sum_amount = sum_advances

        sum_comprobations = sum(line.comprobation_sum for line in self.possible_adv_set_lines_ids if line.check_selection == True)
        self.comprobation_sum = sum_comprobations

        list_trips = []
        for ln in self.possible_adv_set_lines_ids:
            if ln.check_selection == True:
                list_trips.append(ln.trip_id.id)
                         
        self.trips_related_ids = [(6, 0, list_trips)] 
        self.update({'trips_related_ids': [(6, 0, list_trips)]}) 

    
    
    #@api.one
    @api.depends('possible_adv_set_lines_ids')
    def _set_settled_lines(self):
        for rec in self:
            rec.settled_adv_set_lines_ids = [(6, 0, rec.possible_adv_set_lines_ids.filtered(lambda o: o.check_selection).ids)]                  



    #@api.one
    def set_flag_btn_crt_payment(self):
        for rec in self:
            #When "amount to settle" is greater or lesser than 0 just display button for payments
            #through its respectice flag and to aid in xml definition:
            if rec.total_selected > 0:
                rec.btn_crt_payment = True


    #@api.one
    def set_flag_btn_mark_settle(self):
        for rec in self:
            #When "amount to settle" is equal to 0 (and validating that
            # at least user has some rows selected) just display button to settle
            #through its respectice flag and to aid in xml definition:
            flag = False
            
            for line in rec.possible_adv_set_lines_ids:
                if line.check_selection == True:
                    flag = True

            if rec.total_selected == 0 and flag ==True:           
                rec.btn_mark_settle = True


    #@api.one
    def set_flag_btn_debtor_new_a(self):  
        for rec in self:        
            #When "amount to settle" is lesser than 0 just display button for acc. move or advances
            #through its respectice flag and to aid in xml definition:        
            if rec.total_selected < 0:
                rec.btn_debtor_new_adv = True    



    @api.onchange('total_selected')
    def reaction_to_selected_total(self):
        flag = False

        #When "amount to settle" is greater or lesser than 0 just display button for payments
        #through its respectice flag and to aid in xml definition:
        if self.total_selected > 0:
            self.btn_crt_payment = True   

        #When "amount to settle" is equal to 0 (and validating that
        # at least user has some rows selected) just display button to settle
        #through its respectice flag and to aid in xml definition:             
        for line in self.possible_adv_set_lines_ids:
            if line.check_selection == True:
                flag = True

        if self.total_selected == 0 and flag ==True:           
            self.btn_mark_settle = True  

        #When "amount to settle" is lesser than 0 just display button for acc. move or advances
        #through its respectice flag and to aid in xml definition:        
        if self.total_selected < 0:
            self.btn_debtor_new_adv = True  
                                     



    def create_payment(self):
        #This method intends to display a Form View of Payments:
        return {
            #'name':_(""),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.payment',
            #'res_id': p_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {'default_settlement_id': self.id}
        } 

    #@api.one
    def set_related_payment(self):
        for rec in self:
            #Retrieve related payment to this settlement:
            settlement_related = self.env['account.payment'].search([('settlement_id', '=', rec.id)], limit=1).id 
            if settlement_related:
                rec.payment_related_id = settlement_related 




    #@api.one
    def mark_settled(self):
        for rec in self:
            #Change state of this settlement:
            rec.state = 'settled'
            
            #Display into label this settlement was finished: 
            rec.label_process = 'Esta Liquidación ha sido saldada' 

            for line in rec.possible_adv_set_lines_ids:
                if line.check_selection == True:        
                    line.update({'settled': True})         



    
    def send_debtor(self):
        #This method intends to display a Form View of Account Moves:
        return {
            #'name':_(""),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.move',
            #'res_id': p_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {'default_settlement_id': self.id}
        } 

    #@api.one
    def set_related_acc_mov(self):
        for rec in self:
            #Retrieve related payment to this settlement:
            settlement_related = self.env['account.move'].search([('settlement_id', '=', rec.id)], limit=1).id 
            if settlement_related:
                rec.acc_mov_related_id = settlement_related              



    def create_advance(self):   
        #This method intends to display a Form View of Advances:
        return {
            #'name':_(""),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'wobin.advances',
            #'res_id': p_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {'default_settlement_id': self.id, 'default_money_not_consider': True}
        } 

    #@api.one
    def set_related_advance(self):
        for rec in self:
            #Retrieve related payment to this settlement:
            settlement_related = self.env['wobin.advances'].search([('settlement_id', '=', rec.id)], limit=1).id 
            if settlement_related:            
                rec.advance_related_id = settlement_related 
              


    def settle_operation(self):
        #Change state of this settlement if proccess is set up 
        #because already exists a payment, acc. move or advance related with this settlement:
        self.state = 'settled' 

        if self.payment_related_id:
            #Display into label this settlement was finished by a payment: 
            self.label_process = 'Esta Liquidación ha sido saldada por Pago ' + self.payment_related_id.name                                                    

        #if self.acc_mov_related_id:
            #Display into label this settlement was finished by an account move: 
            #self.label_process = 'Esta Liquidación ha sido saldada por Movimiento Contable ' + self.acc_mov_related_id.name                              

        if self.advance_related_id:
            #Display into label this settlement was finished by an advance: 
            self.label_process = 'Esta Liquidación ha sido saldada por Anticipo ' + self.advance_related_id.name 
        
        for line in self.settled_adv_set_lines_ids:
            if line.check_selection == True:
                line.settled = True         
        
        for line in self.possible_adv_set_lines_ids:
            if line.check_selection == True:
                line.update({'settled': True})    
                line.write({'settled': True})

        self.amount_to_settle = None