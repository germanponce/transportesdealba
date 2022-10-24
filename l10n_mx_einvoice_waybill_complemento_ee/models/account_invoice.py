# -*- encoding: utf-8 -*-
# Coded by German Ponce Dominguez 
#     ▬▬▬▬▬.◙.▬▬▬▬▬  
#       ▂▄▄▓▄▄▂  
#    ◢◤█▀▀████▄▄▄▄▄▄ ◢◤  
#    █▄ █ █▄ ███▀▀▀▀▀▀▀ ╬  
#    ◥ █████ ◤  
#     ══╩══╩═  
#       ╬═╬  
#       ╬═╬ Dream big and start with something small!!!  
#       ╬═╬  
#       ╬═╬ You can do it!  
#       ╬═╬   Let's go...
#    ☻/ ╬═╬   
#   /▌  ╬═╬   
#   / \
# Cherman Seingalt - german.ponce@outlook.com

from odoo import api, fields, models, _, tools
from datetime import datetime, date
import time
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.osv import osv, expression

import re

import logging
_logger = logging.getLogger(__name__)

class InvoiceWaybillTrailerInfo(models.Model):
    _name = 'invoice.waybill.trailer.info'
    _description = 'Nodos para Remolques'
    
    invoice_id = fields.Many2one('account.move', 'Factura')

    subtype_trailer_id = fields.Many2one('waybill.tipo.remolque', 'Subtipo Remolque',
                                              help="Atributo: SubTipoRem")

    trailer_plate_cp = fields.Char('Placa',
                                              help="Atributo: Placa")

    
