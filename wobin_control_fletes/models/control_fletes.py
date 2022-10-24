# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import date, datetime
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _

# /////////////////////////////////////////////////////////////////////////////
#
#   Development to create a new PDF report from Odoo Studio View 
#   "Líneas de Pedido de Ventas" where also it was necessary add
#   new custom fields.
#
#   Also it was created a new Report {List View} and PDF for Management
#   of Fleets (with new custom fields too)
#
# /////////////////////////////////////////////////////////////////////////////

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    #Fields added to Form View of Inventory > Operations > Transfers     
    orden_servicio        = fields.Many2one('wobin.orden.servicio', string='Orden de Servicio')




class WobinOrdenServicio(models.Model):
    _name = 'wobin.orden.servicio'
    _description = 'Wobin Orden de Servicio'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 

    @api.model
    def create(self, vals):  
        """This method intends to create a sequence for a given Service Order"""            
        #Change of sequence (if it isn't stored is shown "New" else e.g OSF00001) 
        if vals.get('name', 'New') == 'New':
            sequence = self.env['ir.sequence'].next_by_code('self.osf') or 'New'
            vals['name'] = sequence     
            res = super(WobinOrdenServicio, self).create(vals)  

        return res 


    name         = fields.Char(string="Orden de Servicio", readonly=True, required=True, copy=False, default='New')
    partner_id   = fields.Many2one('res.partner', string='Proveedor', track_visibility='always')
    estado       = fields.Selection([('borrador', 'Borrador'), 
                                     ('oc_relacionada', 'OC Relacionada')   
                                    ], string='Estado', default='borrador', track_visibility='always')                                          
    pickings_ids = fields.One2many('wobin.orden.servicio.lineas', 'wbn_service_order_id', string='Control de Albaranes')
    purchase_with_order_id = fields.Many2one('purchase.order', string='Orden de Compra', track_visibility='always')
    purchase_provider      = fields.Char(string='Proveedor de Ord. Compra', related='purchase_with_order_id.partner_id.name', track_visibility='always')
    purchase_invoice_state = fields.Selection([('no', 'Nothing to Bill'),
                                               ('to invoice', 'Waiting Bills'),
                                               ('invoiced', 'No Bill to Receive'),
                                              ], string='Estado de Facturación', related='purchase_with_order_id.invoice_status', store=True, default='no', track_visibility='always') 
    tarifas             = fields.Float(string='Tarifas (MXP/TON)', digits=(20, 4), track_visibility='always') 
    currency_id         = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)
    precio_producto     = fields.Monetary('Precio Producto (MXP/TON)', currency_field='currency_id', track_visibility='always')
    precio_producto_lbl = fields.Monetary('[Precio Producto Calculado]', currency_field='currency_id', compute='_set_precio_producto', store=True, track_visibility='always')

    #USEFUL CALCULATIONS FROM SERVICE ORDER LINES
    pago_efectivo         = fields.Boolean(string='Pago Efectivo')
    sum_toneladas_origen  = fields.Float(digits=(20, 3), compute='_set_sum_toneladas_origen', store=True)
    sum_toneladas_ef_entregadas = fields.Float(digits=(20, 3), compute='_set_sum_toneladas_ef_entregadas', store=True)
    dif_merma_excedente   = fields.Float(string='Diferencia Merma', digits=(20, 3), compute='_set_dif_merma_excedente', store=True, track_visibility='always')   
    tolerancia            = fields.Float(string='Tolerancia Sistema', digits=(20, 3), compute='_set_tolerancia', store=True, track_visibility='always')
    tolerancia_ajustada   = fields.Float(string='Tolerancia Ajustada', digits=(20, 3), track_visibility='always')
    tolerancia_autorizada = fields.Float(string='Tolerancia Autorizada', digits=(20, 3), compute='_set_tolerancia_autorizada', store=True, track_visibility='always')
    tolerancia_excedida   = fields.Float(string='Tolerancia Excedida', digits=(20, 3), compute='_set_tolerancia_excedida', store=True, track_visibility='always')    
    subtotal_antes_desc   = fields.Float(string='Subtotal antes Descuento', digits=(20, 3), compute='_set_subtotal_antes_desc', store=True, track_visibility='always')    
    desc_tolerancia_exced = fields.Monetary('Descuento por Tolerancia Excedida', currency_field='currency_id', compute='_set_desc_tolerancia_exced', store=True, track_visibility='always')
    importe               = fields.Monetary('Importe', currency_field='currency_id', compute='_set_importe', store=True, track_visibility='always')
    iva                   = fields.Monetary('IVA', currency_field='currency_id', compute='_set_iva', store=True, track_visibility='always')
    retencion             = fields.Monetary('Retención', currency_field='currency_id', compute='_set_retencion', store=True, track_visibility='always')
    total                 = fields.Monetary('Total', currency_field='currency_id', compute='_set_total', store=True, track_visibility='always')        
    total_pago_efectivo   = fields.Monetary('Total', currency_field='currency_id', compute='_set_total_pago_efectivo', store=True, track_visibility='always')        
    company_id            = fields.Many2one('res.company', default=lambda self: self.env['res.company']._company_default_get('your.module'))              
    
    
    @api.onchange('pickings_ids')
    def _onchange_pickings_ids(self): 
        list_origin = []
        list_destiny = []

        for line in self.pickings_ids:
            
            if line.transferencia_origen_id:
                if line.transferencia_origen_id == line.transferencia_destino_id:
                    msg = _('No se pueden duplicar albaranes. Revisar %s y %s') % (line.transferencia_origen_id.name, line.transferencia_destino_id.name)
                    raise UserError(msg)
                
                #Append ids from origin transfers:
                list_origin.append((line.transferencia_origen_id, line.producto_id))

            elif line.transferencia_destino_id:
                if line.transferencia_destino_id == line.transferencia_origen_id:
                    msg = _('No se pueden duplicar albaranes. Revisar %s y %s') % (line.transferencia_origen_id.name, line.transferencia_destino_id.name)
                    raise UserError(msg) 
                
                #Append ids from destiny transfers:
                list_destiny.append((line.transferencia_destino_id, line.producto_destino_id))

        #Avoid duplicates in lines:
        for elem in list_origin:
            if list_origin.count(elem) > 1:
                msg = _('No se pueden duplicar albaranes. Revisar albarán %s') % (elem[0].name)
                raise UserError(msg)

        for elem in list_destiny:
            if list_destiny.count(elem) > 1:
                msg = _('No se pueden duplicar albaranes. Revisar albarán %s') % (elem[0].name)
                raise UserError(msg)         
                     


    @api.depends('pickings_ids') 
    def _set_precio_producto(self):
        if not self.precio_producto_lbl:
            #Iterate over lines until find a destiny move:
            for line in self.pickings_ids:
                if line.transferencia_destino_id: 
                    #Get Order Sale ID or Purchase Order from current tranfer
                    sale_order        = line.transferencia_destino_id.sale_id.id
                    purchase_order    = line.transferencia_destino_id.purchase_id.id
                    picking_type_code = line.transferencia_destino_id.picking_type_code
                    
                    if sale_order and line.producto_destino_id:
                        precio_unitario = self.env['sale.order.line'].search([('order_id', '=', sale_order),
                                                                              ('product_id', '=', line.producto_destino_id.id)], limit=1).price_unit         
                        self.precio_producto_lbl = precio_unitario
                    
                    elif purchase_order and line.producto_destino_id:
                        precio_unitario = self.env['purchase.order.line'].search([('order_id', '=', purchase_order),
                                                                                  ('product_id', '=', line.producto_destino_id.id)], limit=1).price_unit         
                        self.precio_producto_lbl = precio_unitario                     

                    elif picking_type_code == 'internal':
                        self.precio_producto_lbl = 0.0
                    
                    #End iterations
                    break


    # USEFUL CALCULATIONS FROM SERVICE ORDER LINES
    # / / / / / / / / / / / / / / / / / / / / / / /
    @api.depends('pickings_ids')
    def _set_sum_toneladas_origen(self):
        self.sum_toneladas_origen = sum(line.toneladas_origen for line in self.pickings_ids)


    @api.depends('pickings_ids')
    def _set_sum_toneladas_ef_entregadas(self):
        self.sum_toneladas_ef_entregadas = sum(line.toneladas_ef_entregados for line in self.pickings_ids)


    @api.depends('sum_toneladas_origen', 'sum_toneladas_ef_entregadas')    
    def _set_dif_merma_excedente(self):
        diff_aux = self.sum_toneladas_origen - self.sum_toneladas_ef_entregadas 
        if diff_aux > 0:
            self.dif_merma_excedente = diff_aux
        else:
            self.dif_merma_excedente = 0.00


    @api.depends('sum_toneladas_origen')     
    def _set_tolerancia(self):    
        self.tolerancia = self.sum_toneladas_origen * 0.002


    @api.depends('tolerancia', 'tolerancia_ajustada')    
    def _set_tolerancia_autorizada(self):
        self.tolerancia_autorizada = self.tolerancia + self.tolerancia_ajustada


    @api.depends('dif_merma_excedente', 'tolerancia_autorizada') 
    def _set_tolerancia_excedida(self):  
        monto_aux_tol_exc = self.sum_toneladas_origen - self.sum_toneladas_ef_entregadas - self.tolerancia_autorizada
        if monto_aux_tol_exc > 0:
            self.tolerancia_excedida = monto_aux_tol_exc
        else:
            self.tolerancia_excedida = 0.00
         

    @api.depends('sum_toneladas_origen') 
    def _set_subtotal_antes_desc(self):       
        self.subtotal_antes_desc = self.sum_toneladas_origen * self.tarifas


    @api.depends('tolerancia_excedida') 
    def _set_desc_tolerancia_exced(self):
        if self.tolerancia_excedida <= 0:
            self.desc_tolerancia_exced = 0.0
        elif self.tolerancia_excedida > 0:
            self.desc_tolerancia_exced = self.tolerancia_excedida * self.precio_producto


    @api.depends('subtotal_antes_desc', 'desc_tolerancia_exced') 
    def _set_importe(self):
        self.importe = self.subtotal_antes_desc - self.desc_tolerancia_exced


    @api.depends('importe') 
    def _set_iva(self): 
        self.iva = self.importe * 0.16


    @api.depends('importe') 
    def _set_retencion(self): 
        self.retencion = self.importe * 0.04


    @api.depends('importe', 'iva', 'retencion') 
    def _set_total(self):               
        self.total = self.importe + self.iva - self.retencion


    @api.depends('importe') 
    def _set_total_pago_efectivo(self):               
        self.total_pago_efectivo = self.importe






