# -*- coding: utf-8 -*-
from odoo import models, fields, api


class WobinLogisticsTrips(models.Model):
    _name        = 'wobin.logistics.trips'
    _description = 'Wobin Logística Viajes'
    _order       = 'name desc'
    _inherit     = ['mail.thread', 'mail.activity.mixin']        


    @api.model
    def create(self, vals):  
        """This method intends to create a sequence for a trip and a new analytic tag"""
        #Creation of sequence (if it isn't stored is shown "New" else e.g VJ000005)  
        if vals.get('name', 'New') == 'New':
            #Get sequence and assign it to trip's name:
            sequence = self.env['ir.sequence'].next_by_code('self.trip') or 'New'
            vals['name'] = sequence
            #At the same time, a new analytic account is created for this trip (name is 
            #equal to trip's sequence, type must be "trip"):           
            values = {
                    'name': sequence,
                    'analytic_tag_type': 'trip'
                }
            tag_obj = self.env['account.analytic.tag'].create(values)  
            #Assign ID of new analytic tag to trip's field "trip_number_tag":
            vals['trip_number_tag'] = tag_obj.id                    
        return super(WobinLogisticsTrips, self).create(vals)



    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                     FIELDS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°    
    #|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|
    # FIELDS FOR GENERAL DATA OF TRIPS
    #|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|
    name                = fields.Char(string="Viaje", 
                                      readonly=True, 
                                      required=True, 
                                      default='New', 
                                      track_visibility='always')
    company_id          = fields.Many2one('res.company', 
                                          default=lambda self: self.env['res.company']._company_default_get('wobin_logistics'))                                      
    trip_number_tag     = fields.Many2one('account.analytic.tag', 
                                          string='Número de Viaje (Etiqueta Analítica)', 
                                          track_visibility='always')                                    
    contract_id         = fields.Many2one('wobin.logistics.contracts', 
                                          string='Contratos', 
                                          domain=[('state', '=', 'active')], 
                                          ondelete='set null',                                         
                                          track_visibility='always')
    sucursal_id         = fields.Many2one('stock.warehouse', 
                                          string='Sucursal', 
                                          track_visibility='always')
    client_id           = fields.Many2one('res.partner', 
                                          string='Cliente', 
                                          track_visibility='always')
    vehicle_id          = fields.Many2one('wobin.logistics.vehicles', 
                                          string='Vehículo', 
                                          track_visibility='always')     
    analytic_account_id = fields.Many2one('account.analytic.account', 
                                          string='Cuenta Analítica', 
                                          track_visibility='always')
    operator_id         = fields.Many2one('res.partner', 
                                          string='Operador', 
                                          track_visibility='always')
    route               = fields.Char(string='Ruta', 
                                      track_visibility='always')
    # ----- State of the trip --------------------------------------------------------#                                         
    state               = fields.Selection(selection=[('assigned', 'Asignado'), 
                                                      ('route', 'En Ruta'), 
                                                      ('discharged', 'Descargado'), 
                                                      ('to_invoice', 'Por Facturar'), 
                                                      ('billed', 'Facturado'), 
                                                      ('charged', 'Cobrado')], 
                                           string='Estado', 
                                           required=True, 
                                           readonly=True, 
                                           copy=False, 
                                           tracking=True,
                                           default='assigned', 
                                           compute="_set_state", 
                                           store=True,
                                           track_visibility='always')                                          
    
    #|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|
    # FIELDS FOR LOAD DATA OF TRIPS
    #|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|
    start_date      = fields.Date(string='Fecha de inicio', 
                                  track_visibility='always')
    load_date       = fields.Date(string='Fecha de Carga', 
                                  track_visibility='always')
    estimated_qty   = fields.Float(string='Cantidad Estimada (kg)', 
                                   track_visibility='always')
    real_load_qty   = fields.Float(string='Cantidad Real de Carga (kg)', 
                                   track_visibility='always')
    decline_qty     = fields.Float(string='Merma', 
                                   compute='_set_decline_qty', 
                                   store=True, 
                                   track_visibility='always')
    attachment_load = fields.Many2many('ir.attachment', 
                                       relation='first_load_att_relation', 
                                       string='Adjuntos de Carga', 
                                       track_visibility='always')
    load_location   = fields.Char(string='Ubicación de Carga', 
                                  track_visibility='always')
   
    #|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|
    # FIELDS FOR DISCHARGE DATA OF TRIPS
    #|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|
    discharge_date       = fields.Date(string='Fecha de Descarga', 
                                       track_visibility='always')
    real_discharge_qty   = fields.Float(string='Cantidad Real de Descarga (kg)', 
                                        track_visibility='always')
    attachment_discharge = fields.Many2many('ir.attachment', 
                                            relation='second_discharge_att_relation', 
                                            string='Adjuntos de Descarga', 
                                            track_visibility='always')
    discount_decline     = fields.Float(string='Descuento por Merma', 
                                        track_visibility='always')
    qty_to_bill          = fields.Float(string='Importe a Facturar $', 
                                        compute='_set_qty_to_bill', 
                                        store=True, 
                                        track_visibility='always') 
    discharged_flag      = fields.Boolean(string="¿Viaje Descargado?",
                                          track_visibility='always')  
    discharge_location   = fields.Char(string='Ubicación de Descarga', 
                                       track_visibility='always')                                          
    conformity           = fields.Binary(string='Conformidad y Finiquito', 
                                         track_visibility='always')
    checked              = fields.Boolean(string="Conformidad y Finiquito") 

    #|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|
    # FIELDS FOR ANALYSIS, SALE AND ACCOUNT DATA OF TRIPS
    #|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|*|                                         
    sale_order_id        = fields.Many2one('sale.order', 
                                           string='Orden de Venta Generada', 
                                           ondelete='set null', 
                                           track_visibility='always')                                                                                   
    charged_flag         = fields.Boolean(string="¿Es un Viaje Cobrado?", 
                                          track_visibility='always') 
    account_move_id      = fields.Many2one('account.move', 
                                           string='Provisión',
                                           ondelete='set null', 
                                           track_visibility='always') 
    invoiced_flag        = fields.Boolean(string="¿Es un Viaje Facturado?", 
                                          track_visibility='always')                                            
    invoice              = fields.Char(string='Factura', 
                                       track_visibility='always')                                                                                                                                                                                                           



    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                    METHODS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    @api.onchange('contract_id')
    def _onchange_contract(self):
        '''Authomatic assignation for fields in Trips from contract_id's input'''
        if self.contract_id:
            self.client_id = self.contract_id.client_id.id 
            self.route     = self.contract_id.origin_id.name + ', ' + self.contract_id.destination_id.name            



    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        #Authomatic assignation for analytic account from vehicle_id's input
        if self.vehicle_id:
            self.analytic_account_id = self.vehicle_id.analytic_account_id.id



    @api.onchange('attachment_load')
    def _onchange_attachment_load(self):
        #Avoid that model "ir.attachment" generates records without res_id
        if self.attachment_load:
            for attachment in self.attachment_load:
                attachment.res_id = self.id



    @api.onchange('attachment_discharge')
    def _onchange_attachment_discharge(self):
        #Avoid that model "ir.attachment" generates records without res_id
        if self.attachment_discharge:
            for attachment in self.attachment_discharge:
                attachment.res_id = self.id
    


    @api.depends(
        'contract_id',
        'sucursal_id',
        'client_id',
        'vehicle_id',
        'analytic_account_id',  
        'operator_id',        
        'route',              
        'start_date',
        'load_date',       
        'estimated_qty',      
        'real_load_qty',      
        'load_location',
        'discharge_date',     
        'real_discharge_qty', 
        'discharged_flag',   
        'discharge_location',
        'checked',        
        'charged_flag',
        'account_move_id',
        'invoiced_flag',
        'invoice'
    )    
    def _set_state(self):
        '''Set up state in base a which fields are filled up at Form View of Trips'''
        #Get previous assigned state to this trip:
        state_init_aux = self.state

        # Dertemination of States:
        #
        # 'assigned'    --> without, few or empty fields in Trips Form
        #
        # 'route'       --> just with General and Load fields filled in Trips Form
        #
        # 'discharged'  --> just with General, Load and Discharge fields filled until "discharged_flag" in Trips Form
        #
        # 'to_invoice'  --> Only with General, Load and Discharge fields filled until "conformity" in Trips Form              
        #
        # 'billed'      --> With all General, Load and Discharge fields filled (including checks "discharged_flag"  and "conformity")
        #                   and with check of "invoiced_flag" and "invoice" also filled at Trips Form. The fields of "charged_flag" 
        #                   and "account_move_id" must be empty
        #
        # 'charged'     --> With all General, Load and Discharge fields filled (including checks "discharged_flag", "conformity" and
        #                   charged_flag with field "account_move_id" filled too) at Trips View Form. It doesn't have an invoice related
        #                   that's why check of "invoiced_flag" and "invoice" must be empty
        if self.contract_id          and self.sucursal_id        and self.client_id          and self.vehicle_id and \
            self.analytic_account_id and self.operator_id        and self.route              and self.start_date and \
            self.load_date           and self.estimated_qty      and self.real_load_qty      and self.load_location and \
            self.discharge_date      and self.real_discharge_qty and self.discharged_flag    and self.discharge_location and \
            self.checked             and self.charged_flag       and self.account_move_id    and not self.invoiced_flag and \
            not self.invoice:

                self.state = 'charged'  

        elif self.contract_id        and self.sucursal_id        and self.client_id           and self.vehicle_id and \
            self.analytic_account_id and self.operator_id        and self.route               and self.start_date and \
            self.load_date           and self.estimated_qty      and self.real_load_qty       and self.load_location and \
            self.discharge_date      and self.real_discharge_qty and self.discharged_flag     and self.discharge_location and \
            self.checked             and not self.charged_flag   and not self.account_move_id and self.invoiced_flag and \
            self.invoice:                

                self.state = 'billed'    

        elif self.contract_id        and self.sucursal_id        and self.client_id           and self.vehicle_id and \
            self.analytic_account_id and self.operator_id        and self.route               and self.start_date and \
            self.load_date           and self.estimated_qty      and self.real_load_qty       and self.load_location and \
            self.discharge_date      and self.real_discharge_qty and self.discharged_flag     and self.discharge_location and \
            self.checked             and not self.charged_flag   and not self.account_move_id and not self.invoiced_flag and \
            not self.invoice:                 

                self.state = 'to_invoice'   

        elif self.contract_id        and self.sucursal_id        and self.client_id           and self.vehicle_id and \
            self.analytic_account_id and self.operator_id        and self.route               and self.start_date and \
            self.load_date           and self.estimated_qty      and self.real_load_qty       and self.load_location and \
            self.discharge_date      and self.real_discharge_qty and self.discharged_flag     and self.discharge_location and \
            not self.checked         and not self.charged_flag   and not self.account_move_id and not self.invoiced_flag and \
            not self.invoice:  

                self.state = 'discharged'  

        elif self.contract_id        and self.sucursal_id            and self.client_id           and self.vehicle_id and \
            self.analytic_account_id and self.operator_id            and self.route               and self.start_date and \
            self.load_date           and self.estimated_qty          and self.real_load_qty       and self.load_location and \
            not self.discharge_date  and not self.real_discharge_qty and not self.discharged_flag and not self.discharge_location and \
            not self.checked         and not self.charged_flag       and not self.account_move_id and not self.invoiced_flag and \
            not self.invoice: 

                self.state = 'route'

        elif self.contract_id        and self.sucursal_id            and self.client_id           and self.vehicle_id and \
            self.analytic_account_id and self.operator_id            and self.route               and not self.start_date and \
            not self.load_date       and not self.estimated_qty      and not self.real_load_qty   and not self.load_location and \
            not self.discharge_date  and not self.real_discharge_qty and not self.discharged_flag and not self.discharge_location and \
            not self.checked         and not self.charged_flag       and not self.account_move_id and not self.invoiced_flag and \
            not self.invoice:

                self.state = 'assigned'             

        else:  #If none of above conditionals, then get previous state established and assign it again
            self.state = state_init_aux   



    @api.depends('real_load_qty', 'real_discharge_qty')
    def _set_decline_qty(self):
        for rec in self:
            rec.decline_qty = rec.real_load_qty - rec.real_discharge_qty



    @api.depends('contract_id', 'real_load_qty', 'discount_decline')
    def _set_qty_to_bill(self):
        #Get Tariff from Contract data belonging to this Trip:
        tariff = 0.0
        for rec in self:
            if rec.contract_id:
                tariff = rec.contract_id.tariff

                if rec.discount_decline:
                    rec.qty_to_bill = rec.real_load_qty * tariff - rec.discount_decline
                else:
                    rec.qty_to_bill = rec.real_load_qty * tariff        
          
 

    def creation_account_move(self):
        #When check "charged_flag" is True must be created an account.move:
        line_ids_list    = list()
        item             = tuple()
        dictionary_vals  = dict()

        #°°°°°°°°°°°°°°°°°°°°°°°°°°°
        # Creation of Account Move |
        #°°°°°°°°°°°°°°°°°°°°°°°°°°°          
        account_move = {
                'trips_acc_move_ids': [(4, self.id)],
                'ref': 'PROVISION',                
                'journal_id': 86,  #86 ID for Journal of "Contabilidad B" in Transportes de Alba ['Sistema' Company]             
               } 
        acc_mov_obj = self.env['account.move'].create(account_move )
        
        #Consult different info in order to fill up by default some fields in pop up window of account move        
        #°°°°°°°°°°°°°°°°°°°°°°
        #    For Debit Line   |
        #°°°°°°°°°°°°°°°°°°°°°°    
        account_id          = 2191 #2191 ID for Account of 105.01.001 "CLIENTES NACIONALES" in Transportes de Alba ['Sistema' Company]
        enterprise_id       = self.client_id.id
        name                = self.analytic_account_id.name + '|' + self.name
        analytic_account_id = self.analytic_account_id.id
        analytic_tag_ids    = self.env['account.analytic.tag'].search([('name', '=', self.name)], limit=1).ids          
        debit               = self.qty_to_bill                    
        credit              = 0.0
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
        #Append debit info into the list which it will be used later
        #in creation of account move lines:
        line_ids_list.append(dictionary_vals)   
        
        #°°°°°°°°°°°°°°°°°°°°°°
        #   For Credit Line   |
        #°°°°°°°°°°°°°°°°°°°°°°
        account_id          = 2310 #2310 ID for Account of 401.01.001 "INGRESOS POR SERVICIOS" in Transportes de Alba ['Sistema' Company]
        enterprise_id       = self.client_id.id
        name                = self.analytic_account_id.name + '|' + self.name
        analytic_account_id = self.analytic_account_id.id
        analytic_tag_ids    = self.env['account.analytic.tag'].search([('name', '=', self.name)], limit=1).ids          
        debit               = 0.0
        credit              = self.qty_to_bill     
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
        #Append crebit info into the list which it will be used later
        #in creation of account move lines:
        line_ids_list.append(dictionary_vals)   

        #Creation of account move lines:
        self.env['account.move.line'].create(line_ids_list)
                                                                      
        #°°°°°°°°°°°°°°°°°°°°°°
        # Account Move Pop Up |
        #°°°°°°°°°°°°°°°°°°°°°°           
        return {
            'name': "Creación de Asiento Contable",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': acc_mov_obj.id, #Account Move Previously Created
            'view_id': self.env.ref('account.view_move_form').id,                                
            'target': 'new'
        }