class AccountInvoice(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    @api.depends('invoice_line_complement_cp_ids')
    def _get_total_items_cp(self):
        total_quantity_items = 0
        for rec in self:
            if rec.invoice_line_complement_cp_ids:
                total_quantity_items = len(rec.invoice_line_complement_cp_ids)
            rec.total_quantity_items = total_quantity_items

    def _get_permiso_general_tpaf01(self):
        code = 'TPAF01'
        tipo_permiso_obj = self.env["waybill.tipo.permiso"]
        tipo_permiso_general_id = tipo_permiso_obj.search([('code','=',code)], limit=1)
        if tipo_permiso_general_id:
            return tipo_permiso_general_id.id
        else:
            return False

    @api.depends('invoice_line_complement_cp_ids')
    def _get_weight_total(self):
        for rec in self:
            weight_charge_total = 0
            if rec.invoice_line_complement_cp_ids:
                for merchandise in rec.invoice_line_complement_cp_ids:
                    weight_line = merchandise.weight_charge * merchandise.quantity
                    weight_charge_total += weight_line
                    # weight_charge_total += merchandise.weight_charge
            rec.weight_charge_total = weight_charge_total
            rec.weight_charge_gross_total = weight_charge_total

    def _get_default_clave_transporte(self):
        clave_transporte_obj = self.env['waybill.clave.transporte']
        clave_transporte_federal = clave_transporte_obj.search([('code','=','01')], limit=1)
        if clave_transporte_federal:
            return clave_transporte_federal.id
        
        return False

    def _get_default_station_01(self):
        tipo_estacion_obj = self.env['waybill.tipo.estacion']
        estacion_nacional = tipo_estacion_obj.search([('code','=','01')], limit=1)
        if estacion_nacional:
            return estacion_nacional.id
        
        return False

    @api.depends('location_destiny_ids')
    def _get_distance_total(self):
        for rec in self:
            travel_total_distance = 0
            if rec.invoice_line_complement_cp_ids:
                for location in rec.location_destiny_ids:
                    distance_loc = location.location_destiny_distance
                    travel_total_distance += distance_loc
            rec.travel_total_distance = travel_total_distance

    cfdi_complemento = fields.Selection([('na','Sin Complemento'),('carta_porte', 'Carta porte')],
        string='Complemento CFDI', readonly=True, states={'draft': [('readonly', False)]}, 
                                        copy=False, default='na', required=True)  

    ### Lineas ###
    invoice_line_complement_cp_ids = fields.One2many('invoice.line.complement.cp', 'invoice_id',
                                                     'Lineas Complemento CP', copy=True, auto_join=True)
    ##############
    international_shipping = fields.Selection([('SI','SI'),('NO','NO')], 'Transporte Internacional', 
                                              default="NO", help="Atributo: TranspInternac")

    # CP 2.0 #
    merchandice_country_origin_id =  fields.Many2one('res.country', 'País de origen o destino',
                                     help="Atributo: PaisOrigenDestino, Se registra el origen o destino de los bienes.")
    tipo_transporte_entrada_salida_id = fields.Many2one('waybill.clave.transporte', 'Via Entrada Salida',
                                         help="Atributo: ViaEntradaSalida",  default=_get_default_clave_transporte)

    ##########

    shipping_complement_type = fields.Selection([('Entrada','Entrada'),('Salida','Salida')], 'Entrada/Salida Mercancia', default="Salida",
                                                help="Atributo: EntradaSalidaMerc")

    tipo_transporte_id = fields.Many2one('waybill.clave.transporte', 'Tipo Transporte',
                                         help="Atributo: ViaEntradaSalida", default=_get_default_clave_transporte)

    tipo_transporte_code = fields.Char('Codigo Tipo Transporte', related="tipo_transporte_id.code",
                                         help="Atributo: ViaEntradaSalida")

    travel_total_distance =  fields.Float('Distancia total recorrida', digits=(14,2),
                                         help="Atributo: TotalDistRec", compute="_get_distance_total")

    travel_total_distance_type = fields.Selection([('KM','Kilometros'),('M','Metros')], 
                                                  'Tipo Distancia Recorrida (Total)',
                                                  default="KM")
    
    ### Ubicaciones ###

    # CP 2.0 #

    location_origin_ids = fields.One2many('invoice.complement.location.cp', 'invoice_origin_id', 'Ubicaciones Origen', copy=True)
    location_destiny_ids = fields.One2many('invoice.complement.location.cp', 'invoice_destiny_id', 'Ubicaciones Destino', copy=True)

    ##########

    # CP 2.0 #

    weight_charge_total = fields.Float('Peso Neto Total', digits=(14,3), compute="_get_weight_total")
    
    weight_charge_gross_total = fields.Float('Peso Bruto Total', digits=(14,3))

    uom_weight_id =  fields.Many2one('waybill.unidad.peso', 'Unidad de Peso')

    total_quantity_items = fields.Integer('Total Mercancias', compute="_get_total_items_cp",
                                         help="Atributo: NumTotalMercancias")

    waybill_tasc_charges = fields.Float('Cargo por Tasacion', digits=(14,2),
                                         help="Atributo: CargoPorTasacion")

    # FIN CP 2.0 #


    type_stc_permit_id = fields.Many2one('waybill.tipo.permiso', 'Permiso STC',
                                                     help="Atributo: PermSCT", default=_get_permiso_general_tpaf01)

    type_stc_permit_number = fields.Char('Numero Permiso STC',
                                                     help="Atributo: NumPermisoSCT")

    # partner_insurance_id = fields.Many2one('res.partner', 'Aseguradora',
    #                                        help="Atributo: NombreAseg")

    # partner_insurance_number = fields.Char('No. Póliza Seguro', related="partner_insurance_id.partner_insurance_number", 
    #                                     readonly=False, help="Atributo: NumPolizaSeguro")

    configuracion_federal_id = fields.Many2one('waybill.configuracion.autotransporte.federal', 'Configuracion Auto Transporte Federal',
                                              help="Atributo: ConfigVehicular")

    vehicle_plate_cp = fields.Char('Placa Vehicular',
                                              help="Atributo: PlacaVM")

    vehicle_year_model_cp = fields.Char('Año del Modelo',
                                              help="Atributo: AnioModeloVM")

    trailer_line_ids = fields.One2many('invoice.waybill.trailer.info', 'invoice_id', 'Remolques', copy=True)


    
    waybill_origin_station_id = fields.Many2one(
        'waybill.complemento.estacion', string='Estación Origen')
    waybill_destiny_station_id = fields.Many2one(
        'waybill.complemento.estacion', string='Estación Destino')
    waybill_num_guia_aereo = fields.Char(string="Número Guía")
    waybill_transportista_aereo_id = fields.Many2one('res.partner', string="Transportista")
    codigo_transportista_aereo_id = fields.Many2one(related="waybill_transportista_aereo_id.codigo_transportista_aereo_id")
    waybill_embarcador_aereo_id = fields.Many2one('res.partner', string="Embarcador")

    waybill_pedimento = fields.Char(string="Pedimento")

    # CP 2.0 #

    insurance_ids = fields.One2many('invoice.complements.insurance', 'invoice_id', 'Aseguradoras', copy=True)

    partner_insurance_id = fields.Many2one('res.partner', 'Aseguradora',
                                           help="Atributo: NombreAseg")

    partner_insurance_number = fields.Char('No. Póliza Seguro', related="partner_insurance_id.partner_insurance_number", 
                                        readonly=False, help="Atributo: NumPolizaSeguro")
    
    driver_figure_ids = fields.One2many('invoice.complements.transport.figure', 'operators_invoice_id', 
        'Operadores', copy=True)

    other_figure_ids = fields.One2many('invoice.complements.transport.figure', 'others_invoice_id', 
        'Figuras Transporte', copy=True)

    # FIN CP 2.0 #
    
    ### Gestión del Excel ####

    waybill_datas_fname = fields.Char('Nombre Archivo',size=256)

    waybill_file = fields.Binary("Reporte")

    ##########################
    
    @api.onchange('waybill_num_guia_aereo')
    def _onchange_waybill_num_guia_aereo(self):
        if self.waybill_num_guia_aereo and (len(self.waybill_num_guia_aereo) < 12 or len(self.waybill_num_guia_aereo) > 15):
            raise ValidationError(_('Aviso!\n\nLa longitud para el Número de Guía debe ser entre 12 y 15 caracteres'))


    @api.onchange('tipo_transporte_id')
    def _onchange_tipo_transporte_id(self):
        if self.tipo_transporte_id.code not in ('01','03'):
            raise ValidationError(_("Advertencia!\n\nSolo se soporta 01 (Autotransporte Federal) y 03 (Transporte Aéreo)"))
        
        if self.tipo_transporte_id.code == '01': # Autotransporte
            self.type_stc_permit_id = self.env["waybill.tipo.permiso"].search([('code','=','TPAF01')], limit=1).id
            
        elif self.tipo_transporte_id.code == '03': # Aereo
            self.type_stc_permit_id = self.env["waybill.tipo.permiso"].search([('code','=','TPTA01')], limit=1).id

    @api.onchange('weight_charge_total')
    def onchange_weight_charge_total(self):
        if self.weight_charge_total:
            self.weight_charge_gross_total = self.weight_charge_total

    def refresh_complement_waybill_data(self):

        return True

#### Carta Porte 2.0 ####

##### Figuras Transporte #####
class InvoiceComplementsTransportFigure(models.Model):
    _name = 'invoice.complements.transport.figure'
    _description = 'Figuras Transporte Carta Porte'
    _rec_name = 'figure_name'

    @api.depends('partner_id')
    def  _get_figure_name(self):
        for rec in self:
            figure_name  =  ""
            if rec.partner_id:
                figure_name = rec.partner_id.name
            rec.figure_name = figure_name


    figure_name  = fields.Char('Nombre Figura', size=128, compute="_get_figure_name")

    is_operator = fields.Boolean('Operadores')

    operators_invoice_id = fields.Many2one('account.move', 'Ref Op. Factura')  

    others_invoice_id = fields.Many2one('account.move', 'Ref Factura')  

    partner_id = fields.Many2one('res.partner', 'Contacto',
                                                help="Atributo: AseguraRespCivil")

    figure_type_id = fields.Many2one('waybill.figura.transporte', 'Tipo Figura',
                                         help="Atributo: Tipo TipoFigura")

    figure_type_code = fields.Char('Codigo Tipo Figura', related="figure_type_id.code",
                                         help="Atributo: Tipo TipoFigura")

    transport_part_id = fields.Many2one('waybill.parte.transporte', 'Tipo Parte Transporte',
                                         help="Atributo: Figura Transporte")

    transport_part_ids = fields.Many2many('waybill.parte.transporte', 'transport_figure_part_rel',
                                         'transport_id', 'parte_id', 'Tipos Parte Transporte')

    driver_cp_vat = fields.Char('RFC Operador', related="partner_id.vat", 
                                        readonly=False, help="Atributo: RFCOperador")

    cp_driver_license = fields.Char('Numero de Licencia', related="partner_id.cp_driver_license", 
                                        readonly=False, help="Atributo: NumLicencia")

    add_address  = fields.Boolean('Agregar Dirección', 
                                  help="Agrega la dirección en el complemento Carta Porte para la Figura de Transporte")

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id and not self.is_operator:
            if self.partner_id.figure_type_id:
                self.figure_type_id = self.partner_id.figure_type_id.id
            if self.transport_part_ids:
                transport_part_ids =  self.transport_part_ids.ids
                self.transport_part_ids = [(6,0,transport_part_ids)]

    @api.onchange('is_operator')
    def onchange_is_operator(self):
        if self.is_operator:
            figure_type_obj =  self.env['waybill.figura.transporte']
            figure_type_id  = figure_type_obj.search([('code','=','01')], limit=1)
            if figure_type_id:
                self.figure_type_id = figure_type_id.id
    

    @api.constrains('is_operator','figure_type_id')
    def _constraint_figure_type(self):
        for rec in self:
            if not rec.is_operator and rec.figure_type_id and rec.figure_type_id.code == '01':
                raise ValidationError("Capture la figura de Operador en el apartado de Operadores.")
            if rec.figure_type_id:
                if rec.figure_type_id.code not in ('02','03'):
                    rec.transport_part_ids = False
        return True

##### Seguros #####
class InvoiceComplementsInsurance(models.Model):
    _name = 'invoice.complements.insurance'
    _description = 'Seguros Carta Porte'
    _rec_name = 'insurance_partner_id'

    invoice_id = fields.Many2one('account.move', 'Ref Factura')  

    insurance_partner_id = fields.Many2one('res.partner', 'Aseguradora',
                                                help="Atributo: AseguraRespCivil")

    insurance_policy = fields.Char(string="No. Póliza Seguro", related="insurance_partner_id.insurance_policy", 
                                                help="Atributo: PolizaRespCivil", size=50, readonly=False)

    ambiental_insurance_partner_id = fields.Many2one('res.partner', 'Aseguradora Medio Amb.',
                                                help="Atributo: AseguraMedAmbiente")

    ambiental_insurance_policy = fields.Char(string="No. Póliza Seguro Medio Amb.", related="ambiental_insurance_partner_id.ambiental_insurance_policy", 
                                                help="Atributo: PolizaMedAmbiente", size=50, readonly=False)

    transport_insurance_partner_id = fields.Many2one('res.partner', 'Aseguradora Carga',
                                                help="Atributo: AseguraCarga")

    transport_insurance_policy = fields.Char(string="No. Póliza Carga", related="transport_insurance_partner_id.transport_insurance_policy", 
                                                help="Atributo: PolizaCarga", size=50, readonly=False)

    insurance_amount  = fields.Float(string="Prima Seguro",
                                                help="Atributo: PrimaSeguro", digits=(14,2))
                                                
#### Ubicaciones ####

class InvoiceComplementLocationCP(models.Model):
    _name = 'invoice.complement.location.cp'
    _description = 'Ubicaciones Complemento Carta Porte'
    _rec_name = 'location_partner_id'

    def _get_default_station_01(self):
        tipo_estacion_obj = self.env['waybill.tipo.estacion']
        estacion_nacional = tipo_estacion_obj.search([('code','=','01')], limit=1)
        if estacion_nacional:
            return estacion_nacional.id
        
        return False
            
    @api.depends('invoice_origin_id','invoice_destiny_id')
    def _get_default_clave_transporte(self):
        clave_transporte_obj = self.env['waybill.clave.transporte']
        clave_transporte_federal = clave_transporte_obj.search([('code','=','01')], limit=1)
        tipo_transporte_id = False
        for rec in self:
            if rec.invoice_origin_id:
                tipo_transporte_id = rec.invoice_origin_id.tipo_transporte_id.id
            elif rec.invoice_destiny_id:
                tipo_transporte_id = rec.invoice_destiny_id.tipo_transporte_id.id
            else:
                if clave_transporte_federal:
                    tipo_transporte_id = clave_transporte_federal.id
        
            rec.tipo_transporte_id = tipo_transporte_id

    sequence = fields.Integer(default=10)

    tipo_transporte_id = fields.Many2one('waybill.clave.transporte', 'Tipo Transporte',
                                         help="Atributo: ViaEntradaSalida",  compute="_get_default_clave_transporte")

    tipo_transporte_code = fields.Char('Codigo Tipo Transporte (Origen)', related="tipo_transporte_id.code",
                                         help="Atributo: Tipo Complemento")

    invoice_origin_id = fields.Many2one('account.move', 'Ref Factura Origen') 

    invoice_destiny_id = fields.Many2one('account.move', 'Ref Factura Origen')  

    location_type = fields.Selection([
                                        ('Origen','Origen'),
                                        ('Destino','Destino'),

                                     ], string="Tipo Ubicación", help="Atributo: TipoUbicacion")

    id_location = fields.Char('ID Ubicación', size=12)

    location_partner_id = fields.Many2one('res.partner', 'Dirección Ubicación',
                                                help="Atributo: RFC y Atributo: Nombre")

    location_date = fields.Datetime('Fecha Salida/Llegada', 
                                              help="Atributo: FechaHoraSalidaLlegada")


    location_destiny_distance = fields.Float('Distancia recorrida', digits=(14,2),
                                         help="Atributo: DistanciaRecorrida")

    location_destiny_distance_type = fields.Selection([('KM','Kilometros'),('M','Metros')], 'Tipo Distancia Recorrida',
                                                  default="KM")

    location_station_type_id = fields.Many2one('waybill.tipo.estacion', 'Tipo Estacion',
                                                     help="Atributo: TipoEstacion", default=_get_default_station_01)

    location_station_id = fields.Many2one('waybill.complemento.estacion', 'Estacion',
                                                     help="Atributo: NumEstacion y NombreEstacion")


    location_partner_references = fields.Char('Referencias',
                                                    help="Atributo: Referencia")
    
    @api.onchange('location_partner_id')
    def onchange_location_partner_id(self):
        if self.location_partner_id:
            if self.location_type == 'Origen':
                self.id_location = self.location_partner_id.idorigen
            else:
                self.id_location = self.location_partner_id.iddestino
            self.location_partner_references  = self.location_partner_id.l10n_mx_street_reference
            
    @api.onchange('location_type')
    def onchange_location_type(self):
        if self.location_type and not self.id_location:
            if self.location_type == 'Origen':
                self.id_location = 'OR'
            else:
                self.id_location = 'DE'
    

    @api.constrains('id_location')
    def _constraint_location(self):
        for rec in self:
            if rec.id_location:
                _estructura_ubicacion = re.compile('(OR|DE)[0-9]{6}')
                if not _estructura_ubicacion.match(rec.id_location):
                    raise UserError("La estructura de Origen/Destino %s.\n No cumple con la estructura del SAT (OR|DE)[0-9]" % rec.id_location)
        return True

###########################################

class InvoiceLineComplementCP(models.Model):
    _name = 'invoice.line.complement.cp'
    _description = 'Lineas Complemento Carta Porte'
    _rec_name = 'invoice_line_id'

    def _get_default_clave_transporte(self):
        clave_transporte_obj = self.env['waybill.clave.transporte']
        clave_transporte_federal = clave_transporte_obj.search([('code','=','01')], limit=1)
        if clave_transporte_federal:
            return clave_transporte_federal.id
        
        return False

    @api.depends("invoice_id.international_shipping")
    def _get_international_shipping(self):
        for rec in self:
            international_shipping = 'NO'
            if not rec.invoice_id:
                international_shipping = self._context.get('default_international_shipping','NO')
            else:
                international_shipping = rec.invoice_id.international_shipping
            rec.international_shipping = international_shipping
            
    product_id = fields.Many2one('product.product', 'Producto')

    description = fields.Char('Descripción')

    invoice_line_id = fields.Many2one('account.move.line', 'Linea Factura')  

    sat_product_id = fields.Many2one('product.unspsc.code','Producto SAT',domain=[('applies_to', '=', 'product')]) ### Campo LdM E.E.

    quantity = fields.Float('Cantidad', digits=(14,4))

    sat_uom_id = fields.Many2one('product.unspsc.code','UdM SAT', domain=[('applies_to', '=', 'uom')]) ### Campo LdM E.E.

    invoice_id = fields.Many2one('account.move', 'Factura Relacionada')  

    weight_charge = fields.Float('Peso en KG', digits=(14,3))

    dimensions_charge = fields.Char('Dimensiones', size=128)

    clave_stcc_id = fields.Many2one('waybill.producto.stcc', 'Clave STCC')

    hazardous_material = fields.Selection([('Sí','Sí'),('No','No')], string="Material Peligroso", default="No" )
    
    hazardous_key_product_id = fields.Many2one('waybill.materiales.peligrosos', 'Clave Material Peligroso')

    charge_value = fields.Float('Valor Mercancia', digits=(14,3))

    ### Carta Porte 2.0 ###
    # Pedimentos ## Nuevo Objeto
    # Cantidad Transporta ### Nuevo Objeto
    tipo_transporte_id = fields.Many2one('waybill.clave.transporte', 'Tipo Transporte',
                                         help="Atributo: ViaEntradaSalida", default=_get_default_clave_transporte)

    tipo_transporte_code = fields.Char('Codigo Tipo Transporte (Origen)', related="tipo_transporte_id.code",
                                         help="Atributo: Tipo Complemento")

    international_shipping = fields.Selection([('SI','SI'),('NO','NO')], 'Transporte Internacional',
                                             compute="_get_international_shipping")
    
    pedimentos_ids =  fields.One2many('invoice.line.complement.pedimento', 'invoice_line_merchandise_id', 'Pedimentos', copy=True)
    cantidades_ids =  fields.One2many('invoice.line.complement.cantidad.transporta', 'invoice_line_merchandise_id', 'Cantidades Transporta', copy=True)

    tipo_embalaje_id  =  fields.Many2one('waybill.tipo.embalaje', 'Tipo de Embalaje')

    fraccion_arancelaria = fields.Char('Fraccion Arancelaria')
    comercio_ext_uuid = fields.Char('UUID Relacionado Comercio Exterior', help="Indica el UUID de la factura con la cual se relaciona el envio.")

    ### Guias de Identificación ####
    guia_ids = fields.One2many('invoice.line.complement.guia', 'invoice_line_merchandise_id', 'Guias de Identificacion', copy=True)

    ### Materiales Peligrosos 2022 ####
    force_hazardous_pac = fields.Boolean("Enviar Valor MP (PAC)", help="Indica si enviaremos el valor de Material Peligroso 'No'  dentro del XML,\
        este valor puede ser obligatorio con algunos PAC que manejan las claves genericas donde el Material Peligroso es 0,1.")

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            if self.product_id.dimensiones_plg:
                self.dimensions_charge = self.product_id.dimensiones_plg
            if self.product_id.weight:
                self.weight_charge = self.product_id.weight
            if self.product_id.unspsc_code_id:
                ### Campo LdM E.E.
                self.sat_product_id = self.product_id.unspsc_code_id.id
            if self.product_id.clave_stcc_id:
                if self.tipo_transporte_code == '04':
                    self.clave_stcc_id = self.product_id.clave_stcc_id.id
            if self.product_id.uom_id and self.product_id.uom_id.unspsc_code_id:
                ### Campo LdM E.E.
                self.sat_uom_id = self.product_id.uom_id.unspsc_code_id.id
            if self.product_id.tipo_embalaje_id:
                self.tipo_embalaje_id = self.product_id.tipo_embalaje_id.id
            if self.product_id.l10n_mx_edi_tariff_fraction_id:
                self.fraccion_arancelaria = self.product_id.l10n_mx_edi_tariff_fraction_id.code
            if self.product_id.hazardous_material:
                self.hazardous_material = self.product_id.hazardous_material
            if self.product_id.hazardous_key_product_id:
                self.hazardous_key_product_id = self.product_id.hazardous_key_product_id.id
            ### Materiales Peligrosos 2022 ####
            if self.product_id.force_hazardous_pac:
                self.force_hazardous_pac = self.product_id.force_hazardous_pac
            self.description =  self.product_id.name

class InvoiceLineComplementPedimento(models.Model):
    _name = 'invoice.line.complement.pedimento'
    _description = 'Lineas Complemento Pedimentos'
    _rec_name = 'waybill_pedimento'

    invoice_line_merchandise_id = fields.Many2one('invoice.line.complement.cp','Ref. Linea Transporta')

    waybill_pedimento = fields.Char(string="Pedimento", required="1")

class InvoiceLineComplementCantidadTransporta(models.Model):
    _name = 'invoice.line.complement.cantidad.transporta'
    _description = 'Lineas Complemento Cantidad Transporta'
    _rec_name = 'invoice_line_merchandise_id'    

    invoice_line_merchandise_id = fields.Many2one('invoice.line.complement.cp','Ref. Linea Transporta')

    cantidad = fields.Float(string="Cantidad", digits=(14,3))

    idorigen = fields.Char(string="ID Origen", default="OR")

    iddestino = fields.Char(string="ID Destino", default="DE")

    @api.constrains('idorigen')
    def _constraint_idorigen(self):
        for rec in self:
            if rec.idorigen:
                _estructura_ubicacion = re.compile('(OR|DE)[0-9]{6}')
                if not _estructura_ubicacion.match(rec.idorigen):
                    raise UserError("La estructura de Origen/Destino %s.\n No cumple con la estructura del SAT (OR|DE)[0-9]" % rec.idorigen)

        return True

    @api.constrains('iddestino')
    def _constraint_iddestino(self):
        for rec in self:
            if rec.iddestino:
                _estructura_ubicacion = re.compile('(OR|DE)[0-9]{6}')
                if not _estructura_ubicacion.match(rec.iddestino):
                    raise UserError("La estructura de Origen/Destino %s.\n No cumple con la estructura del SAT (OR|DE)[0-9]" % rec.iddestino)

        return True


### Guias de Identificación ####

class InvoiceLineComplementGuia(models.Model):
    _name = 'invoice.line.complement.guia'
    _description = 'Guias Complemento Mercancia Transportada'
    _rec_name = 'numero_guia'    

    invoice_line_merchandise_id = fields.Many2one('invoice.line.complement.cp','Ref. Linea Transporta')

    peso_paquete = fields.Float(string="Peso (KG)", digits=(14,3),
        help="PesoGuiaIdentificacion")

    numero_guia = fields.Char(string="Número",  size=30,
        help="NumeroGuiaIdentificacion")


    descripcion_guia = fields.Char(string="Descripción",  size=256,
        help="DescripGuiaIdentificacion")

    @api.constrains('numero_guia')
    def _constraint_numero_guia(self):
        for rec in self:
            if rec.numero_guia:
                _estructura_ubicacion = re.compile('[^|]{10,30}')
                if not _estructura_ubicacion.match(rec.numero_guia):
                    raise UserError("La guia especificada %s.\n No cumple con la estructura del SAT [^|]{10,30}" % rec.numero_guia)

        return True