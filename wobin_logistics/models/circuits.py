# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WobinLogisticsCircuits(models.Model):
    _name        = 'wobin.logistics.circuits'
    _description = 'Wobin Logística Circuitos'
    _order       = 'name desc'
    _inherit     = ['mail.thread', 'mail.activity.mixin']
    

    #@api.model
    #def create(self, vals):                        
    #    #Creation of sequence (if it isn't stored is shown "New" else e.g CRCT000005)  
    #    if vals.get('name', 'New') == 'New':
    #        vals['name'] = self.env['ir.sequence'].next_by_code('self.circuit') or 'New'               
    #    return super(WobinLogisticsCircuits, self).create(vals)  


    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                     FIELDS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    name        = fields.Char(string="Circuito", 
                              readonly=True, 
                              required=True, 
                              copy=False, 
                              #default='New',
                              track_visibility='always')   
    unit_id     = fields.Many2one('wobin.logistics.vehicles',
                                  string='Unidad', 
                                  required=True,
                                  track_visibility='always')
    operator_id = fields.Many2one('res.partner', 
                                  string='Operador', 
                                  required=True,
                                  track_visibility='always')
    start_date  = fields.Date(string='Fecha inicio circuito',
                              track_visibility='always')
    end_date    = fields.Date(string='Fecha fin circuito',
                              track_visibility='always')
    trips_count   = fields.Integer(compute='_compute_trips_count')    
    state_circuit = fields.Selection([('activo', 'Activo'),
                                      ('cerrado', 'Cerrado')
                                     ], string='Estado', 
                                        default='activo',                                        
                                        compute='_compute_state_circuit',
                                        store=True,
                                        track_visibility='always')



    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                    METHODS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    def _compute_trips_count(self):
        for record in self:
            record.trips_count = self.env['wobin.logistics.trips'].search_count([('circuit_id', '=', self.id)])



    @api.depends('start_date', 'end_date')
    def _compute_state_circuit(self):
        for record in self:
            if record.start_date and not record.end_date:
                record.state_circuit = 'activo'
            elif record.end_date:
                record.state_circuit = 'cerrado'    



    def create_trip(self):
        """This method displays a Form View of Trips"""         
        return {
            'name': "Creación de Viaje",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',                                
            'res_model': 'wobin.logistics.trips',
            'view_id': self.env.ref('wobin_logistics.view_logistics_trips_form').id,
            'target': 'new',
            'context': {'default_circuit_id': self.id}
        }
    


    def get_trips(self):
        self.ensure_one()
        return {
            'name': 'Viajes',
            'type': 'ir.actions.act_window',            
            'view_mode': 'tree',
            'res_model': 'wobin.logistics.trips',
            'view_id': self.env.ref('wobin_logistics.view_logistics_trips_list').id,
            'domain': [('circuit_id', '=', self.id)],
            'context': "{'create': False}"
        }