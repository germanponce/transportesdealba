# -*- coding: utf-8 -*-
from odoo import models, fields, api


class WobinAdvances(models.Model):
    _name = 'wobin.advances'
    _description = 'Wobin Anticipos'
    _inherit = ['mail.thread', 'mail.activity.mixin']      


    @api.model
    def create(self, vals):  
        """This method intends to create a sequence for a given advance"""            
        #Change of sequence (if it isn't stored is shown "New" else e.g ANT000005) 
        if vals.get('name', 'New') == 'New':
            sequence = self.env['ir.sequence'].next_by_code('self.advance') or 'New'
            vals['name'] = sequence             
          
            #Update flag to indicate employee for checking up:
            employee_obj = self.env['res.partner'].browse(vals['operator_id'])
            employee_obj.flag_employee_active = True

            res = super(WobinAdvances, self).create(vals)

            #After record was created successfully and if considering there is a new trip 
            #with new record for operator then create a new record for Wobin Moves Advances Settlements Lines 
            existing_move = self.env['wobin.moves.adv.set.lines'].search([('operator_id', '=', res.operator_id.id),
                                                                          ('trip_id', '=', res.trip_id.id)], limit=1)                                                                       
            if not existing_move:
                #Create a new record for Wobin Moves Advances Settlements Lines
                values = {
                          'operator_id': res.operator_id.id,
                          'trip_id': res.trip_id.id,
                          'advances_ids': [(4, res.id)]
                         }
                mov_ad_set_lns_obj = self.env['wobin.moves.adv.set.lines'].create(values)            
                vals['mov_ad_set_lns_id'] = mov_ad_set_lns_obj.id
            else:
                existing_move.advances_ids = [(4, res.id)]     

        return res



    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                     FIELDS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    name        = fields.Char(string="Anticipo", 
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
                               track_visibility='always')
    trip_id     = fields.Many2one('wobin.logistics.trips', 
                                  string='Viaje', 
                                  track_visibility='always', 
                                  ondelete='cascade')
    expenses_to_check      = fields.Float(string='Gastos Pendientes por Comprobar', 
                                          digits=(15,2), 
                                          compute='_set_expenses_to_check',
                                          track_visibility='always')
    payment_related_id     = fields.Many2one('account.payment', 
                                             string='Pago Relacionado',
                                             ondelete='set null',  
                                             track_visibility='always')
    mov_ad_set_lns_id      = fields.Many2one('wobin.moves.adv.set.lines',
                                             ondelete='cascade')
    settlements_ids        = fields.One2many('wobin.settlements', 'advance_related_id',
                                             string='Liquidación', 
                                             ondelete='cascade')
    money_not_consider     = fields.Boolean(string='', default=False)
    company_id             = fields.Many2one('res.company', 
                                             default=lambda self: self.env['res.company']._company_default_get('wobin_ant_liq'))



    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                    METHODS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    def write(self, vals):
        #Override write method in order to detect fields changed:
        res = super(WobinAdvances, self).write(vals)  

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
                              'advances_ids': [(4, self.id)],
                             }
                    self.env['wobin.moves.adv.set.lines'].create(values)   
        return res                



    def _set_expenses_to_check(self):
        for rec in self:
            if rec.trip_id.id and rec.operator_id.id:
                #Sum amounts from the same trip by operator
                sql_query = """SELECT sum(amount) 
                                FROM wobin_advances 
                                WHERE trip_id = %s AND operator_id = %s"""
                self.env.cr.execute(sql_query, (rec.trip_id.id, rec.operator_id.id,))
                result = self.env.cr.fetchone()
                if result:                    
                    rec.expenses_to_check = result[0]



    def create_payment(self):
        """This method intends to display a Form View of Payments""" 
        return {
            'name':"Creación de Pago",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',            
            'res_model': 'account.payment',
            'view_id': self.env.ref('account.view_account_payment_form').id,
            'target': 'new',
            'context': {
                        'default_payment_type': 'outbound',
                        'default_amount': self.amount,
                        'default_advances_ids': [(4, self.id)],
                        'default_ref': self.name,
                        'default_journal_id': 74,  #74 ID for Journal of "Caja y efectivo" in Transportes de Alba ['Sistema' Company]                    
                       }
        }