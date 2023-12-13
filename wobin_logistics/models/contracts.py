# -*- coding: utf-8 -*-
from odoo import models, fields, api


class WobinLogisticsContracts(models.Model):
    _name = 'wobin.logistics.contracts'
    _description = 'Wobin Logística Contractos'
    _inherit     = ['mail.thread', 'mail.activity.mixin']   


    @api.model
    def create(self, vals):                        
        #Creation of sequence (if it isn't stored is shown "New" else e.g CONTR000005)  
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('self.contract') or 'New'               
        return super(WobinLogisticsContracts, self).create(vals)  



    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                     FIELDS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    name            = fields.Char(string="Contrato", 
                                  readonly=True, 
                                  required=True, 
                                  copy=False, 
                                  default='New',
                                  track_visibility='always')
    company_id      = fields.Many2one('res.company', 
                                      default=lambda self: self.env['res.company']._company_default_get('wobin_logistics'))                                  
    client_id       = fields.Many2one('res.partner', 
                                      string='Cliente',
                                      track_visibility='always')
    product_id      = fields.Many2one('product.product', 
                                      string='Producto', 
                                      track_visibility='always')
    covenant_qty    = fields.Float(string='Cantidad Pactada (kg)',
                                   track_visibility='always')
    tariff          = fields.Float(string='Tarifa $', 
                                   track_visibility='always')
    expected_income = fields.Float(string='Ingreso Esperado $', 
                                   readonly=True, 
                                   compute='_set_expected_income',
                                   store=True,
                                   track_visibility='always')
    origin_id       = fields.Many2one('wobin.logistics.routes', 
                                      string='Origen',
                                      track_visibility='always')
    destination_id  = fields.Many2one('wobin.logistics.routes', 
                                      string='Destino',
                                      track_visibility='always')
    remitter        = fields.Char(string='Remitente',
                                  track_visibility='always')
    recipient       = fields.Char(string='Destinatario',
                                  track_visibility='always')
    shipping        = fields.Char(string='Envío',
                                  track_visibility='always')
    observations    = fields.Html('Observaciones',
                                  track_visibility='always')
    state           = fields.Selection(selection=[('active', 'Activo'),
                                                  ('close', 'Cerrado')], 
                                       string='Estado', 
                                       required=True, 
                                       readonly=True, 
                                       copy=False, 
                                       default='active', 
                                       track_visibility='always') 

    #|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|
    # FIELDS FOR ANALYSIS AND REPORTS OF CONTRACTS
    #|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|
    trips_ids          = fields.One2many('wobin.logistics.trips', 
                                         'contract_id', 
                                         string='Viajes') 
    trip_delivered_qty = fields.Float(string='Cant. Entregada', 
                                      compute='_set_trip_delivered_qty',
                                      store=True)
    difference_qty     = fields.Float(string='Cant. Restante', 
                                      compute='_set_dif_qty',
                                      store=True)
    trip_status        = fields.Selection([('to_do', 'Por Comenzar'),
                                           ('doing', 'En Curso'),
                                           ('done', 'Terminado')], 
                                          string='Status de Surtimiento del Contrato', 
                                          index=True, 
                                          readonly=True, 
                                          default='to_do', 
                                          copy=False, 
                                          compute='_set_trip_status',
                                          store=True)    


    
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                    METHODS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°    
    @api.depends('covenant_qty', 'tariff')
    def _set_expected_income(self):
        for rec in self:
            rec.expected_income = self.covenant_qty * self.tariff



    @api.depends('trips_ids')
    def _set_trip_delivered_qty(self):
        '''This method intends to sum all discharges of multiple 
           trips assigned to a given contract'''
        for rec in self:
            if rec.trips_ids:
                rec.trip_delivered_qty = sum(trip.real_load_qty for trip in rec.trips_ids)        



    @api.depends('covenant_qty', 'trip_delivered_qty')
    def _set_dif_qty(self):
        '''This method intends to show the difference between delivered_qty 
           and discharged_qty assigned to a trip'''
        for rec in self:           
            rec.difference_qty = rec.covenant_qty - rec.trip_delivered_qty



    @api.depends('trips_ids')
    def _set_trip_status(self):
        '''This method intends to show the status of related trips to this 
           contract in order to determine if covenant_qty has already been
           delivered by the trips or if still lacks product to deliver'''        
        sum_trips_covenant_qty = 0.0
        for rec in self:
            if not rec.trips_ids:
                rec.trip_status = 'to_do'
            else: 
                sum_trips_covenant_qty = sum(trip.real_discharge_qty for trip in rec.trips_ids) 

                if sum_trips_covenant_qty == rec.covenant_qty:
                    rec.trip_status = 'done'
                else:
                    rec.trip_status = 'doing'



    def close_contract(self):
        """This method sets state "close" for the contract"""
        for rec in self:
            rec.state = 'close'



    #def create_trip(self):
    #    """This method displays a Form View of Trips"""         
    #    return {
    #        'name': "Creación de Viaje",
    #        'type': 'ir.actions.act_window',
    #        'view_type': 'form',
    #        'view_mode': 'form',                                
    #        'res_model': 'wobin.logistics.trips',
    #        'view_id': self.env.ref('wobin_logistics.view_logistics_trips_form').id,
    #        'target': 'new',
    #        'context': {'default_contract_id': self.id}
    #    }