class WobinOrdenServicioLineas(models.Model):
    _name = 'wobin.orden.servicio.lineas'
    _description = 'Wobin Orden de Servicio Líneas'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 


    _sql_constraints = [('transferencia_origen', 
                         'unique (transferencia_origen_id)',     
                         'Albaranes duplicados no están permitidos por línea'),
                        ('transferencia_destino', 
                         'unique (transferencia_destino_id)',     
                         'Albaranes duplicados no están permitidos por línea')]


    #General Data:
    wbn_service_order_id     = fields.Many2one('wobin.orden.servicio', string='Orden de Servicio')
    estado_wbn_servi_ord     = fields.Selection([('borrador', 'Borrador'), 
                                                 ('oc_relacionada', 'OC Relacionada') 
                                                ],string='Estado', related='wbn_service_order_id.estado')
    wbn_pur_order_related    = fields.Char(string="Orden de Compra", related='wbn_service_order_id.purchase_with_order_id.name', store=True)
    company_id               = fields.Many2one('res.company', default=lambda self: self.env['res.company']._company_default_get('your.module'))    
                                    
    #Upload Origin Data:
    transferencia_origen_id  = fields.Many2one('stock.picking', string='Movimiento Origen')    
    fecha_carga_origen       = fields.Date(string='Fecha Carga', compute='_set_fecha_carga', store=True)
    producto_id              = fields.Many2one('product.product', string='Producto', compute='_set_producto_id', store=True)
    toneladas_origen         = fields.Float(string='Ton. Carga', digits=(20, 3), compute='_set_toneladas_origen', store=True)
    
    #Discharge Destiny Data:
    transferencia_destino_id = fields.Many2one('stock.picking', string='Movimiento Destino')
    fecha_descarga_destino   = fields.Date(string='Fecha Entrega', compute='_set_fecha_descarga', store=True)
    producto_destino_id      = fields.Many2one('product.product', string='Producto', compute='_set_producto_destino_id', store=True)
    toneladas_destino        = fields.Float(string='Ton. Entrega', digits=(20, 3), compute='_set_toneladas_destino', store=True)
    toneladas_ef_entregados  = fields.Float(string='Ton. Efectivamente Entregadas', digits=(20, 3), compute='_set_toneladas_ef_entregados', readonly=False, store=True)



    def create(self, vals):
        #Override write method in order to detect fields changed:
        res = super(WobinOrdenServicioLineas, self).create(vals) 
        
        for dic in vals:
            for key in dic:                
                if dic['transferencia_origen_id']:
                    picking_obj = self.env['stock.picking'].browse(dic['transferencia_origen_id'])
                    picking_obj.orden_servicio = dic['wbn_service_order_id']   

                if dic['transferencia_destino_id']:
                    picking_obj = self.env['stock.picking'].browse(dic['transferencia_destino_id'])
                    picking_obj.orden_servicio = dic['wbn_service_order_id']               
        return res



    def _actualizacion_albaranes_ord_servicio(self, orden_servicio_id, ord_serv_linea, bandera_is_unlink):
            # / - / -  / - / -  / - / -  / - / -  / - / -  / - / -  / - / -  / - / -  / - / -  / - / -  / - / -  / - / -  / - /
            #Get from Stock.Pickings all posible records with this Service Order:
            pickings = self.env['stock.picking'].search([('orden_servicio', '=', orden_servicio_id)]).ids
            
            #Create set() for all posible pickings with that service order:
            posible_pickings_set = set(pickings)            

            #Get real and correct related pickings:
            real_pickings_obj_list = self.env['wobin.orden.servicio.lineas'].search([('wbn_service_order_id', '=', orden_servicio_id)])                   
            
            #Create set() for real pickings:
            real_pickings_set = set()
            for picking in real_pickings_obj_list:                
                if picking.transferencia_origen_id.id:                    
                    real_pickings_set.add(picking.transferencia_origen_id.id)
                
                if picking.transferencia_destino_id.id:
                    real_pickings_set.add(picking.transferencia_destino_id.id)  

            #Due to real_pickings_set is a set() and this proccess just apply for deletion
            #it's important to remove the present item triggered by calling of method in order 
            #not to be added into real_pickings set() and so to achieve symetric difference:
            if bandera_is_unlink == True:                
                picking_obj = self.env['wobin.orden.servicio.lineas'].search([('id', '=', ord_serv_linea)])
                
                if picking_obj.transferencia_origen_id:
                    real_pickings_set.remove(picking_obj.transferencia_origen_id.id) 
                if picking_obj.transferencia_destino_id:
                    real_pickings_set.remove(picking_obj.transferencia_destino_id.id)                                                                          

            #UNLINK Records unnecessary ones by Set() Symetric Difference:
            set_recs_to_delete = set()                           
            
            set_recs_to_delete = posible_pickings_set.symmetric_difference(real_pickings_set)

            for item in set_recs_to_delete:
                picking_d_obj = self.env['stock.picking'].search([('id', '=', item)])
                picking_d_obj.orden_servicio = None  



    def write(self, vals):
        #Override write method in order to detect fields changed:
        res = super(WobinOrdenServicioLineas, self).write(vals)         

        if vals.get('transferencia_origen_id'):
            picking_obj = self.env['stock.picking'].browse(vals.get('transferencia_origen_id'))
            picking_obj.orden_servicio = self.wbn_service_order_id.id
            #Calling of method in order to avoid inconsistences when write event is active
            self._actualizacion_albaranes_ord_servicio(self.wbn_service_order_id.id, self.id, False)                                                      

        if vals.get('transferencia_destino_id'):
            picking_obj = self.env['stock.picking'].browse(vals.get('transferencia_destino_id'))
            picking_obj.orden_servicio = self.wbn_service_order_id.id
            #Calling of method in order to avoid inconsistences when write event is active
            self._actualizacion_albaranes_ord_servicio(self.wbn_service_order_id.id, self.id, False)

        return res  



    def unlink(self):
        #Override write method in order to detect fields changed:
        for rec in self:                     
            if rec.wbn_service_order_id.id:
                #Calling of method in order to avoid inconsistences when write event is active
                self._actualizacion_albaranes_ord_servicio(rec.wbn_service_order_id.id, rec.id, True)  
    
        return super(WobinOrdenServicioLineas, self).unlink()                           
    
    
        
    #/ - / - / - / - / - / - / - / - / - / - / - /
    #Upload Origin Methods
    #/ - / - / - / - / - / - / - / - / - / - / - /  
    @api.depends('transferencia_origen_id')
    def _set_fecha_carga(self):
        for rec in self:     
            if rec.transferencia_origen_id and not rec.transferencia_destino_id:        
                fecha_carga_origen_aux = self.env['stock.picking'].search([('id', '=', rec.transferencia_origen_id.id)], limit=1).date_done
                
                if fecha_carga_origen_aux:
                    rec.fecha_carga_origen = fecha_carga_origen_aux.date()


    @api.depends('transferencia_origen_id')
    def _set_producto_id(self):  
        for rec in self:           
            if rec.transferencia_origen_id and not rec.transferencia_destino_id: 
                rec.producto_id = self.env['stock.move'].search([('picking_id', '=', rec.transferencia_origen_id.id)], limit=1).product_id.id


    @api.depends('transferencia_origen_id')
    def _set_toneladas_origen(self):
        for rec in self:        
            if rec.transferencia_origen_id and not rec.transferencia_destino_id: 
                rec.toneladas_origen = self.env['stock.move'].search([('picking_id', '=', rec.transferencia_origen_id.id)], limit=1).quantity_done    
 


    #/ - / - / - / - / - / - / - / - / - / - / - /
    #Discharge Destiny Methods
    #/ - / - / - / - / - / - / - / - / - / - / - /
    @api.depends('transferencia_destino_id')
    def _set_fecha_descarga(self):
        for rec in self:
            if rec.transferencia_destino_id and not rec.transferencia_origen_id:        
                fecha_destino_aux = self.env['stock.picking'].search([('id', '=', rec.transferencia_destino_id.id)], limit=1).date_done

                if fecha_destino_aux:
                    rec.fecha_descarga_destino = fecha_destino_aux.date()


    @api.depends('transferencia_destino_id')
    def _set_producto_destino_id(self):    
        for rec in self:            
            if rec.transferencia_destino_id and not rec.transferencia_origen_id:        
                rec.producto_destino_id = self.env['stock.move'].search([('picking_id', '=', rec.transferencia_destino_id.id)], limit=1).product_id.id
              
    
    @api.depends('transferencia_destino_id')
    def _set_toneladas_destino(self):    
        for rec in self:            
            if rec.transferencia_destino_id and not rec.transferencia_origen_id:        
                rec.toneladas_destino = self.env['stock.move'].search([('picking_id', '=', rec.transferencia_destino_id.id)], limit=1).quantity_done    
    

    @api.depends('transferencia_destino_id')
    def _set_toneladas_ef_entregados(self): 
        for rec in self:  
            if not rec.toneladas_ef_entregados:     
                if rec.transferencia_destino_id and not rec.transferencia_origen_id:        
                    rec.toneladas_ef_entregados = self.env['stock.move'].search([('picking_id', '=', rec.transferencia_destino_id.id)], limit=1).quantity_done   






