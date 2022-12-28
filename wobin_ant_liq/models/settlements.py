# -*- coding: utf-8 -*-
from odoo import models, fields, api


class WobinSettlements(models.Model):
    _name = 'wobin.settlements'
    _description = 'Wobin Liquidaciones'
    _inherit = ['mail.thread', 'mail.activity.mixin']     


    @api.model
    def create(self, vals):  
        """This method intends to create a sequence for a given settlement"""
        #Change of sequence (if it isn't stored is shown "New" else e.g LIQ000005)  
        if vals.get('name', 'New') == 'New':
            sequence = self.env['ir.sequence'].next_by_code('self.settlement') or 'New'
            vals['name'] = sequence                      
        return super(WobinSettlements, self).create(vals)



    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                     FIELDS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    name        = fields.Char(string="Liquidación", 
                              readonly=True, 
                              required=True, 
                              copy=False, 
                              default='New', 
                              track_visibility='always')
    operator_id = fields.Many2one('res.partner',
                                  string='Operador', 
                                  track_visibility='always', 
                                  ondelete='cascade')
    date        = fields.Date(string='Fecha', 
                              track_visibility='always')
    attachments = fields.Many2many('ir.attachment', 
                                   relation='settlements_attachment', 
                                   string='Adjuntos', 
                                   track_visibility='always')
    possible_adv_set_lines_ids = fields.One2many('wobin.moves.adv.set.lines', 'settlement_id', 
                                                 string='Posibles Movimientos por Operador')
    settled_adv_set_lines_ids  = fields.One2many('wobin.moves.adv.set.lines', 'settlement_aux_id', 
                                                 string='Movimientos Saldados por Operador', 
                                                 compute='_set_settled_lines', 
                                                 store=True)
    total_selected   = fields.Float(string='Total de Saldos Seleccionados $', 
                                    digits=(15,2))
    total_settlement = fields.Float(string='Total de Liquidación', 
                                    digits=(15,2))
    amount_to_settle = fields.Float(string='Saldo a Liquidar $', 
                                    digits=(15,2))
    state            = fields.Selection(selection = [('pending', 'Pendiente'),
                                                     ('ready', 'Preparado para saldar'),
                                                     ('settled', 'Saldado')], 
                                        string='Estado', 
                                        required=True, 
                                        readonly=True, 
                                        copy=False, 
                                        tracking=True, 
                                        default='pending', 
                                        track_visibility='always')    
    #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    btn_crt_payment    = fields.Boolean(compute="_set_flag_button_create_payment", 
                                        store=True, 
                                        default=False)
    btn_mark_settle    = fields.Boolean(compute="_set_flag_button_mark_settle", 
                                        store=True, 
                                        default=False)
    btn_debtor_new_adv = fields.Boolean(compute="_set_flag_button_debtor_new_advance", 
                                        store=True, 
                                        default=False)
    label_process      = fields.Text(string='')
    payment_related_id = fields.Many2one('account.payment', 
                                         string='Pago Relacionado')    
    advance_related_id = fields.Many2one('wobin.advances', 
                                         string='Anticipo Relacionado')    
    mov_ad_set_lns_id  = fields.Many2one('wobin.moves.adv.set.lines')
    company_id         = fields.Many2one('res.company', 
                                         default=lambda self: self.env['res.company']._company_default_get('wobin_ant_liq'))



    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                    METHODS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    @api.onchange('operator_id')
    def _onchange_operator(self):
        #Fill up one2many field with data for current operator and a given trip:
        lines_gotten = self.env['wobin.moves.adv.set.lines'].search([('operator_id', '=', self.operator_id.id), 
                                                                     ('settled', '=', False)]).ids
        self.possible_adv_set_lines_ids = [(6, 0, lines_gotten)] 



    @api.onchange('possible_adv_set_lines_ids')
    def _onchange_posible_adv_set_lines(self):     
        # Only sum up lines which are selected by user:
        sum_amount = sum(line.amount_to_settle for line in self.possible_adv_set_lines_ids if line.check_selection == True)
        # Assign to total selected:
        self.total_selected = sum_amount  
        self.total_settlement = sum_amount
        self.amount_to_settle = sum_amount



    @api.depends('possible_adv_set_lines_ids')
    def _set_settled_lines(self):
        for rec in self:
            rec.settled_adv_set_lines_ids = [(6, 0, rec.possible_adv_set_lines_ids.filtered(lambda o: o.check_selection).ids)]                  



    @api.depends('total_selected')
    def _set_flag_button_create_payment(self):
        for rec in self:
            #When "amount to settle" is greater or lesser than 0 just display button for payments
            #through its respective flag and to aid in xml definition:
            if rec.total_selected > 0:
                rec.btn_crt_payment = True


    
    @api.depends('possible_adv_set_lines_ids', 'total_selected')
    def _set_flag_button_mark_settle(self):
        for rec in self:
            #When "amount to settle" is equal to 0 (and validating that
            # at least user has some rows selected) just display button to settle
            #through its respective flag and to aid in xml definition:
            flag = False
            
            for line in rec.possible_adv_set_lines_ids:
                if line.check_selection == True:
                    flag = True

            if rec.total_selected == 0 and flag ==True:           
                rec.btn_mark_settle = True



    @api.depends('total_selected')
    def _set_flag_button_debtor_new_advance(self):  
        for rec in self:        
            #When "amount to settle" is lesser than 0 just display button for acc. move or advances
            #through its respective flag and to aid in xml definition:        
            if rec.total_selected < 0:
                rec.btn_debtor_new_adv = True      



    def mark_settled(self):
        for rec in self:
            #Change state of this settlement:
            rec.state = 'settled'
            
            #Display into label this settlement was finished: 
            rec.label_process = 'Esta Liquidación ha sido saldada' 

            for line in rec.possible_adv_set_lines_ids:
                if line.check_selection == True:        
                    line.update({'settled': True})   



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
                line.write({'settled': True})

        self.amount_to_settle = None



    def create_payment(self):
        #Change state of settlement to "ready"
        self.state = 'ready'

        #This method intends to display a Form View of Payments:
        return {
            'name':"Creación de Pago",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',            
            'res_model': 'account.payment',
            'view_id': self.env.ref('account.view_account_payment_form').id,                        
            'target': 'new',
            'context': {
                        'default_payment_type': 'outbound',
                        'default_amount': self.total_selected,
                        'default_settlements_ids': [(4, self.id)], 
                        'default_ref': self.name,
                        'default_journal_id': 74,  #74 ID for Journal of "Caja y efectivo" in Transportes de Alba ['Sistema' Company]                    
                       }            
        } 



    def create_advance(self):   
        #Change state of settlement to "ready"
        self.state = 'ready'

        #This method intends to display a Form View of Advances:
        return {
            'name': "Creación de Anticipo",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'wobin.advances',
            'view_id': self.env.ref('wobin_ant_liq.view_advances_form').id,                        
            'target': 'new',
            'context': {
                        'default_operator_id': self.operator_id.id, 
                        'default_amount': abs(self.total_selected), 
                        'default_settlements_ids': [(4, self.id)], 
                        'default_money_not_consider': True
                       }
        }