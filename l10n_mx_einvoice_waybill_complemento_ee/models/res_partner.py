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


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit ='res.partner'

    
    @api.model
    def _address_fields(self):
        """Returns the list of address fields that are synced from the parent."""
        return super(ResPartner, self)._address_fields() + ['zip_sat_id', 'colonia_sat_id']
    
    def _get_default_country_id(self):
        country_obj = self.env['res.country']
        country = country_obj.search([('code', '=', 'MX'), ], limit=1)
        return country and country.id or False
    
    def _get_base_vat_split(self):
        vat = self.vat
        if vat[:2] == 'MX':
            if len(vat) > 13:
                self.vat_split = self.vat[2:]
            else:
                self.vat_split = self.vat
        else:
            self.vat_split = self.vat

    country_id      = fields.Many2one('res.country', string='Country', ondelete='restrict', default=_get_default_country_id)
    envio_manual_cfdi = fields.Boolean(string="Envío manual del CFDI", 
                                       help="Si marca la casilla entonces las facturas que genere a este cliente NO serán"
                                       "enviadas automáticamente al validar la factura, sino que manualmente tendrá que"
                                       "presionar el Botón de Envío correspondiente. Esto es útil si maneja Addendas o si"
                                       "el CFDI debe ser subido a algún portal del Cliente.")
    

    vat_split =  fields.Char(compute='_get_base_vat_split', string='VAT Split', #store=True,
                    help='Remove the prefix of the country of the VAT') 

    num_reg_trib    =  fields.Char('NumRegIdTrib', size=40, 
                                   help="Atributo requerido para incorporar el número de identificación o registro fiscal"
                                        "del país de residencia para efectos fiscales del receptor del CFDI.\n Obligatorio"
                                        "para Clientes en el Extranjero." )
    
    partner_insurance_number = fields.Char('No. Póliza Seguro')

    l10n_mx_street_reference =  fields.Char('Referencias', size=128, 
                                            help="Atributo requerido para incorporar el número de identificación"
                                                 "o registro fiscal del país de residencia para efectos fiscales"
                                                 "del receptor del CFDI." )

    zip_sat_id      = fields.Many2one('res.country.zip.sat.code', string='CP Sat', 
                                      help='Indica el Codigo del Sat para Comercio Exterior.')
    colonia_sat_id  = fields.Many2one('res.colonia.zip.sat.code', string='Colonia Sat', 
                                      help='Indica el Codigo del Sat para Comercio Exterior.')
    country_code_rel = fields.Char('Codigo Pais', related="country_id.code")

    country_code_rel_2 = fields.Char('Codigo Pais Copy', related="country_id.code")


    codigo_transportista_aereo_id = fields.Many2one('waybill.codigo.transporte.aereo',
                                                 string="Código Transportista Aéreo",
                                                   help="Usado para el Complemento de Carta Porte")

    insurance_policy = fields.Char(string="No. Póliza Seguro",
                                                help="Atributo: PolizaRespCivil", size=50)

    ambiental_insurance_policy = fields.Char(string="No. Póliza Seguro Medio Amb.",
                                                help="Atributo: PolizaMedAmbiente", size=50)

    transport_insurance_policy = fields.Char(string="No. Póliza Carga",
                                                help="Atributo: PolizaCarga", size=50)

    cp_driver_license = fields.Char('Numero de Licencia')

    #### Automatización ####
    idorigen = fields.Char(string="ID Origen", default="OR")

    iddestino = fields.Char(string="ID Destino", default="DE")

    figure_type_id = fields.Many2one('waybill.figura.transporte', 'Tipo Figura',
                                         help="Atributo: Tipo TipoFigura")

    transport_part_ids = fields.Many2many('waybill.parte.transporte', 'partner_figure_part_rel',
                                         'transport_id', 'parte_id', 'Tipos Parte Transporte')


    @api.onchange('zip_sat_id')
    def onchange_zip_sat_id(self):
        if self.zip_sat_id:
            self.zip = self.zip_sat_id.code
            colonia_sat_id = self.env['res.colonia.zip.sat.code'].search([('zip_sat_code','=',self.zip_sat_id.id)])
            if colonia_sat_id:
                self.colonia_sat_id = colonia_sat_id[0].id

    @api.onchange('colonia_sat_id')
    def onchange_colonia_sat_id(self):
        if self.colonia_sat_id:
            self.l10n_mx_edi_colony = self.colonia_sat_id.code
    
    
    