class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    wbn_service_order_ids    = fields.One2many('wobin.orden.servicio', 'purchase_with_order_id', string='Ordenes de Servicio')
    summation_service_orders = fields.Float(string='Suma de Ord. de Servicio', digits=(20, 3), compute='_set_sumatoria_osfs', store=True)


    def write(self, vals):
        #Override write method in order to detect fields changed:
        res = super(PurchaseOrder, self).write(vals) 

        if vals.get('state', False):
            purchase = None
            #Get Purchase Order data and its state:
            purchase = self.name 
            if purchase:            
                purchase_state = self.state
                #If the Purchase Order has changed its state to "purchase" it's important to change
                #Service Order's state to "oc_relacionada"
                if purchase_state == 'purchase':
                    orden_servicio_obj = self.env['wobin.orden.servicio'].search([('purchase_with_order_id', '=', self.id)])                    
                    
                    if orden_servicio_obj:                        
                        for osf in orden_servicio_obj:
                            osf.estado = 'oc_relacionada'

                #If the Purchase Order has changed its state to "cancel" it's important to change
                #Service Order's state to "borrador"                                            
                if purchase_state == 'cancel':
                    orden_servicio_obj = self.env['wobin.orden.servicio'].search([('purchase_with_order_id', '=', self.id)])
                    
                    if orden_servicio_obj:                        
                        for osf in orden_servicio_obj:
                            osf.estado = 'borrador'                            
                                       
        if vals.get('wbn_service_order_ids', False):
            #Construction of post message's content:
            uid = self.env.user.id
            name_user = self.env['res.users'].search([('id', '=', uid)]).name

            post =  "<ul style=\"margin:0px 0 9px 0\">"
            post += "<li><p style='margin:0px; font-size:13px; font-family:\"Lucida Grande\", Helvetica, Verdana, Arial, sans-serif'>Usuario que modificó el campo de Órdenes de Servicio: <strong>" + name_user + "</strong></p></li>"
            post += "</ul>"
            
            self.message_post(body = post)
                            
        return res


    @api.depends('wbn_service_order_ids') 
    def _set_sumatoria_osfs(self):
        if self.wbn_service_order_ids:
            #Sum up all total amounts from 
            self.summation_service_orders = sum(line.importe for line in self.wbn_service_order_ids)