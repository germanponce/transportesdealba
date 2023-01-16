# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class WobinComprobations(models.Model):
    _name = 'wobin.comprobations'
    _description = 'Wobin Comprobaciones'
    _inherit = ['mail.thread', 'mail.activity.mixin']     

    
    @api.model
    def create(self, vals):  
        """This method intends to create a sequence for a given comprobation"""
        #Change of sequence (if it isn't stored is shown "New" else e.g COMP000005)  
        if vals.get('name', 'New') == 'New':
            sequence = self.env['ir.sequence'].next_by_code('self.comprobation') or 'New'
            vals['name'] = sequence    

        res = super(WobinComprobations, self).create(vals)  
            
        #After record was created successfully and if considering there is a new trip 
        #with new record for operator then create a new record for Wobin Moves Advances Settlements Lines 
        existing_move = self.env['wobin.moves.adv.set.lines'].search([('operator_id', '=', res.operator_id.id),
                                                                      ('trip_id', '=', res.trip_id.id)], limit=1)                                                                       
        if not existing_move:
            #Create a new record for Wobin Moves Advances Settlements Lines
            values = {
                      'operator_id': res.operator_id.id,
                      'trip_id': res.trip_id.id,
                      'comprobations_ids': [(4, res.id)]
                     }
            mov_ad_set_lns_obj = self.env['wobin.moves.adv.set.lines'].create(values)            
            vals['mov_ad_set_lns_id'] = mov_ad_set_lns_obj.id  
        else:
            existing_move.comprobations_ids = [(4, res.id)]                                                                                                     

        return res



    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                     FIELDS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    name        = fields.Char(string="Comprobación", 
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
    amount      = fields.Float(string='Monto $', 
                               digits=(15,2), 
                               compute='_set_amount_total',
                               store=True,
                               track_visibility='always')
    total       = fields.Float(string='Total $', 
                               digits=(15,2),
                               compute='_set_amount_total',
                               store=True,
                               track_visibility='always')
    trip_id     = fields.Many2one('wobin.logistics.trips', 
                                  string='Viaje', 
                                  track_visibility='always', 
                                  ondelete='cascade')
    expenses_to_refund = fields.Float(string='Gastos Pendientes por Reembolsar', 
                                      digits=(15,2), 
                                      compute='_set_expenses_to_refund', 
                                      track_visibility='always')
    acc_mov_related_id = fields.Many2one('account.move', 
                                         string='Movimiento Contable Relacionado', 
                                         ondelete='cascade', 
                                         track_visibility='always')
    mov_ad_set_lns_id  = fields.Many2one('wobin.moves.adv.set.lines', 
                                         ondelete='cascade')
    comprobation_lines_ids = fields.One2many('wobin.comprobation.lines', 'comprobation_id', 
                                             string='Líneas de Concepto')   
    state      = fields.Selection([('draft', 'Borrador'),
                                   ('checked', 'Comprobado'),                                     
                                   ('cancelled', 'Cancelado')], 
                                  string='Estado', 
                                  default='draft', 
                                  compute='_set_checked_state', 
                                  store=True,                                   
                                  track_visibility='always')   
    company_id = fields.Many2one('res.company', 
                                 default=lambda self: self.env['res.company']._company_default_get('wobin_ant_liq'))                                     



    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                    METHODS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    def write(self, vals):
        #Override write method in order to detect fields changed:
        res = super(WobinComprobations, self).write(vals)  

        self.ensure_one()
        
        #If in fields changed are operator_id and trip_id update 
        #that data in its respective wobin.moves.adv.set.lines rows:
        if vals.get('operator_id', False):
            mov_lns_obj = self.env['wobin.moves.adv.set.lines'].browse(self.mov_ad_set_lns_id.id)
            
            if mov_lns_obj:
                mov_lns_obj.operator_id = vals['operator_id']

        if vals.get('trip_id', False):
            mov_lns_obj = self.env['wobin.moves.adv.set.lines'].browse(self.mov_ad_set_lns_id.id)
            
            if mov_lns_obj:
                mov_lns_obj.trip_id = vals['trip_id'] 

                sql_query = """SELECT count(*) 
                               FROM wobin_moves_adv_set_lines
                               WHERE operator_id = %s AND trip_id = %s"""
                self.env.cr.execute(sql_query, (self.operator_id.id, self.trip_id.id,))
                result = self.env.cr.fetchone()
                if result:                   
                    if result[0] > 1:
                        self.env['wobin.moves.adv.set.lines'].browse(self.mov_ad_set_lns_id.id).unlink()            
            else:                
                #Considering there is a new trip with new record for operator 
                #then create a new record for Wobin Moves Advances Settlements Lines 
                existing_movs = self.env['wobin.moves.adv.set.lines'].search([('operator_id', '=', self.operator_id.id),
                                                                              ('trip_id', '=', self.trip_id.id)]).ids                                                                       
                if not existing_movs:
                    #Create a new record for Wobin Moves Advances Settlements Lines
                    values = {
                              'operator_id': self.operator_id.id,
                              'trip_id': self.trip_id.id,
                              'comprobations_ids': [(4, self.id)],
                             }
                    self.env['wobin.moves.adv.set.lines'].create(values)                                  
        return res  



    @api.onchange('comprobation_lines_ids')
    def _onchange_comprobation_lines_ids(self):        
        # Only sum up lines which are not credit concepts:
        sum_amount = sum(line.amount for line in self.comprobation_lines_ids if line.concept_id.credit_flag != True)
        # Assign to amount and total:
        self.amount = sum_amount        
        self.total = sum_amount
        #Sum all amounts of debit concepts and fill up authomatically
        #amount if concept to input is credit:
        for line in self.comprobation_lines_ids: 
            if line.concept_id.credit_flag == True: 
                line.amount = sum_amount  



    @api.depends('comprobation_lines_ids')      
    def _set_amount_total(self):
        # Only sum up lines which are not credit concepts:
        sum_amount = sum(line.amount for line in self.comprobation_lines_ids if line.concept_id.credit_flag != True)
        # Assign to amount and total:
        self.amount = sum_amount        
        self.total = sum_amount   



    def _set_expenses_to_refund(self):
        for rec in self:
            #Sum amounts from the same trip by operator
            sql_query = """SELECT SUM(amount) 
                            FROM wobin_comprobations 
                            WHERE trip_id = %s AND operator_id = %s;"""
            self.env.cr.execute(sql_query, (rec.trip_id.id, rec.operator_id.id,))
            result = self.env.cr.fetchone()

            if result:                    
                rec.expenses_to_refund = result[0] 



    @api.depends('acc_mov_related_id')
    def _set_checked_state(self):
        for rec in self:
            if rec.acc_mov_related_id:            
                #Change state to "checked" in order to make disappear 
                #button "Create Comprobation Entry"
                self.write({'state': 'checked'})                         
                
                
                
    def cancelar_comprobacion(self):
        for rec in self:
            #Validate if there is no Accounting Moves related else Cancel Comprobation:
            if rec.acc_mov_related_id:
                msg =  "No se puede cancelar esta Comprobación "
                msg += rec.name
                msg += "\nDebido a que posee un Movimiento Contable ya relacionado con ella."
                msg += "\n\nPor favor, primero Cancelar y Suprimir este Asiento Contable: "
                msg += rec.acc_mov_related_id.name
                raise UserError(msg)
            else:            
                rec.state = 'cancelled'                 


       
    def create_account_move(self):
        #This method intends to display a Form View of Account Move        
        line_ids_list    = list()
        item             = tuple()
        dictionary_vals  = dict()

        #°°°°°°°°°°°°°°°°°°°°°°°°°°°
        # Creation of Account Move |
        #°°°°°°°°°°°°°°°°°°°°°°°°°°°          
        account_move = {
                'trips_acc_move_ids': [(4, self.trip_id.id)],
                'comprobations_ids': [(4, self.id)],
                'ref': self.name,                
                'journal_id': 86,  #86 ID for Journal of "Contabilidad B" in Transportes de Alba ['Sistema' Company]             
               } 
        acc_mov_obj = self.env['account.move'].create(account_move )        
        # | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
        # Subprocess:
        # Consult different models in order to fill up by default some fields in 
        # pop up window of account move lines
        
        #   For Debit Lines
        for line in self.comprobation_lines_ids:  
            credit = 0.00; debit = 0.00           
            account_id          = line.concept_id.account_account_id.id
            enterprise_id       = self.operator_id.enterprise_id.id
            name                = line.concept_id.name + '|' + self.trip_id.analytic_account_id.name + '|' + self.trip_id.name
            analytic_account_id = self.trip_id.analytic_account_id.id
            analytic_tag_ids    = self.env['account.analytic.tag'].search([('name', '=', self.trip_id.name)], limit=1).ids          
            
            # Determine concepts set like credit:
            credit_flag = line.concept_id.credit_flag
            if credit_flag == True:
                credit = line.amount
            else:
                debit = line.amount            
            
            # Dictionary of account move line to be created:
            dictionary_vals = {
                'move_id': acc_mov_obj.id,
                'account_id': account_id,
                'partner_id': enterprise_id, 
                'name': name,                
                'analytic_account_id': analytic_account_id,
                'analytic_tag_ids': analytic_tag_ids,
                'debit': debit,
                'credit': credit
            }
            # Append debit & credit info into the list which it will be used later
            # in creation of account move lines:
            line_ids_list.append(dictionary_vals)        

        # Creation of account move lines:
        self.env['account.move.line'].create(line_ids_list)

        #°°°°°°°°°°°°°°°°°°°°°°
        # Account Move Pop Up |
        #°°°°°°°°°°°°°°°°°°°°°°           
        return {
            'name': "Creación de Asiento de Diario",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': acc_mov_obj.id, #Account Move Previously Created
            'view_id': self.env.ref('account.view_move_form').id,                        
            'target': 'new'
        }  





class WobinComprobationLines(models.Model):
    _name = 'wobin.comprobation.lines'
    _description = 'Wobin Comprobation Lines'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 


    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                     FIELDS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    comprobation_id = fields.Many2one('wobin.comprobations', 
                                      string='Referencia de Comprobación', 
                                      required=True, 
                                      ondelete='cascade', 
                                      index=True)
    concept_id      = fields.Many2one('wobin.concepts', 
                                      string='Concepto', 
                                      track_visibility='always')
    amount          = fields.Float(string='Monto $', 
                                   digits=(15,2), 
                                   track_visibility='always')
    credit_flag     = fields.Boolean(string='Concepto como Crédito/Haber', 
                                     compute='_set_flag', 
                                     store=True)
    company_id      = fields.Many2one('res.company', 
                                      default=lambda self: self.env['res.company']._company_default_get('wobin_ant_liq'))



    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                    METHODS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    def _set_flag(self):
        for rec in self:
            rec.credit_flag = self.env['wobin.concepts'].search([('id', '=', rec.concept_id.id)], limit=1).credit_flag