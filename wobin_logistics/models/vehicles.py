# -*- coding: utf-8 -*-
from odoo import models, fields, api


class WobinLogisticsVehicles(models.Model):
    _name = 'wobin.logistics.vehicles'
    _description = 'Wobin Logística Vehículos'
    _inherit     = ['mail.thread', 'mail.activity.mixin']  


    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                     FIELDS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    name                = fields.Char(track_visibility='always')
    company_id          = fields.Many2one('res.company', 
                                          default=lambda self: self.env['res.company']._company_default_get('wobin_logistics'))    
    mark                = fields.Char(string='Marca', 
                                      track_visibility='always')
    model               = fields.Char(string='Modelo', 
                                      track_visibility='always')
    year                = fields.Char(string='Año', 
                                      track_visibility='always')
    description         = fields.Char(string='Descripción', 
                                      track_visibility='always')
    series              = fields.Char(string='Serie', 
                                      track_visibility='always')
    license_plate       = fields.Char(string='Placa', 
                                      track_visibility='always') 
    current_trip        = fields.Many2one('wobin.logistics.trips', 
                                          string='Viaje Actual', 
                                          compute="_set_current_trip", 
                                          store=True, 
                                          track_visibility='always')
    analytic_account_id = fields.Many2one('account.analytic.account', 
                                          string='Cuenta Analítica', 
                                          track_visibility='always')
    trips_history       = fields.One2many('wobin.logistics.trips', 'vehicle_id', 
                                          string='Historial de Viajes', 
                                          track_visibility='always')
    state               = fields.Selection(selection=[('in_use', 'En Uso'), 
                                                      ('without_charge', 'Sin Carga')], 
                                           string='Estado', 
                                           required=True, 
                                           readonly=True, 
                                           copy=False, 
                                           default='without_charge', 
                                           compute="_set_state", 
                                           store= True, 
                                           track_visibility='always')


      
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                    METHODS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    @api.depends('trips_history')
    def _set_current_trip(self):  
        for rec in self:      
            trip = self.env['wobin.logistics.trips'].search([('vehicle_id', '=', rec.id)], 
                                                            order='create_date desc',
                                                            limit=1)
            if trip:   
                if trip.state != 'discharged': 
                    rec.current_trip = trip.id
                else:                
                    rec.current_trip = None                                                              



    @api.depends('current_trip')
    def _set_state(self):
        for rec in self:
            if rec.current_trip:
                rec.state = 'in_use'
            else:
                rec.state = 'without_charge'