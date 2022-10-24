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

from odoo import api, fields, models, _, tools, release
from datetime import datetime
from datetime import datetime, date
from odoo.exceptions import UserError, RedirectWarning, ValidationError

## Manejo de Fechas y Horas ##
from pytz import timezone
import pytz

import re

import logging
_logger = logging.getLogger(__name__)

import re

### Gestión del Excel ####

import xlwt
from io import BytesIO
import base64

from itertools import zip_longest

##########################

##### Materiales Peligrosos #####
from . import materiales_peligrosos ## Clase con Codigos MP
# instance_class_hazardous = materiales_peligrosos.HazardousFCodes()
# hazardous_code = instance_class_hazardous.is_hazardous_material(str(code_result))
#################################

#### Librerias LdM E.E. ###
from lxml import etree
from xml.dom import minidom
from xml.dom.minidom import parse, parseString

from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
import base64
from io import BytesIO
from lxml.objectify import fromstring

### Reemplazo de las Cadenas XSLT Para Cadena
CFDI_TEMPLATE_33 = 'l10n_mx_edi_40.cfdiv40'
CFDI_XSLT_CADENA_TFD = 'l10n_mx_einvoice_waybill_complemento_ee/SAT/cadenaoriginal_4_0/cadenaoriginal_TFD_1_1.xslt'
CFDI_XSLT_CADENA = 'l10n_mx_einvoice_waybill_complemento_ee/SAT/cadenaoriginal_4_0/cadenaoriginal_4_0.xslt'

def create_list_html(array):
    '''Convert an array of string to a html list.
    :param array: A list of strings
    :return: an empty string if not array, an html list otherwise.
    '''
    if not array:
        return ''
    msg = ''
    for item in array:
        msg += '<li>' + item + '</li>'
    return '<ul>' + msg + '</ul>'


# Cambiar el error
msg2 = "Contacta a tu administrador de Sistema o contactanos info@argil.mx"

#### Metodos de la LdM E.E. ####

class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'
    
    def _l10n_mx_edi_export_invoice_cfdi(self, invoice):
        self.ensure_one()
        if invoice.cfdi_complemento != 'carta_porte':
            return super(AccountEdiFormat, self)._l10n_mx_edi_export_invoice_cfdi(invoice)

        # == CFDI values ==
        cfdi_values = self._l10n_mx_edi_get_invoice_cfdi_values(invoice)
        if cfdi_values.get('document_type', '') == 'T':
            ### Integración CFDI Traslado ###
            _logger.info("\n########## Si es un CFDI de Traslado no lleva tipo de cambio y la moneda es XXX >>>>>>>> ")
            cfdi_values.update({
                         'currency_name': 'XXX',
                         'currency_conversion_rate': False,
                       })

        # == Generate the CFDI ==
        cfdi = self.env.ref('l10n_mx_edi_40.cfdiv40')._render(cfdi_values)

        #### Trucando el CFDI XML para corregir el error en la moneda XXX el 0.0 por 0 ya que Qweb lo borra ###
        ### CFDI Traslado ####
        if cfdi_values.get('document_type', '') == 'T':
            _logger.info("\n########## Si es un CFDI de Traslado eliminamos el Total y SubTotal por el error en decimales. >>>>>>>> ")
            cfdi_minidom = minidom.parseString(cfdi)
            if cfdi_minidom.getElementsByTagName('cfdi:Comprobante'):
                subnode_cfdi_comprobante = cfdi_minidom.getElementsByTagName('cfdi:Comprobante')[0]
                ### Obtenemos los Totales para verificar en modo Debug ####
                cfdi_minidom_total = subnode_cfdi_comprobante.getAttribute('Total') if subnode_cfdi_comprobante.getAttribute('Total') else ''
                cfdi_minidom_subtotal = subnode_cfdi_comprobante.getAttribute('SubTotal') if subnode_cfdi_comprobante.getAttribute('SubTotal') else ''
                ### Eliminamos los Totales ####
                subnode_cfdi_comprobante.setAttribute('Total', str(0))
                subnode_cfdi_comprobante.setAttribute('SubTotal', str(0))

                ######## Agregamos los Prefijos de Carta Porte en la Cabecera Principal #########
                subnode_cfdi_comprobante.setAttribute('xmlns:cartaporte20', "http://www.sat.gob.mx/CartaPorte20")
                subnode_cfdi_comprobante.setAttribute('xsi:schemaLocation', "http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd http://www.sat.gob.mx/CartaPorte20 http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte20.xsd")

                #### Validando el Valor de la Mercancia o corrigiendo el nodo necesario valor 0.0 ####
                if cfdi_minidom.getElementsByTagName('cartaporte20:Mercancia'):
                    for node_mercancia in cfdi_minidom.getElementsByTagName('cartaporte20:Mercancia'):
                        if not node_mercancia.getAttribute('ValorMercancia'):
                            node_mercancia.setAttribute('ValorMercancia', str(0.0))

                #### Eliminando el Namespace Secundario de Carta Porte ####
                if cfdi_minidom.getElementsByTagName('cartaporte20:CartaPorte'):
                    subnode_cfdi_complemento_carta_porte = cfdi_minidom.getElementsByTagName('cartaporte20:CartaPorte')[0]                    
                    subnode_cfdi_complemento_carta_porte.removeAttribute('xsi:schemaLocation')
                    # subnode_cfdi_complemento_carta_porte.removeAttribute('xmlns:cartaporte20')

                cfdi_custom = cfdi_minidom.toxml('UTF-8')
                cfdi = cfdi_custom

        else:
            #### Validando el Valor de la Mercancia o corrigiendo el nodo necesario valor 0.0 ####
            cfdi_minidom = minidom.parseString(cfdi)
            if cfdi_minidom.getElementsByTagName('cartaporte20:Mercancia'):
                for node_mercancia in cfdi_minidom.getElementsByTagName('cartaporte20:Mercancia'):
                    if not node_mercancia.getAttribute('ValorMercancia'):
                        node_mercancia.setAttribute('ValorMercancia', str(0.0))
            ######## Agregamos los Prefijos de Carta Porte en la Cabecera Principal #########       
            subnode_cfdi_comprobante = cfdi_minidom.getElementsByTagName('cfdi:Comprobante')[0]
            ### Agregamos el Atributo de la Carta porte Prefix ####
            subnode_cfdi_comprobante.setAttribute('xmlns:cartaporte20', "http://www.sat.gob.mx/CartaPorte20")
            subnode_cfdi_comprobante.setAttribute('xsi:schemaLocation', "http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd http://www.sat.gob.mx/CartaPorte20 http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte20.xsd")

            #### Eliminando el Namespace Secundario de Carta Porte ####
            if cfdi_minidom.getElementsByTagName('cartaporte20:CartaPorte'):
                subnode_cfdi_complemento_carta_porte = cfdi_minidom.getElementsByTagName('cartaporte20:CartaPorte')[0]                    
                subnode_cfdi_complemento_carta_porte.removeAttribute('xsi:schemaLocation')
                # subnode_cfdi_complemento_carta_porte.removeAttribute('xmlns:cartaporte20')
                
            cfdi_custom = cfdi_minidom.toxml('UTF-8')
            cfdi = cfdi_custom
            
        #### Proceso Normal ####
        decoded_cfdi_values = invoice._l10n_mx_edi_decode_cfdi(cfdi_data=cfdi)
        cfdi_cadena_crypted = cfdi_values['certificate'].sudo().get_encrypted_cadena(decoded_cfdi_values['cadena'])
        decoded_cfdi_values['cfdi_node'].attrib['Sello'] = cfdi_cadena_crypted

        # == Optional check using the XSD ==
        # xsd_attachment = self.env.ref('l10n_mx_edi.xsd_cached_cfdv33_xsd', False)
        # xsd_datas = base64.b64decode(xsd_attachment.datas) if xsd_attachment else None

        # if xsd_datas:
        #     try:
        #         with BytesIO(xsd_datas) as xsd:
        #             _check_with_xsd(decoded_cfdi_values['cfdi_node'], xsd)
        #     except (IOError, ValueError):
        #         _logger.info(_('The xsd file to validate the XML structure was not found'))
        #     except Exception as e:
        #         return {'errors': str(e).split('\\n')}
        cfdi_previo = etree.tostring(decoded_cfdi_values['cfdi_node'], pretty_print=True, xml_declaration=True, encoding='UTF-8')
        cfdi_previo_debug = str(cfdi_previo).replace('\n','')
        _logger.info("\nCFDI Precio con Complemento Carta Porte:\n%s" % cfdi_previo_debug)
        return {
            'cfdi_str': cfdi_previo,
        }


class AccountInvoice(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    
    def _check_validations_complement_waybill(self):
        _logger.info("\n########## Realizamos algunas validaciones sobre el complemento de Carta Porte >>>>>>>> ")
        if self.cfdi_complemento == 'carta_porte':
            if self.tipo_transporte_id.code == '01':
                if not self.insurance_ids:
                    raise UserError("No se tiene identificada la información para el Seguro dentro del complemento de Autotransporte.")
                if not self.location_origin_ids or not self.location_destiny_ids:
                    raise UserError("El complemento debe  contener al menos un Origen y un Destino.")
            #### Si no tiene CP Forzamos la Escritura ####
            if self.company_id.partner_id.zip_sat_id and not self.company_id.partner_id.zip:
                self.company_id.partner_id.zip = self.company_id.partner_id.zip_sat_id.code

            if self.company_id.partner_id.commercial_partner_id.zip_sat_id and not self.company_id.partner_id.commercial_partner_id.zip:
                self.company_id.partner_id.commercial_partner_id.zip = self.company_id.partner_id.commercial_partner_id.zip_sat_id.code

            if self.partner_id.zip_sat_id and not self.partner_id.zip:
                self.partner_id.zip = self.partner_id.zip_sat_id.code
            
            #####  Validaciones Direcciones ####
            ################
            #### Origen ####
            ################

            for location_inst in self.location_origin_ids:
                tz = self.env.user.partner_id.tz or 'Mexico/General'
                location_partner_select = location_inst.location_partner_id

                loc_partner_state = ""
                if location_partner_select.state_id and location_partner_select.state_id.code:
                    loc_partner_state = location_partner_select.state_id.code
                if not loc_partner_state:
                    raise UserError("El estado ingresado en la direccion no cuenta con el Codigo SAT.")

                loc_partner_country = ""
                if location_partner_select.country_id and location_partner_select.country_id.l10n_mx_edi_code:
                    loc_partner_country = location_partner_select.country_id.l10n_mx_edi_code
                if not loc_partner_country:
                    raise UserError("El pais ingresado en la direccion no cuenta con el Codigo SAT.")

                loc_partner_zip = ""
                if location_partner_select.zip_sat_id:
                    loc_partner_zip = location_partner_select.zip_sat_id.code
                if not loc_partner_zip:
                    loc_partner_zip = location_partner_select.zip
                if not loc_partner_zip:
                    raise UserError("La direccion no cuenta con el Codigo Postal.")
                    
            ################
            ### Destino ####
            ################

            for location_dest in self.location_destiny_ids:
                tz = self.env.user.partner_id.tz or 'Mexico/General'
                location_partner_select = location_dest.location_partner_id

                loc_partner_state = ""
                if location_partner_select.state_id and location_partner_select.state_id.code:
                    loc_partner_state = location_partner_select.state_id.code
                if not loc_partner_state:
                    raise UserError("El estado ingresado en la direccion no cuenta con el Codigo SAT.")

                loc_partner_country = ""
                if location_partner_select.country_id and location_partner_select.country_id.l10n_mx_edi_code:
                    loc_partner_country = location_partner_select.country_id.l10n_mx_edi_code
                if not loc_partner_country:
                    raise UserError("El pais ingresado en la direccion no cuenta con el Codigo SAT.")

                loc_partner_zip = ""
                if location_partner_select.zip_sat_id:
                    loc_partner_zip = location_partner_select.zip_sat_id.code
                if not loc_partner_zip:
                    loc_partner_zip = location_partner_select.zip
                if not loc_partner_zip:
                    raise UserError("La direccion no cuenta con el Codigo Postal.")        
            
            #### Validacion de las Claves para el Complemento ####
            for line in self.invoice_line_complement_cp_ids:
                sat_product_id = line.sat_product_id
                if not sat_product_id:
                    raise UserError(_("Error!\nEl producto:\n %s \nNo cuenta con la Clave de Producto/Servicio del SAT." % line.sat_product_id.code))

                sat_uom_id = line.sat_uom_id
                if not sat_uom_id:
                    raise UserError(_("Error!\nLa linea de factura:\n %s \nNo cuenta con la Clave de Unidad de Medida SAT." % line.sat_product_id.code))

                if not line.weight_charge:
                    raise UserError(_("Error!\nLa linea de factura:\n %s \nNo cuenta con el Peso en KG." % line.product_id.name))
            
            ### Validacion del Operador ####

            #### Validando las Figuras de Transporte ####
            for driver in self.driver_figure_ids:
                driver_cp_id = driver.partner_id
                if not driver_cp_id.country_id:
                    raise UserError("El Operador %s no cuenta con información del PAIS." % driver_cp_id.name) 
                if not driver_cp_id.country_id.l10n_mx_edi_code:
                    raise UserError("El Pais %s no cuenta con la clave SAT." % driver_cp_id.country_id.name) 
                if driver.add_address and self.transport_document_cfdi == False:          
                    state_info  = ""
                    country_code = ""
                    zip_code = ""

                    if driver_cp_id.state_id and driver_cp_id.state_id.code:
                        state_info = driver_cp_id.state_id.code
                    if not state_info:
                        raise UserError("En la dirección del Operador %s el estado ingresado en la direccion no cuenta con el Codigo SAT." % driver_cp_id.name)

                    zip_code = ""
                    if driver_cp_id.zip_sat_id:
                        zip_code = driver_cp_id.zip_sat_id.code
                    if not zip_code:
                        zip_code = driver_cp_id.zip
                    if not zip_code:
                        raise UserError("En la dirección del Operador %s no cuenta con el Codigo Postal." % driver_cp_id.name)


            for figure in self.other_figure_ids:
                figure_partner = figure.partner_id
                if not figure_partner.country_id:
                    raise UserError("La Figura %s no cuenta con información del PAIS." % figure_partner.name) 
                if not figure_partner.country_id.l10n_mx_edi_code:
                    raise UserError("El Pais %s no cuenta con la clave SAT." % figure_partner.country_id.name) 
                 
                if figure.add_address and self.transport_document_cfdi == False:            
                    state_info  = ""
                    country_code = ""
                    zip_code = ""

                    state_info = ""
                    if figure_partner.state_id and figure_partner.state_id.code:
                        state_info = figure_partner.state_id.code
                    if not state_info:
                        raise UserError("En la dirección de la Figura %s el estado ingresado en la direccion no cuenta con el Codigo SAT." % figure_partner.name)

                    zip_code = ""
                    if figure_partner.zip_sat_id:
                        zip_code = figure_partner.zip_sat_id.code
                    if not zip_code:
                        zip_code = figure_partner.zip
                    if not zip_code:
                        raise UserError("En la dirección de la Figura %s no cuenta con el Codigo Postal." % figure_partner.name)

            if self.tipo_transporte_id and self.tipo_transporte_id.code == '01':
                ### Validación ####
                ### Validando que tenga Mercancias Transportadas ###
                if not self.invoice_line_complement_cp_ids:
                    raise UserError("Para el complemento de Carta Porte es necesario indicar las Mercancias Transportadas.")
                else:
                    #### Validando el nodo de Dimensiones y atributos de Mercancias ###
                    for merchandise in self.invoice_line_complement_cp_ids:
                        dimensions_charge = merchandise.dimensions_charge
                        if dimensions_charge:
                            _merchandise_re = re.compile('([0-9]{1,3}[/]){2}([0-9]{1,3})(cm|plg)')
                            if not _merchandise_re.match(dimensions_charge):
                                raise UserError(_('Verifique su información\n\nLas dimensiones establecidas "%s" \
                                     no se apega a los lineamientos del SAT.\nEjemplo: 30/20/10plg\nExpresión Regular: [0-9]{2}[/]{1}[0-9]{2}[/]{1}[0-9]{2}cm|[0-9]{2}[/]{1}[0-9]{2}[/]{1}[0-9]{2}plg') % (dimensions_charge))

                ### Si el CFDI es de Tipo Ingreso debe tener información de retenciones y traslados ####
                if self.type == 'out_invoice' and self.amount_total > 1.0:
                    tax_ret = False
                    tax_trasl = False
                    for taxline in self.tax_line_ids:
                        if taxline.amount_total < 0.0:
                            tax_ret = True
                        elif taxline.amount_total > 0.0:
                            tax_trasl = True
                    
                    customer_country_code = self.partner_id.country_id.code if self.partner_id.country_id else ""

                    if not tax_ret:
                        if customer_country_code == 'MX':
                            raise UserError("Cuando se utiliza el complemento de Carta Porte para Transporte Federal \
                                             en un comprobante de tipo Ingreso (I), \
                                             el nodo de Impuestos Retenidos no puede estar vacio.")
                    if not tax_trasl:
                        if customer_country_code == 'MX':
                            raise UserError("Cuando se utiliza el complemento de Carta Porte para Transporte Federal \
                                             en un comprobante de tipo Ingreso (I), \
                                             el nodo de Impuestos Trasladados no puede estar vacio.")
        return True
    
    #### Metodos de la LdM E.E. ####
    def _l10n_mx_edi_decode_cfdi(self, cfdi_data=None):
        ''' Helper to extract relevant data from the CFDI to be used, for example, when printing the invoice.
        :param cfdi_data:   The optional cfdi data.
        :return:            A python dictionary.
        '''
        self.ensure_one()

        def get_node(cfdi_node, attribute, namespaces):
            if hasattr(cfdi_node, 'Complemento'):
                node = cfdi_node.Complemento.xpath(attribute, namespaces=namespaces)
                return node[0] if node else None
            else:
                return None

        def get_cadena(cfdi_node, template):
            if cfdi_node is None:
                return None
            cadena_root = etree.parse(tools.file_open(template))
            return str(etree.XSLT(cadena_root)(cfdi_node))

        # Find a signed cfdi.
        if not cfdi_data:
            signed_edi = self._get_l10n_mx_edi_signed_edi_document()
            if signed_edi:
                cfdi_data = base64.decodebytes(signed_edi.attachment_id.with_context(bin_size=False).datas)

        # Nothing to decode.
        if not cfdi_data:
            return {}

        cfdi_node = fromstring(cfdi_data)
        tfd_node = get_node(
            cfdi_node,
            'tfd:TimbreFiscalDigital[1]',
            {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'},
        )

        cadena = tfd_node is not None and get_cadena(tfd_node, self._l10n_mx_edi_get_cadena_xslts()[0]) or get_cadena(cfdi_node, self._l10n_mx_edi_get_cadena_xslts()[1])

        res = {
            'uuid': ({} if tfd_node is None else tfd_node).get('UUID'),
            'supplier_rfc': cfdi_node.Emisor.get('Rfc', cfdi_node.Emisor.get('rfc')),
            'customer_rfc': cfdi_node.Receptor.get('Rfc', cfdi_node.Receptor.get('rfc')),
            'amount_total': cfdi_node.get('Total', cfdi_node.get('total')),
            'cfdi_node': cfdi_node,
            'usage': cfdi_node.Receptor.get('UsoCFDI'),
            'payment_method': cfdi_node.get('formaDePago', cfdi_node.get('MetodoPago')),
            'bank_account': cfdi_node.get('NumCtaPago'),
            'sello': cfdi_node.get('sello', cfdi_node.get('Sello', 'No identificado')),
            'sello_sat': tfd_node is not None and tfd_node.get('selloSAT', tfd_node.get('SelloSAT', 'No identificado')),
            'cadena': cadena,
            'certificate_number': cfdi_node.get('noCertificado', cfdi_node.get('NoCertificado')),
            'certificate_sat_number': tfd_node is not None and tfd_node.get('NoCertificadoSAT'),
            'expedition': cfdi_node.get('LugarExpedicion'),
            'fiscal_regime': cfdi_node.Emisor.get('RegimenFiscal', ''),
            'emission_date_str': cfdi_node.get('fecha', cfdi_node.get('Fecha', '')).replace('T', ' '),
            'stamp_date': tfd_node is not None and tfd_node.get('FechaTimbrado', '').replace('T', ' '),
        }
        # raise UserError("AQUI >>> ")
        return res

    #### Sobreescribimos la cabecera para el Complemento de Carta Porte y Algunas Validaciones ####
    def _get_facturae_invoice_dict_data(self):
        self.ensure_one()
        ### Validaciónes de Carta Porte ####
        self._check_validations_complement_waybill()

        invoice_data_parents = {}

        if self.cfdi_complemento == 'carta_porte':
            invoice_data_parents['cfdi:Comprobante'].update(
                    {'xmlns:cfdi'   : "http://www.sat.gob.mx/cfd/4",
                     'xmlns:xs'     : "http://www.w3.org/2001/XMLSchema",
                     'xmlns:xsi'    : "http://www.w3.org/2001/XMLSchema-instance",
                     'xmlns:cartaporte20': "http://www.sat.gob.mx/CartaPorte20",
                     'xsi:schemaLocation': "http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd http://www.sat.gob.mx/CartaPorte20 http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte20.xsd",
                     'Version': "4.0", })
        return invoice_data_parents


    #### Metodo para insertar los Nodos de Ubicaciones ####
    def _get_complement_waybill_locations(self, ):
        #### Nodo Principal ####
        locations_dict = {'cartaporte20:Ubicaciones': []}
        ################
        #### Origen ####
        ################

        for location_inst in self.location_origin_ids:
            tz = self.env.user.partner_id.tz or 'Mexico/General'
            location_partner_select = location_inst.location_partner_id

            loc_partner_state = ""
            if location_partner_select.state_id and location_partner_select.state_id.code:
                loc_partner_state = location_partner_select.state_id.code

            loc_partner_country = ""
            if location_partner_select.country_id and location_partner_select.country_id.l10n_mx_edi_code:
                loc_partner_country = location_partner_select.country_id.l10n_mx_edi_code

            loc_partner_zip = ""
            if location_partner_select.zip_sat_id:
                loc_partner_zip = location_partner_select.zip_sat_id.code
            if not loc_partner_zip:
                loc_partner_zip = location_partner_select.zip

            loc_partner_info = {
                                            'Estado': loc_partner_state or False,
                                            'Pais': loc_partner_country or False,
                                            'CodigoPostal': loc_partner_zip or False,
                                            'Referencia': location_inst.location_partner_references or False,
                                           }

            #### Dirección/Domicilio ####
            loc_partner_street = location_partner_select.street_name
            if  loc_partner_street:
                loc_partner_info.update({
                                            'Calle': loc_partner_street,   
                                        })
            else:
                loc_partner_info.update({
                                            'Calle': False,   
                                        })

            loc_partner_ext_number = location_partner_select.street_number
            if loc_partner_ext_number:
                loc_partner_info.update({
                                            'NumeroExterior': loc_partner_ext_number,   
                                        })
            else:
                loc_partner_info.update({
                                            'NumeroExterior': False,   
                                        })

            loc_partner_int_number = location_partner_select.street_number2
            if loc_partner_int_number:
                loc_partner_info.update({
                                            'NumeroInterior': loc_partner_int_number,   
                                        })
            else:
                loc_partner_info.update({
                                            'NumeroInterior': False,   
                                        })

            loc_partner_colony = location_partner_select.colonia_sat_id.code if location_partner_select.colonia_sat_id else ""
            if loc_partner_colony:
                loc_partner_colony =  self.add_padding_char(4,loc_partner_colony,'0','left')
                loc_partner_info.update({
                                            'Colonia': loc_partner_colony,   
                                        })
            else:
                loc_partner_info.update({
                                            'Colonia': False,   
                                        })

            loc_partner_locality = location_partner_select.l10n_mx_edi_locality_id.code if location_partner_select.l10n_mx_edi_locality_id else ""
            if loc_partner_locality:
                loc_partner_info.update({
                                            'Localidad': loc_partner_locality,   
                                        })
            else:
                loc_partner_info.update({
                                            'Localidad': False,   
                                        })

            loc_partner_township = location_partner_select.zip_sat_id.township_sat_code.code if location_partner_select.zip_sat_id.township_sat_code else ""
            if loc_partner_township:
                loc_partner_info.update({
                                            'Municipio': loc_partner_township,   
                                        })
            else:
                loc_partner_info.update({
                                            'Municipio': False,   
                                        })

            if location_inst.location_partner_references:
                loc_partner_info.update({
                                            'Referencia': location_inst.location_partner_references,
                                        })
            else:
                loc_partner_info.update({
                                            'Referencia': False,
                                        })

            loc_partner_vat = location_partner_select.vat
            if not loc_partner_vat:
                if location_partner_select.parent_id:
                    loc_partner_vat = location_partner_select.parent_id.vat
            num_reg_trib = location_partner_select.num_reg_trib
            if not num_reg_trib:
                if location_partner_select.parent_id:
                    num_reg_trib = location_partner_select.parent_id.num_reg_trib
            loc_partner_name = location_partner_select.name

            location_date_tz = location_inst.location_date and self.get_complement_server_to_local_timestamp(
                    location_inst.location_date, tz) or False

            if location_date_tz:
                location_date_tz = str(location_date_tz)[0:19]
                location_date_tz.replace(' ','T')
                date_loc = location_date_tz.split(' ')
                date_loc_tz = date_loc[0]+'T'+date_loc[1]
            else:
                date_loc_tz = ""

            loc_address_data = {
                                    'TipoUbicacion': location_inst.location_type if location_inst.location_type else False,
                                    'RFCRemitenteDestinatario': loc_partner_vat if loc_partner_vat else False,
                                    'NombreRemitenteDestinatario':  loc_partner_name if loc_partner_name else False,
                                    'FechaHoraSalidaLlegada': date_loc_tz if date_loc_tz else False,
                              }

            if location_inst.id_location:
                loc_address_data.update({
                                                'IDUbicacion': location_inst.id_location,
                                            })
            else:
                loc_address_data.update({
                                                'IDUbicacion': False,
                                            })

            if loc_partner_country != 'MEX' and num_reg_trib:
                loc_address_data.update({
                                                'NumRegIdTrib': num_reg_trib,
                                                'ResidenciaFiscal': loc_partner_country,
                                            })
            else:
                loc_address_data.update({
                                                'NumRegIdTrib': False,
                                                'ResidenciaFiscal': False,
                                            })

            # NumEstacion
            # NombreEstacion
            if location_inst.tipo_transporte_code in ('03', '04') and location_inst.location_station_id:
                loc_address_data.update({
                                                'NumEstacion': location_inst.location_station_id.code_identification,
                                                'NombreEstacion': location_inst.location_station_id.name,
                                            })
            else:
                loc_address_data.update({
                                                'NumEstacion': False,
                                                'NombreEstacion': False,
                                            })

            if location_inst.tipo_transporte_code != '01' and location_inst.location_station_type_id:
                loc_address_data.update({
                                                'TipoEstacion': location_inst.location_station_type_id.code,
                                            })
            else:
                loc_address_data.update({
                                                'TipoEstacion': False,
                                            })

            if location_inst.location_type == 'Destino':
                location_destiny_distance  = location_inst.location_destiny_distance
                loc_address_data.update({
                                                'DistanciaRecorrida':  "%.2f" % (location_destiny_distance),
                                            })
            else:
                loc_address_data.update({
                                                'DistanciaRecorrida':  False,
                                            })

            if loc_partner_info:
                loc_address_data.update({
                                                     'cartaporte20:Domicilio': loc_partner_info,
                                                   })

            #### Agremamos el Nodo de Ubicacion en el Nodo Principal ####
            locations_dict['cartaporte20:Ubicaciones'].append(
                    {
                        'cartaporte20:Ubicacion': loc_address_data,
                        
                    }
                    )

        ################
        ### Destino ####
        ################

        for location_dest in self.location_destiny_ids:
            tz = self.env.user.partner_id.tz or 'Mexico/General'
            location_partner_select = location_dest.location_partner_id

            loc_partner_state = ""
            if location_partner_select.state_id and location_partner_select.state_id.code:
                loc_partner_state = location_partner_select.state_id.code

            loc_partner_country = ""
            if location_partner_select.country_id and location_partner_select.country_id.l10n_mx_edi_code:
                loc_partner_country = location_partner_select.country_id.l10n_mx_edi_code

            loc_partner_zip = ""
            if location_partner_select.zip_sat_id:
                loc_partner_zip = location_partner_select.zip_sat_id.code
            if not loc_partner_zip:
                loc_partner_zip = location_partner_select.zip

            loc_partner_info = {
                                            'Estado': loc_partner_state or False,
                                            'Pais': loc_partner_country or False,
                                            'CodigoPostal': loc_partner_zip or False,
                                            'Referencia': location_dest.location_partner_references or False,
                                           }

            #### Dirección/Domicilio ####
            loc_partner_street = location_partner_select.street_name
            if  loc_partner_street:
                loc_partner_info.update({
                                            'Calle': loc_partner_street,   
                                        })
            else:
                loc_partner_info.update({
                                            'Calle': False,   
                                        })

            loc_partner_ext_number = location_partner_select.street_number
            if loc_partner_ext_number:
                loc_partner_info.update({
                                            'NumeroExterior': loc_partner_ext_number,   
                                        })
            else:
                loc_partner_info.update({
                                            'NumeroExterior': False,   
                                        })

            loc_partner_int_number = location_partner_select.street_number2
            if loc_partner_int_number:
                loc_partner_info.update({
                                            'NumeroInterior': loc_partner_int_number,   
                                        })
            else:
                loc_partner_info.update({
                                            'NumeroInterior': False,   
                                        })

            loc_partner_colony = location_partner_select.colonia_sat_id.code if location_partner_select.colonia_sat_id else ""
            if loc_partner_colony:
                loc_partner_colony =  self.add_padding_char(4,loc_partner_colony,'0','left')
                loc_partner_info.update({
                                            'Colonia': loc_partner_colony,   
                                        })
            else:
                loc_partner_info.update({
                                            'Colonia': False,   
                                        })

            loc_partner_locality = location_partner_select.l10n_mx_edi_locality_id.code if location_partner_select.l10n_mx_edi_locality_id else ""
            if loc_partner_locality:
                loc_partner_info.update({
                                            'Localidad': loc_partner_locality,   
                                        })
            else:
                loc_partner_info.update({
                                            'Localidad': False,   
                                        })

            loc_partner_township = location_partner_select.zip_sat_id.township_sat_code.code if location_partner_select.zip_sat_id.township_sat_code else ""
            if loc_partner_township:
                loc_partner_info.update({
                                            'Municipio': loc_partner_township,   
                                        })
            else:
                loc_partner_info.update({
                                            'Municipio': False,   
                                        })

            if location_dest.location_partner_references:
                loc_partner_info.update({
                                            'Referencia': location_dest.location_partner_references,
                                        })
            else:
                loc_partner_info.update({
                                            'Referencia': False,
                                        })

            loc_partner_vat = location_partner_select.vat
            if not loc_partner_vat:
                if location_partner_select.parent_id:
                    loc_partner_vat = location_partner_select.parent_id.vat
            num_reg_trib = location_partner_select.num_reg_trib
            if not num_reg_trib:
                if location_partner_select.parent_id:
                    num_reg_trib = location_partner_select.parent_id.num_reg_trib
            loc_partner_name = location_partner_select.name

            location_date_tz = location_dest.location_date and self.get_complement_server_to_local_timestamp(
                    location_dest.location_date, tz) or False

            if location_date_tz:
                location_date_tz = str(location_date_tz)[0:19]
                location_date_tz.replace(' ','T')
                date_loc = location_date_tz.split(' ')
                date_loc_tz = date_loc[0]+'T'+date_loc[1]
            else:
                date_loc_tz = ""

            loc_address_data = {
                                    'TipoUbicacion': location_dest.location_type or False,
                                    'RFCRemitenteDestinatario': loc_partner_vat or False,
                                    'NombreRemitenteDestinatario':  loc_partner_name or False,
                                    'FechaHoraSalidaLlegada': date_loc_tz or False,
                              }

            if location_dest.id_location:
                loc_address_data.update({
                                                'IDUbicacion': location_dest.id_location,
                                            })
            else:
                loc_address_data.update({
                                                'IDUbicacion': False,
                                            })

            if loc_partner_country != 'MEX' and num_reg_trib:
                loc_address_data.update({
                                                'NumRegIdTrib': num_reg_trib,
                                                'ResidenciaFiscal': loc_partner_country,
                                            })
            else:
                loc_address_data.update({
                                                'NumRegIdTrib': False,
                                                'ResidenciaFiscal': False,
                                            })
            # NumEstacion
            # NombreEstacion
            if location_dest.tipo_transporte_code in ('03', '04') and location_dest.location_station_id:
                loc_address_data.update({
                                                'NumEstacion': location_dest.location_station_id.code_identification,
                                                'NombreEstacion': location_dest.location_station_id.name,
                                            })
            else:
                loc_address_data.update({
                                                'NumEstacion': False,
                                                'NombreEstacion': False,
                                            })

            if location_dest.tipo_transporte_code != '01' and location_dest.location_station_type_id:
                loc_address_data.update({
                                                'TipoEstacion': location_dest.location_station_type_id.code,
                                            })
            else:
                loc_address_data.update({
                                                'TipoEstacion': False,
                                            })

            if location_dest.location_type == 'Destino':
                location_destiny_distance  = location_dest.location_destiny_distance
                loc_address_data.update({
                                                'DistanciaRecorrida':  "%.2f" % (location_destiny_distance),
                                            })
            else:
                loc_address_data.update({
                                                'DistanciaRecorrida': False,
                                            })

            if loc_partner_info:
                loc_address_data.update({
                                                     'cartaporte20:Domicilio': loc_partner_info,
                                                   })

            #### Agremamos el Nodo de Ubicacion en el Nodo Principal ####
            locations_dict['cartaporte20:Ubicaciones'].append(
                    {
                        'cartaporte20:Ubicacion': loc_address_data,
                        
                    }
                    )

        return locations_dict


    #### Metodo para insertar los Nodos de Mercancias ####
    def _get_complement_waybill_items(self, ):
        _logger.info("\n##### Insertando los nodos para Mercancias >>>>>>>> ")
        mercancias_data = {
                            'NumTotalMercancias': len(self.invoice_line_complement_cp_ids.ids),
                          }
        if self.waybill_tasc_charges > 0.0:
            mercancias_data.update({
                                    'CargoPorTasacion': "%.3f" % (self.waybill_tasc_charges),
                                    })
        else:
            mercancias_data.update({
                                    'CargoPorTasacion': False,
                                    })

        if self.weight_charge_total > 0.0:
            mercancias_data.update({
                                    'PesoNetoTotal': "%.3f" % (self.weight_charge_total),
                                    })
        else:
            mercancias_data.update({
                                    'PesoNetoTotal': False,
                                    })

        if self.weight_charge_gross_total > 0.0:
            mercancias_data.update({
                                    'PesoBrutoTotal': "%.3f" % (self.weight_charge_gross_total),
                                    })
        else:
            mercancias_data.update({
                                    'PesoBrutoTotal': False,
                                    })

        if self.uom_weight_id:
            mercancias_data.update({
                                    'UnidadPeso': self.uom_weight_id.code,
                                    })
        else:
            mercancias_data.update({
                                    'UnidadPeso': False,
                                    })

        mercancias_data.update({'cartaporte20:Mercancias': []})
        #### Nodos Mercancia ####
        number_of_items = len(self.invoice_line_complement_cp_ids.ids)
        for line in self.invoice_line_complement_cp_ids:
            ### Como debe quedar el Nodo ###
            sat_product_id = line.sat_product_id
            clave_stcc_id = line.clave_stcc_id
            sat_uom_id = line.sat_uom_id
            merchandise_data = {
                                    'BienesTransp': sat_product_id.code if sat_product_id else False,
                                    'ClaveSTCC': clave_stcc_id.code if clave_stcc_id else False,
                                    'Descripcion': line.description,
                                    'Cantidad': "%.6f" % (line.quantity),
                                    'ClaveUnidad': sat_uom_id.code if sat_uom_id else False,
                                    'Unidad': sat_uom_id.name if sat_uom_id else False,
                                    # 'FraccionArancelaria' : line.product_id.l10n_mx_edi_tariff_fraction_id.code,
                                }
            if line.tipo_transporte_code != '04':
                merchandise_data.update({
                                    'ClaveSTCC': False,
                                })

            if line.dimensions_charge:
                merchandise_data.update({
                                            'Dimensiones': line.dimensions_charge,
                                        })
            else:
                merchandise_data.update({
                                            'Dimensiones': False,
                                        })

            if line.weight_charge:
                merchandise_data.update({
                                            'PesoEnKg': "%.3f" % (line.weight_charge * line.quantity),
                                        })
            else:
                merchandise_data.update({
                                            'PesoEnKg': False,
                                        })
            
            ######### Materiales Peligrosos ########
            instance_class_hazardous = materiales_peligrosos.HazardousFCodes()
            hazardous_code = instance_class_hazardous.is_hazardous_material(str(sat_product_id.code))
            if line.hazardous_material == 'Sí':
                merchandise_data.update({
                                            'MaterialPeligroso': line.hazardous_material,
                                        })
            else:
                if hazardous_code == '0,1' and line.force_hazardous_pac:
                    merchandise_data.update({
                                                'MaterialPeligroso': 'No',
                                            })
                else:
                    merchandise_data.update({
                                                'MaterialPeligroso': False,
                                            })

            if line.hazardous_key_product_id:
                merchandise_data.update({
                                            'CveMaterialPeligroso': line.hazardous_key_product_id.code,
                                        })
            else:
                merchandise_data.update({
                                            'CveMaterialPeligroso': False,
                                        })

            if line.invoice_id and line.invoice_id.currency_id:
                merchandise_data.update({
                                            'Moneda': line.invoice_id.currency_id.name.upper(),
                                        })


            if line.charge_value:
                merchandise_data.update({
                                            'ValorMercancia': "%.3f" % (line.charge_value),
                                        })
            else:
                merchandise_data.update({
                                            'ValorMercancia': 0.0,
                                        })

            if line.tipo_embalaje_id:
                merchandise_data.update({
                                            'Embalaje': line.tipo_embalaje_id.code,
                                            'DescripEmbalaje': line.tipo_embalaje_id.name,
                                        })
            else:
                merchandise_data.update({
                                            'Embalaje': False,
                                            'DescripEmbalaje': False,
                                        })

            if line.fraccion_arancelaria:
                merchandise_data.update({
                                            'FraccionArancelaria': line.fraccion_arancelaria,
                                        })
            else:
                merchandise_data.update({
                                            'FraccionArancelaria': False,
                                        })
            if line.comercio_ext_uuid:
                merchandise_data.update({
                                            'UUIDComercioExt': line.comercio_ext_uuid,
                                        })
            else:
                merchandise_data.update({
                                            'UUIDComercioExt': False,
                                        })

            #### Agregando los Pedimentos ####
            pedimentos_list =  []
            if line.pedimentos_ids:
                for pedimento in line.pedimentos_ids:
                    pedimento_data  =  {'Pedimento':  pedimento.waybill_pedimento}
                    pedimentos_list.append(pedimento_data)

            merchandise_data.update({
                                           'cartaporte20:Pedimentos': pedimentos_list,
                                        })

            ### Agregando Guias de Identificación ####
            guias_list =  []
            if line.guia_ids:
                for guia in line.guia_ids:
                    guia_data  =  {
                                    'NumeroGuiaIdentificacion':  guia.numero_guia,
                                    'DescripGuiaIdentificacion':  guia.descripcion_guia,
                                    'PesoGuiaIdentificacion':  "%.3f" % (guia.peso_paquete),
                                    }
                    guias_list.append(guia_data)

            merchandise_data.update({
                                           'cartaporte20:GuiasIdentificacion': guias_list,
                                        })
            
            #### Agregando Cantidad Transportada ####
            cantidades_list =  []
            if line.cantidades_ids:
                for cantidadtransporta in line.cantidades_ids:
                    cant_transporta_data  =  {
                                                'Cantidad':  cantidadtransporta.cantidad,
                                                'IDOrigen':  cantidadtransporta.idorigen,
                                                'IDDestino':  cantidadtransporta.iddestino,
                                            } 
                    cantidades_list.append(cant_transporta_data)
                    
            merchandise_data.update({
                                           'cartaporte20:CantidadTransporta': cantidades_list,
                                        })
            
            # merchandise_data = {
            #                         'BienesTransp': "10101500",
            #                         'ClaveSTCC': "01",
            #                         'Descripcion': "Test",
            #                         'Cantidad': "1",
            #                         'ClaveUnidad': "H87",
            #                         'Dimensiones': "30/20/10plg",
            #                         'PesoEnKg': "20.000",
            #                         'ValorMercancia': "0.000",
            #                         'Moneda': "MXN",
            #                     }
            mercancias_data['cartaporte20:Mercancias'].append(
                                                            merchandise_data  
                                                            )
        return mercancias_data

    #### Insertando el nodo de acuerdo al tipo de transporte ####
    def _get_complement_waybill_transport_type(self,):
        _logger.info("\n##### Insertando los nodos para el tipo de Transporte >>>>>>>> ")
        if self.tipo_transporte_id.code == '01':
            _logger.info("\n##### Auto Transporte Federal >>>>>>>> ")
            vehicle_id_data = {
                                    'ConfigVehicular': self.configuracion_federal_id.code,
                                    'PlacaVM': self.vehicle_plate_cp,
                                    'AnioModeloVM': self.vehicle_year_model_cp
                               }
            insurance_list = []
            for insurance in self.insurance_ids:
                insurance_vals = {
                                    'AseguraRespCivil': insurance.insurance_partner_id.name,
                                    'PolizaRespCivil': insurance.insurance_policy,
                                    'AseguraMedAmbiente': False,
                                    'PolizaMedAmbiente': False,
                                    'AseguraCarga': False,
                                    'PolizaCarga': False,
                                    'PrimaSeguro': False,
                                }
                if insurance.ambiental_insurance_partner_id:
                    insurance_vals.update({
                                    'AseguraMedAmbiente': insurance.ambiental_insurance_partner_id.name,
                                    'PolizaMedAmbiente': insurance.ambiental_insurance_policy,
                                    })
                if insurance.transport_insurance_partner_id:
                    insurance_vals.update({
                                    'AseguraCarga': insurance.transport_insurance_partner_id.name,
                                    'PolizaCarga': insurance.transport_insurance_policy,
                                    })
                if insurance.insurance_amount > 0.0:
                    insurance_vals.update({
                                    'PrimaSeguro': "%.3f" % (insurance.insurance_amount),
                                    })
                insurance_list.append(insurance_vals)

            federal_transport_data = {
                                           'PermSCT': self.type_stc_permit_id.code,
                                           'NumPermisoSCT': self.type_stc_permit_number,
                                           'cartaporte20:IdentificacionVehicular': vehicle_id_data,
                                           'cartaporte20:Seguros': [insurance_list[-1]] if insurance_list else False, ## Si queremos mandar todos los registros de seguro descomentar
                                      }
        elif self.tipo_transporte_id.code == '03':
            vehicle_id_data = {'PlacaVM': self.vehicle_plate_cp,
                              }
            federal_transport_data = {
                                           'PermSCT': self.type_stc_permit_id.code,
                                           'NumPermisoSCT': self.type_stc_permit_number,
                                           'NombreAseg': self.partner_insurance_id.commercial_partner_id.name,
                                           'NumPolizaSeguro': self.partner_insurance_number,
                                           'cartaporte:IdentificacionVehicular': vehicle_id_data,
                                      }

        return federal_transport_data

    def _get_complement_waybill_type_federal_add_trailers(self):
        trailers_list = []
        #### Trailer 01 ####
        if self.trailer_line_ids:
            for trailer in self.trailer_line_ids:
                trailer_plate_cp = trailer.trailer_plate_cp

                remolque_data = { 
                                    'SubTipoRem': trailer.subtype_trailer_id.code,
                                    'Placa': trailer_plate_cp if trailer_plate_cp else "" ,
                                   }

                trailers_list.append(
                                        remolque_data
                                    )
        return trailers_list

    #### Insertando el nodo Figura de Transporte ####

    def _get_complement_waybill_figure_transport(self,):
        _logger.info("\n##### Insertando el Nodo de Figura de Transporte >>>>>>>> ")
        driver_figure_ids = self.driver_figure_ids
        other_figure_ids = self.other_figure_ids
        figures_list = []
        
        for driver in self.driver_figure_ids:
            driver_cp_id = driver.partner_id
            info_driver = {
                            'TipoFigura': '01',
                            'NombreFigura': driver_cp_id.name,
                            'NumLicencia': driver.cp_driver_license,
                          }

            if driver_cp_id.country_id.l10n_mx_edi_code != 'MEX':
                info_driver.update({
                                    'ResidenciaFiscalFigura': driver_cp_id.country_id.l10n_mx_edi_code,
                                    'NumRegIdTribFigura': driver_cp_id.num_reg_trib,
                                    'RFCFigura': False,
                                    })
            else:
                info_driver.update({
                                    'RFCFigura': driver.driver_cp_vat,
                                    'ResidenciaFiscalFigura': False,
                                    'NumRegIdTribFigura': False,
                                    })    
            if driver.add_address and self.transport_document_cfdi == False:            
                state_info  = ""
                country_code = ""
                zip_code = ""

                state_info = ""
                if driver_cp_id.state_id and driver_cp_id.state_id.code:
                    state_info = driver_cp_id.state_id.code

                zip_code = ""
                if driver_cp_id.zip_sat_id:
                    zip_code = driver_cp_id.zip_sat_id.code
                if not zip_code:
                    zip_code = driver_cp_id.zip

                address_info =  {
                                   'Estado': state_info,
                                   'Pais': driver_cp_id.country_id.l10n_mx_edi_code,
                                   'CodigoPostal': zip_code,
                                }

                #### Dirección/Domicilio ####
                op_partner_street = driver_cp_id.street_name
                if  op_partner_street:
                    address_info.update({
                                                'Calle': op_partner_street,   
                                            })
                else:
                    address_info.update({
                                                'Calle': False,   
                                            })


                op_partner_ext_number = driver_cp_id.street_number
                if op_partner_ext_number:
                    address_info.update({
                                                'NumeroExterior': op_partner_ext_number,   
                                            })
                else:
                    address_info.update({
                                                'NumeroExterior': False,   
                                            })


                op_partner_int_number = driver_cp_id.street_number2
                if op_partner_int_number:
                    address_info.update({
                                                'NumeroInterior': op_partner_int_number,   
                                            })
                else:
                    address_info.update({
                                                'NumeroInterior': False,   
                                            })

                op_partner_colony = driver_cp_id.colonia_sat_id.code if driver_cp_id.colonia_sat_id else ""
                if op_partner_colony:
                    op_partner_colony =  self.add_padding_char(4,op_partner_colony,'0','left')
                    address_info.update({
                                                'Colonia': op_partner_colony,   
                                            })
                else:
                    address_info.update({
                                                'Colonia': False,   
                                            })

                op_partner_locality = driver_cp_id.l10n_mx_edi_locality_id.code if driver_cp_id.l10n_mx_edi_locality_id else ""
                if op_partner_locality:
                    address_info.update({
                                                'Localidad': op_partner_locality,   
                                            })
                else:
                    address_info.update({
                                                'Localidad': False,   
                                            })

                op_partner_township = driver_cp_id.zip_sat_id.township_sat_code.code if driver_cp_id.zip_sat_id.township_sat_code else ""
                if op_partner_township:
                    address_info.update({
                                                'Municipio': op_partner_township,   
                                            })
                else:
                    address_info.update({
                                                'Municipio': False,   
                                            })

                info_driver.update({
                                        'cartaporte20:Domicilio': address_info,
                                   })
            else:
                info_driver.update({
                                        'cartaporte20:Domicilio': False,
                                   })
            info_driver.update({
                                        'cartaporte20:PartesTransporte': [],
                                   })

            driver_data = {   
                            'cartaporte20:TiposFigura': info_driver,
                            
                         }

            figures_list.append(driver_data)

        for figure in self.other_figure_ids:
            figure_partner = figure.partner_id
            info_figure = {
                            'TipoFigura': figure.figure_type_id.code,
                            'NombreFigura': figure_partner.name,
                          }
            if figure_partner.country_id.l10n_mx_edi_code != 'MEX':
                info_figure.update({
                                    'ResidenciaFiscalFigura': figure_partner.country_id.l10n_mx_edi_code,
                                    'NumRegIdTribFigura': figure_partner.num_reg_trib,
                                    'RFCFigura': False,
                                    })
            else:
                info_figure.update({
                                    'RFCFigura': figure_partner.vat_split,
                                    'ResidenciaFiscalFigura': False,
                                    'NumRegIdTribFigura': False,
                                    })    
            if figure.add_address and self.transport_document_cfdi == False:              
                state_info  = ""
                country_code = ""
                zip_code = ""

                state_info = ""
                if figure_partner.state_id and figure_partner.state_id.code:
                    state_info = figure_partner.state_id.code

                zip_code = ""
                if figure_partner.zip_sat_id:
                    zip_code = figure_partner.zip_sat_id.code
                if not zip_code:
                    zip_code = figure_partner.zip

                address_info =  {
                                   'Estado': state_info,
                                   'Pais': figure_partner.country_id.l10n_mx_edi_code,
                                   'CodigoPostal': zip_code,
                                }

                #### Dirección/Domicilio ####
                fig_partner_street = figure_partner.street_name
                if  fig_partner_street:
                    address_info.update({
                                                'Calle': fig_partner_street,   
                                            })
                else:
                    address_info.update({
                                                'Calle': False,   
                                            })

                fig_partner_ext_number = figure_partner.street_number
                if fig_partner_ext_number:
                    address_info.update({
                                                'NumeroExterior': fig_partner_ext_number,   
                                            })
                else:
                    address_info.update({
                                                'NumeroExterior': False,   
                                            })

                fig_partner_int_number = figure_partner.street_number2
                if fig_partner_int_number:
                    address_info.update({
                                                'NumeroInterior': fig_partner_int_number,   
                                            })
                else:
                    address_info.update({
                                                'NumeroInterior': False,   
                                            })

                fig_partner_colony = figure_partner.colonia_sat_id.code if figure_partner.colonia_sat_id else ""
                if fig_partner_colony:
                    fig_partner_colony =  self.add_padding_char(4,fig_partner_colony,'0','left')
                    address_info.update({
                                                'Colonia': fig_partner_colony,   
                                            })
                else:
                    address_info.update({
                                                'Colonia': False,   
                                            })

                fig_partner_locality = figure_partner.l10n_mx_edi_locality_id.code if figure_partner.l10n_mx_edi_locality_id else ""
                if fig_partner_locality:
                    address_info.update({
                                                'Localidad': fig_partner_locality,   
                                            })
                else:
                    address_info.update({
                                                'Localidad': False,   
                                            })

                fig_partner_township = figure_partner.zip_sat_id.township_sat_code if figure_partner.zip_sat_id.township_sat_code else ""
                if fig_partner_township:
                    address_info.update({
                                                'Municipio': fig_partner_township,   
                                            })
                else:
                    address_info.update({
                                                'Municipio': False,   
                                            })


                info_figure.update({
                                        'cartaporte20:Domicilio': address_info,
                                   })
            else:
                info_figure.update({
                                        'cartaporte20:Domicilio': False,

                                   })
            info_figure_list = []

            if figure.transport_part_ids:
                for part in figure.transport_part_ids:
                    part_data  = {
                                        'ParteTransporte': part.code,
                                 }
                    info_figure_list.append(part_data)

            info_figure.update({
                                        'cartaporte20:PartesTransporte': info_figure_list,
                                   })

            figure_data = {   
                            'cartaporte20:TiposFigura': info_figure,
                            
                         }

            figures_list.append(figure_data)

        return figures_list


    #### Metodos para la Asignación de Zona horaria con las fechas/horas ####
        ####################################
    
    def get_complement_server_timezone(self):
        return "UTC"
    

    def get_complement_server_to_local_timestamp(self, fecha, dst_tz_name,
            tz_offset=True, ignore_unparsable_time=True):

        if not fecha:
            return False

        res = fecha
        server_tz = self.get_complement_server_timezone()
        try:
            # dt_value needs to be a datetime object (so no time.struct_time or mx.DateTime.DateTime here!)
            dt_value = fecha
            if tz_offset and dst_tz_name:
                try:                        
                    src_tz = pytz.timezone(server_tz)
                    dst_tz = pytz.timezone(dst_tz_name)
                    src_dt = src_tz.localize(dt_value, is_dst=True)
                    dt_value = src_dt.astimezone(dst_tz)
                except Exception:
                    pass
            res = dt_value.replace(tzinfo=None)
        except Exception:
            if not ignore_unparsable_time:
                return False
        return res

    ########## Metodos que Agrega Relleno (Padding) ###########

    def add_padding_char(self, padding_number, cadena, caracter, position_add):
        while(len(cadena)<padding_number):
            if position_add == 'left':
                cadena = caracter+cadena
            else:
                cadena = cadena+caracter
        return cadena

    #### Metodos solo para el Reporte #####

    def get_location_address(self, partner_location, location_partner_references):
        domicilio =""
        partner_location_parent = False
        if partner_location.parent_id:
            partner_location_parent = partner_location.parent_id
        origin_partner_street = partner_location.street_name
        if not origin_partner_street and partner_location_parent:
            origin_partner_street = partner_location_parent.street_name

        domicilio = domicilio+' Calle: '+ str(origin_partner_street)

        origin_partner_ext_number = partner_location.street_number
        if not origin_partner_ext_number and partner_location_parent:
            origin_partner_ext_number = partner_location_parent.street_number
        if origin_partner_ext_number:
            domicilio = domicilio+' No. Exterior: '+ str(origin_partner_ext_number)

        origin_partner_int_number = partner_location.street_number2
        if not origin_partner_int_number and partner_location_parent:
            origin_partner_int_number = partner_location_parent.street_number2
        if origin_partner_int_number:
            domicilio = domicilio+' No. Interior: '+ str(origin_partner_int_number)

        origin_partner_colony = partner_location.colonia_sat_id.name if partner_location.colonia_sat_id else ""
        if not origin_partner_colony and partner_location_parent:
            origin_partner_colony = partner_location_parent.colonia_sat_id.name if partner_location_parent.colonia_sat_id else ""
        if origin_partner_colony:
            domicilio = domicilio+' Colonia: '+ str(origin_partner_colony)

        origin_partner_locality = partner_location.zip_sat_id.locality_sat_code.name if partner_location.zip_sat_id.locality_sat_code else ""
        if not origin_partner_locality and partner_location_parent:
            origin_partner_locality = partner_location_parent.zip_sat_id.locality_sat_code.code if partner_location_parent.zip_sat_id.locality_sat_code else ""
        if origin_partner_locality:
            domicilio = domicilio+' Localidad: '+ str(origin_partner_locality)

        origin_partner_references = location_partner_references
        if origin_partner_references:
            domicilio = domicilio+' Referencia: '+ str(origin_partner_references)

        origin_partner_township = partner_location.city_id.name if partner_location.city_id else ""
        if not origin_partner_township and partner_location_parent:
            origin_partner_township = partner_location_parent.city_id.name if partner_location_parent.city_id else ""
        if origin_partner_township:
            domicilio = domicilio+' Municipio: '+ str(origin_partner_township)

        origin_partner_state = ""
        if partner_location.state_id:
            origin_partner_state = partner_location.state_id.name
        if not origin_partner_state and partner_location_parent:
            if partner_location_parent.state_id and partner_location_parent.state_id:
                origin_partner_state = partner_location_parent.state_id.name
        if origin_partner_state:
            domicilio = domicilio+' Estado: '+ str(origin_partner_state)

        origin_partner_country = ""
        if partner_location.country_id:
            origin_partner_country = partner_location.country_id.name
        if not origin_partner_country and partner_location_parent:
            if partner_location_parent.country_id:
                origin_partner_country = partner_location_parent.country_id.name

        domicilio = domicilio+' Pais: '+ str(origin_partner_country)

        origin_partner_zip = ""
        if partner_location.zip_sat_id:
            origin_partner_zip = partner_location.zip_sat_id.code
        if not origin_partner_zip and partner_location_parent:
            if partner_location_parent.zip_sat_id:
                origin_partner_zip = partner_location_parent.zip_sat_id.code
        if not origin_partner_zip:
            origin_partner_zip = partner_location.zip
            if not origin_partner_zip and partner_location_parent:
                origin_partner_zip = partner_location_parent.zip
        
        domicilio = domicilio+' CodigoPostal: '+ str(origin_partner_zip)

        return domicilio

    def convert_datetime_to_tz(self, date_time):
        tz = self.env.user.partner_id.tz or 'Mexico/General'
        waybill_date_time = date_time and self.get_complement_server_to_local_timestamp(
                    date_time, tz) or False

        waybill_date_time = str(waybill_date_time)[0:19]
        waybill_date_time.replace(' ','T')
        date_out_splt = waybill_date_time.split(' ')
        date_res_tz = date_out_splt[0]+'T'+date_out_splt[1]
        return date_res_tz


    ############### Descarga de Plantilla Excel ##################################

    def download_waybill_data_excel(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        file_url = base_url+"/web/content?model=account.move&field=waybill_file&filename_field=waybill_datas_fname&id=%s&&download=true" % (self.id,)
        self.generate_report_waybill_xlsx()
        return {
                 'type': 'ir.actions.act_url',
                 'url': file_url,
                 'target': 'new'
                }
        


    def generate_report_waybill_xlsx(self):
        workbook = xlwt.Workbook(encoding='utf-8',style_compression=2)
        heading_format = xlwt.easyxf('font:height 200,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center')
        heading_format_left = xlwt.easyxf('font:height 200,bold True;pattern: pattern solid, fore_colour gray25;align: horiz left')
        bold = xlwt.easyxf('font:bold True,height 215;pattern: pattern solid, fore_colour gray25;align: horiz center')
        bold_center = xlwt.easyxf('font:height 240,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center;')
        bold_right = xlwt.easyxf('font:height 240,bold True;pattern: pattern solid, fore_colour gray25;align: horiz right;')
        bold_left = xlwt.easyxf('font:height 240,bold True;pattern: pattern solid, fore_colour gray25;align: horiz left;')

        ### Cutom Color Background fot Comments ####
        xlwt.add_palette_colour("gray_custom", 0x21)
        workbook.set_colour_RGB(0x21, 238, 238, 238)

        tags_data_gray = xlwt.easyxf('font:bold True,height 200;pattern: pattern solid, fore_colour gray_custom;align: horiz center')
        
        tags_data_gray_right = xlwt.easyxf('font:height 200,bold True;pattern: pattern solid, fore_colour gray_custom;align: horiz right;')
        tags_data_gray_center = xlwt.easyxf('font:height 200,bold True;pattern: pattern solid, fore_colour gray_custom;align: horiz center;')
        tags_data_gray_left = xlwt.easyxf('font:height 200;pattern: pattern solid, fore_colour gray_custom;align: horiz left;')
            
        

        totals_bold_right = xlwt.easyxf('font:height 200,bold True;pattern: pattern solid, fore_colour gray25;align: horiz right;')
        totals_bold_center = xlwt.easyxf('font:height 200,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center;')
        totals_bold_left = xlwt.easyxf('font:height 200;pattern: pattern solid, fore_colour gray25;align: horiz left;')
        
        normal_center = xlwt.easyxf('align: horiz center;')
        normal_right = xlwt.easyxf('align: horiz right;')
        normal_left = xlwt.easyxf('align: horiz left;')

        normal_center_yellow = xlwt.easyxf('align: horiz center;pattern: pattern solid, fore_colour light_yellow;')
        normal_right_yellow = xlwt.easyxf('align: horiz right;pattern: pattern solid, fore_colour light_yellow;')
        normal_left_yellow = xlwt.easyxf('align: horiz left;pattern: pattern solid, fore_colour light_yellow;')

        #### Con Bordes #####
        # "borders: top double, bottom double, left double, right double;" # Como botones

        tags_data_gray_right_border = xlwt.easyxf('font:height 200,bold True;pattern: pattern solid, fore_colour gray_custom;align: horiz right;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        tags_data_gray_center_border = xlwt.easyxf('font:height 200,bold True;pattern: pattern solid, fore_colour gray_custom;align: horiz center;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        tags_data_gray_left_border = xlwt.easyxf('font:height 200;pattern: pattern solid, fore_colour gray_custom;align: horiz left;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        
        normal_center_yellow_border = xlwt.easyxf('align: horiz center;pattern: pattern solid, fore_colour light_yellow;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        normal_right_yellow_border = xlwt.easyxf('align: horiz right;pattern: pattern solid, fore_colour light_yellow;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        normal_left_yellow_border = xlwt.easyxf('align: horiz left;pattern: pattern solid, fore_colour light_yellow;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')

        normal_center_border = xlwt.easyxf('align: horiz center;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        normal_right_border = xlwt.easyxf('align: horiz right;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')
        normal_left_border = xlwt.easyxf('align: horiz left;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')

        heading_format_border = xlwt.easyxf('font:height 200,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center;borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;')

        worksheet = workbook.add_sheet('Cartar Porte 2.0', bold_center)
        worksheet.write_merge(0, 0, 0, 3, 'DATOS CLIENTE', heading_format)
        left = xlwt.easyxf('align: horiz center;font:bold True')
        worksheet.write_merge(0, 0, 4, 6, 'DATOS DEL CFDI', heading_format)
        worksheet.col(0).width  = int(40 * 260)
        worksheet.col(1).width  = int(40 * 260)
        worksheet.col(2).width  = int(18 * 260)
        worksheet.col(3).width  = int(18 * 260)
        worksheet.col(4).width  = int(40 * 260)
        worksheet.col(5).width  = int(18 * 260)
        worksheet.col(6).width  = int(40 * 260)
        worksheet.col(7).width  = int(18 * 260)
        worksheet.col(8).width  = int(18 * 260)
        worksheet.col(9).width  = int(18 * 260)
        worksheet.col(10).width = int(18 * 260)
        worksheet.col(11).width = int(18 * 260)
        worksheet.col(12).width = int(18 * 260)
        worksheet.col(13).width = int(18 * 260)
        worksheet.col(14).width = int(18 * 260)
        worksheet.col(15).width = int(18 * 260)
        worksheet.col(16).width = int(18 * 260)
        worksheet.col(17).width = int(18 * 260)
        worksheet.col(18).width = int(18 * 260)
        worksheet.col(20).width = int(18 * 260)
        worksheet.col(21).width = int(18 * 260)
        worksheet.col(22).width = int(18 * 260)
        
        row = 1
        worksheet.write(row, 0, "Nombre", tags_data_gray_left_border)
        worksheet.write(row, 1, self.partner_id.name, normal_left) # Cambiar

        forma_pago_name = ""
        if self.l10n_mx_edi_payment_method_id:
            forma_pago_name = self.l10n_mx_edi_payment_method_id.code+" - " + self.l10n_mx_edi_payment_method_id.name

        worksheet.write(row, 4, "Forma de Pago (Clave SAT)", tags_data_gray_left_border)
        worksheet.write_merge(row, row, 5, 6, forma_pago_name, normal_left_border) # Cambiar

        row += 1
        rfc_cliente = self.partner_id.vat
        worksheet.write(row, 0, "RFC", tags_data_gray_left_border)
        worksheet.write(row, 1, rfc_cliente, normal_left_border) # Cambiar

        metodo_pago_code = self.l10n_mx_edi_payment_policy
        worksheet.write(row, 4, "Política de Pago", tags_data_gray_left_border)
        worksheet.write_merge(row, row, 5, 6, metodo_pago_code, normal_left_border) # Cambiar

        row += 1
        partner_street = self.partner_id.street_name
        worksheet.write(row, 0, "Calle", tags_data_gray_left_border)
        worksheet.write(row, 1, partner_street, normal_left_border) # Cambiar

        uso_cfdi_code = self.l10n_mx_edi_usage if self.l10n_mx_edi_usage else ""
        worksheet.write(row, 4, "Uso CFDI (Clave SAT)", tags_data_gray_left_border)
        worksheet.write_merge(row, row, 5, 6, uso_cfdi_code, normal_left_border) # Cambiar


        row += 1
        partner_ext_number = self.partner_id.street_number
        worksheet.write(row, 0, "Número Ext.", tags_data_gray_left_border)
        worksheet.write(row, 1, partner_ext_number, normal_left_border) # Cambiar

        row += 1
        partner_int_number = self.partner_id.street_number2 if self.partner_id.street_number2 else "SN"
        worksheet.write(row, 0, "Número Int.", tags_data_gray_left_border)
        worksheet.write(row, 1, partner_int_number, normal_left_border) # Cambiar

        row += 1
        partner_colony_code = self.partner_id.colonia_sat_id.code if self.partner_id.colonia_sat_id else ""
        partner_colony_name = self.partner_id.colonia_sat_id.name if self.partner_id.colonia_sat_id else ""
        worksheet.write(row, 0, "Colonia (Clave SAT)", tags_data_gray_left_border)
        worksheet.write(row, 1, partner_colony_code, normal_left_border) # Cambiar
        worksheet.write(row, 2, partner_colony_name, normal_left_yellow) # Cambiar

        row += 1
        partner_locality_code = self.partner_id.zip_sat_id.locality_sat_code.code if self.partner_id.zip_sat_id.locality_sat_code else ""
        partner_locality_name = ""
        worksheet.write(row, 0, "Localidad", tags_data_gray_left_border)
        worksheet.write(row, 1, partner_locality_code, normal_left_border) # Cambiar
        worksheet.write(row, 2, partner_locality_name, normal_left_yellow) # Cambiar

        row += 1
        partner_zip = self.partner_id.zip_sat_id.code if self.partner_id.zip_sat_id else self.partner_id.zip
        worksheet.write(row, 0, "CP", tags_data_gray_left_border)
        worksheet.write(row, 1, partner_zip, normal_left_border) # Cambiar

        row += 1
        partner_state_code = self.partner_id.state_id.name if self.partner_id.state_id else ""
        partner_state_name = ""
        if self.partner_id.state_id:
            if self.partner_id.state_id.code:
                partner_state_code = self.partner_id.state_id.code if self.partner_id.state_id.code else ""
        worksheet.write(row, 0, "Estado (Código SAT)", tags_data_gray_left_border)
        worksheet.write(row, 1, partner_state_code, normal_left_border) # Cambiar
        worksheet.write(row, 2, partner_state_name, normal_left_yellow) # Cambiar

        row += 1
        partner_country_code = ""
        partner_country_name = self.partner_id.country_id.name if self.partner_id.country_id else ""
        if self.partner_id.country_id.l10n_mx_edi_code:
            partner_country_code = self.partner_id.country_id.l10n_mx_edi_code
        worksheet.write(row, 0, "País (Código)", tags_data_gray_left_border)
        worksheet.write(row, 1, partner_country_code, normal_left_border) # Cambiar
        worksheet.write(row, 2, partner_country_name, normal_left_yellow) # Cambiar
        

        ### Complemento Carta Porte ###
        row += 3
        worksheet.write_merge(row, row, 0, 6, 'Datos Complemento Carta Porte', heading_format_left)
        row += 2

        tipo_transporte_code = self.tipo_transporte_id.code if self.tipo_transporte_id else ""
        tipo_transporte_name = self.tipo_transporte_id.name if self.tipo_transporte_id else ""
        worksheet.write(row, 0, "Tipo Transporte (Clave SAT)", tags_data_gray_left_border)
        worksheet.write(row, 1, tipo_transporte_code, normal_left_border) # Cambiar
        worksheet.write(row, 2, tipo_transporte_name, normal_left_yellow) # Cambiar

        international_shipping = self.international_shipping
        worksheet.write(row, 4, "Transporte Internacional", tags_data_gray_left_border)
        worksheet.write(row, 5, international_shipping, normal_left_border) # Cambiar

        row +=1
        permiso_stc_code = self.type_stc_permit_id.code if self.type_stc_permit_id else ""
        permiso_stc_name = self.type_stc_permit_id.name if self.type_stc_permit_id else ""
        worksheet.write(row, 0, "Permiso STC", tags_data_gray_left_border)
        worksheet.write(row, 1, permiso_stc_code, normal_left_border) # Cambiar
        worksheet.write(row, 2, permiso_stc_name, normal_left_yellow) # Cambiar

        entrada_salida = self.shipping_complement_type
        worksheet.write(row, 4, "Entrada/Salida", tags_data_gray_left_border)
        worksheet.write(row, 5, entrada_salida, normal_left_border) # Cambiar

        row +=1
        permiso_stc_number = self.type_stc_permit_number
        worksheet.write(row, 0, "Numero Permiso STC", tags_data_gray_left_border)
        worksheet.write(row, 1, permiso_stc_number, normal_left_border) # Cambiar

        merchandice_country_origin_code = ""
        if self.merchandice_country_origin_id:
            merchandice_country_origin_code = self.merchandice_country_origin_id.l10n_mx_edi_code if self.merchandice_country_origin_id.l10n_mx_edi_code else ""
        worksheet.write(row, 4, "País de Origen/Destino (Código)", tags_data_gray_left_border)
        worksheet.write(row, 5, merchandice_country_origin_code, normal_left_border) # Cambiar

        row +=1
        configuracion_federal_code = self.configuracion_federal_id.code if self.configuracion_federal_id else ""
        configuracion_federal_name = self.configuracion_federal_id.name if self.configuracion_federal_id else ""
        worksheet.write(row, 0, "Configuración del Transporte", tags_data_gray_left_border)
        worksheet.write(row, 1, configuracion_federal_code, normal_left_border) # Cambiar
        worksheet.write(row, 2, configuracion_federal_name, normal_left_yellow) # Cambiar

        tipo_transporte_entrada_salida_code = self.tipo_transporte_entrada_salida_id.code if self.tipo_transporte_entrada_salida_id else ""
        worksheet.write(row, 4, "Vía Entrada Salida", tags_data_gray_left_border)
        worksheet.write(row, 5, tipo_transporte_entrada_salida_code, normal_left_border) # Cambiar

        row +=1
        waybill_pedimento = self.waybill_pedimento if self.waybill_pedimento else ""
        worksheet.write(row, 4, "Pedimento", tags_data_gray_left_border)
        worksheet.write(row, 5, waybill_pedimento, normal_left_border) # Cambiar

        row +=2
        configuracion_federal_code = self.configuracion_federal_id.code if self.configuracion_federal_id else ""
        worksheet.write(row, 0, "Unidad Motriz", tags_data_gray_left_border)
        worksheet.write(row, 1, configuracion_federal_code, normal_left_border) # Cambiar

        tipo_transporte_entrada_salida_code = self.tipo_transporte_entrada_salida_id.code if self.tipo_transporte_entrada_salida_id else ""
        worksheet.write_merge(row, row, 4, 5, 'Remolques', heading_format_border)

        row +=1
        vehicle_plate_cp = self.vehicle_plate_cp if self.vehicle_plate_cp else ""
        worksheet.write(row, 0, "Placa Vehicular", tags_data_gray_left_border)
        worksheet.write(row, 1, configuracion_federal_code, normal_left_border) # Cambiar

        tipo_transporte_entrada_salida_code = self.tipo_transporte_entrada_salida_id.code if self.tipo_transporte_entrada_salida_id else ""
        worksheet.write(row, 4, "Tipo Remolque (Clave SAT)", tags_data_gray_left_border)
        worksheet.write(row, 5, "Placas", tags_data_gray_left_border)

        remolques_names = []
        remolques_placas = []
        if self.trailer_line_ids:
            for trailer in self.trailer_line_ids:
                remolques_names.append(trailer.subtype_trailer_id.code)
                remolques_placas.append(trailer.trailer_plate_cp)

        row +=1
        vehicle_year_model_cp = self.vehicle_year_model_cp if self.vehicle_year_model_cp else ""
        worksheet.write(row, 0, "Modelo", tags_data_gray_left_border)
        worksheet.write(row, 1, vehicle_year_model_cp, normal_left_border) # Cambiar

        if remolques_names:
            worksheet.write(row, 4, remolques_names[0] if remolques_names else "", normal_left_border) # Cambiar
            worksheet.write(row, 5, remolques_placas[0] if remolques_placas else "", normal_left_border) # Cambiar
            remolques_names.pop(0)
            remolques_placas.pop(0)

        if remolques_names: # Siquedaron mas remolques
            i = 0
            for remolque in remolques_names:
                row +=1
                worksheet.write(row, 4, remolques_names[i], normal_left_border) # Cambiar
                worksheet.write(row, 5, remolques_placas[i], normal_left_border) # Cambiar
                i+=1

        ### Figuras de Transporte ###
        row += 3
        worksheet.write_merge(row, row, 0, 6, 'Figuras de Transporte', heading_format_left)
        row += 2
        worksheet.write(row, 0, "Tipo de Figura", tags_data_gray_center_border)
        worksheet.write(row, 1, "Nombre", tags_data_gray_center_border)
        worksheet.write(row, 2, "RFC", tags_data_gray_center_border)
        worksheet.write(row, 3, "Estado (Código SAT)", tags_data_gray_center_border)
        worksheet.write(row, 4, "País (Código)", tags_data_gray_center_border)
        worksheet.write(row, 5, "CP", tags_data_gray_center_border)
        worksheet.write(row, 6, "Tipos Parte Transporte", tags_data_gray_center_border)

        ### Operadores ####

        for driver in self.driver_figure_ids:
            driver_cp_id = driver.partner_id

            country_code = ""
            zip_code = ""

            state_info = ""
            if driver_cp_id.state_id and driver_cp_id.state_id.code:
                state_info = driver_cp_id.state_id.code
           
            zip_code = ""
            if driver_cp_id.zip_sat_id:
                zip_code = driver_cp_id.zip_sat_id.code
            if not zip_code:
                zip_code = driver_cp_id.zip

            if driver_cp_id.country_id and driver_cp_id.country_id.l10n_mx_edi_code:
                country_code = driver_cp_id.country_id.l10n_mx_edi_code

            driver_complete_info = driver_cp_id.name
            if driver_cp_id.cp_driver_license:
                driver_complete_info = driver_complete_info + " \n# Licencia: "+driver_cp_id.cp_driver_license

            row += 1
            worksheet.write(row, 0, "01", normal_left_border)
            worksheet.write(row, 1, driver_complete_info, normal_left_border)
            worksheet.write(row, 2, driver.driver_cp_vat, normal_left_border)
            worksheet.write(row, 3, state_info, normal_left_border)
            worksheet.write(row, 4, country_code, normal_left_border)
            worksheet.write(row, 5, zip_code, normal_left_border)
            worksheet.write(row, 6, "", normal_left_border)

        ### Otras Figuras ####

        for figure in self.other_figure_ids:
            figure_cp_id = figure.partner_id

            country_code = ""
            zip_code = ""

            state_info = ""
            if figure_cp_id.state_id and figure_cp_id.state_id.code:
                state_info = figure_cp_id.state_id.code
           
            zip_code = ""
            if figure_cp_id.zip_sat_id:
                zip_code = figure_cp_id.zip_sat_id.code
            if not zip_code:
                zip_code = figure_cp_id.zip

            if figure_cp_id.country_id and figure_cp_id.country_id.l10n_mx_edi_code:
                country_code = figure_cp_id.country_id.l10n_mx_edi_code

            figure_complete_info = figure_cp_id.name

            partes_transporte = ""
            if figure.transport_part_ids:
                for part in figure.transport_part_ids:
                    partes_transporte = partes_transporte+", "+part.code if partes_transporte else part.code

            row += 1
            worksheet.write(row, 0, figure.figure_type_id.code, normal_left_border)
            worksheet.write(row, 1, figure_complete_info, normal_left_border)
            worksheet.write(row, 2, figure_cp_id.vat, normal_left_border)
            worksheet.write(row, 3, state_info, normal_left_border)
            worksheet.write(row, 4, country_code, normal_left_border)
            worksheet.write(row, 5, zip_code, normal_left_border)
            worksheet.write(row, 6, partes_transporte, normal_left_border)

        ### Aseguradoras ###
        row += 3
        worksheet.write_merge(row, row, 0, 6, 'Aseguradoras', heading_format_left)
        row += 2
        worksheet.write(row, 0, "Tipo de Aseguradora", tags_data_gray_center_border)
        worksheet.write(row, 1, "Nombre", tags_data_gray_center_border)
        worksheet.write(row, 2, "RFC", tags_data_gray_center_border)
        worksheet.write(row, 3, "Estado (Código SAT)", tags_data_gray_center_border)
        worksheet.write(row, 4, "País (Código)", tags_data_gray_center_border)
        worksheet.write(row, 5, "CP", tags_data_gray_center_border)
        worksheet.write(row, 6, "No. Póliza", tags_data_gray_center_border)

        for insurance in self.insurance_ids:
            
            insurance_partner_id = insurance.insurance_partner_id
            ambiental_insurance_partner_id = insurance.ambiental_insurance_partner_id
            transport_insurance_partner_id = insurance.transport_insurance_partner_id

            if insurance_partner_id:
                country_code = ""
                zip_code = ""

                state_info = ""
                if insurance_partner_id.state_id and insurance_partner_id.state_id.code:
                    state_info = insurance_partner_id.state_id.code
               
                zip_code = ""
                if insurance_partner_id.zip_sat_id:
                    zip_code = insurance_partner_id.zip_sat_id.code
                if not zip_code:
                    zip_code = insurance_partner_id.zip

                if insurance_partner_id.country_id and insurance_partner_id.country_id.l10n_mx_edi_code:
                    country_code = insurance_partner_id.country_id.l10n_mx_edi_code

                row += 1
                worksheet.write(row, 0, "Vehículo", tags_data_gray_left_border)
                worksheet.write(row, 1, insurance_partner_id.name, normal_left_border)
                worksheet.write(row, 2, insurance_partner_id.vat, normal_left_border)
                worksheet.write(row, 3, state_info, normal_left_border)
                worksheet.write(row, 4, country_code, normal_left_border)
                worksheet.write(row, 5, zip_code, normal_left_border)
                worksheet.write(row, 6, insurance.insurance_policy, normal_left_border)

            if ambiental_insurance_partner_id:
                country_code = ""
                zip_code = ""

                state_info = ""
                if ambiental_insurance_partner_id.state_id and ambiental_insurance_partner_id.state_id.code:
                    state_info = ambiental_insurance_partner_id.state_id.code
               
                zip_code = ""
                if ambiental_insurance_partner_id.zip_sat_id:
                    zip_code = ambiental_insurance_partner_id.zip_sat_id.code
                if not zip_code:
                    zip_code = ambiental_insurance_partner_id.zip

                if ambiental_insurance_partner_id.country_id and ambiental_insurance_partner_id.country_id.l10n_mx_edi_code:
                    country_code = ambiental_insurance_partner_id.country_id.l10n_mx_edi_code

                row += 1
                worksheet.write(row, 0, "Medio Ambiente", tags_data_gray_left_border)
                worksheet.write(row, 1, ambiental_insurance_partner_id.name, normal_left_border)
                worksheet.write(row, 2, ambiental_insurance_partner_id.vat, normal_left_border)
                worksheet.write(row, 3, state_info, normal_left_border)
                worksheet.write(row, 4, country_code, normal_left_border)
                worksheet.write(row, 5, zip_code, normal_left_border)
                worksheet.write(row, 6, insurance.ambiental_insurance_policy, normal_left_border)

            if transport_insurance_partner_id:
                country_code = ""
                zip_code = ""

                state_info = ""
                if transport_insurance_partner_id.state_id and transport_insurance_partner_id.state_id.code:
                    state_info = transport_insurance_partner_id.state_id.code
               
                zip_code = ""
                if transport_insurance_partner_id.zip_sat_id:
                    zip_code = transport_insurance_partner_id.zip_sat_id.code
                if not zip_code:
                    zip_code = transport_insurance_partner_id.zip

                if transport_insurance_partner_id.country_id and transport_insurance_partner_id.country_id.l10n_mx_edi_code:
                    country_code = transport_insurance_partner_id.country_id.l10n_mx_edi_code

                row += 1
                worksheet.write(row, 0, "Carga", tags_data_gray_left_border)
                worksheet.write(row, 1, transport_insurance_partner_id.name, normal_left_border)
                worksheet.write(row, 2, transport_insurance_partner_id.vat, normal_left_border)
                worksheet.write(row, 3, state_info, normal_left_border)
                worksheet.write(row, 4, country_code, normal_left_border)
                worksheet.write(row, 5, zip_code, normal_left_border)
                worksheet.write(row, 6, insurance.transport_insurance_policy, normal_left_border)

        
        ### Ubicaciones Origen ###
        row += 3
        worksheet.write_merge(row, row, 0, 13, 'Ubicaciones Origen', heading_format_left)
        row += 2
        worksheet.write(row, 0, "Clave", tags_data_gray_center_border)
        worksheet.write(row, 1, "Nombre", tags_data_gray_center_border)
        worksheet.write(row, 2, "RFC", tags_data_gray_center_border)
        worksheet.write(row, 3, "Calle", tags_data_gray_center_border)
        worksheet.write(row, 4, "Num Ext.", tags_data_gray_center_border)
        worksheet.write(row, 5, "Número Int.", tags_data_gray_center_border)
        worksheet.write(row, 6, "Colonia (Clave SAT)", tags_data_gray_center_border)
        worksheet.write(row, 7, "CP", tags_data_gray_center_border)
        worksheet.write(row, 8, "Localidad", tags_data_gray_center_border)
        worksheet.write(row, 9, "Municipio", tags_data_gray_center_border)
        worksheet.write(row, 10, "Estado (Código SAT)", tags_data_gray_center_border)
        worksheet.write(row, 11, "País (Código)", tags_data_gray_center_border)
        worksheet.write(row, 12, "Referencias", tags_data_gray_center_border)
        worksheet.write(row, 13, "Fecha/Hora Salida", tags_data_gray_center_border)

        for location_inst in self.location_origin_ids:
            tz = self.env.user.partner_id.tz or 'Mexico/General'
            location_partner_select = location_inst.location_partner_id

            loc_partner_state = ""
            if location_partner_select.state_id and location_partner_select.state_id.code:
                loc_partner_state = location_partner_select.state_id.code

            loc_partner_country = ""
            if location_partner_select.country_id and location_partner_select.country_id.l10n_mx_edi_code:
                loc_partner_country = location_partner_select.country_id.l10n_mx_edi_code

            loc_partner_zip = ""
            if location_partner_select.zip_sat_id:
                loc_partner_zip = location_partner_select.zip_sat_id.code
            if not loc_partner_zip:
                loc_partner_zip = location_partner_select.zip
            
            #### Dirección/Domicilio ####
            loc_partner_street = location_partner_select.street_name

            loc_partner_ext_number = location_partner_select.street_number

            loc_partner_int_number = location_partner_select.street_number2

            loc_partner_colony = location_partner_select.colonia_sat_id.code if location_partner_select.colonia_sat_id else ""

            loc_partner_locality = location_partner_select.zip_sat_id.locality_sat_code.code if location_partner_select.zip_sat_id.locality_sat_code else ""


            loc_partner_township = location_partner_select.city_id.l10n_mx_edi_code if location_partner_select.city_id.l10n_mx_edi_code else ""

            loc_partner_vat = location_partner_select.vat
            if not loc_partner_vat:
                if location_partner_select.parent_id:
                    loc_partner_vat = location_partner_select.parent_id.vat
            num_reg_trib = location_partner_select.num_reg_trib
            if not num_reg_trib:
                if location_partner_select.parent_id:
                    num_reg_trib = location_partner_select.parent_id.num_reg_trib
            loc_partner_name = location_partner_select.name

            location_date_tz = location_inst.location_date and self.get_complement_server_to_local_timestamp(
                    location_inst.location_date, tz) or False

            if location_date_tz:
                location_date_tz = str(location_date_tz)[0:19]
                location_date_tz.replace(' ','T')
                date_loc = location_date_tz.split(' ')
                date_loc_tz = date_loc[0]+'T'+date_loc[1]
            else:
                date_loc_tz  = ""

            row += 1
            worksheet.write(row, 0, location_inst.id_location, tags_data_gray_left_border)
            worksheet.write(row, 1, loc_partner_name, normal_left_border)
            worksheet.write(row, 2, loc_partner_vat, normal_left_border)
            worksheet.write(row, 3, loc_partner_street, normal_left_border)
            worksheet.write(row, 4, loc_partner_int_number, normal_left_border)
            worksheet.write(row, 5, country_code, normal_left_border)
            worksheet.write(row, 6, loc_partner_colony, normal_left_border)
            worksheet.write(row, 7, loc_partner_zip, normal_left_border)
            worksheet.write(row, 8, loc_partner_locality, normal_left_border)
            worksheet.write(row, 9, loc_partner_township, normal_left_border)
            worksheet.write(row, 10, loc_partner_state, normal_left_border)
            worksheet.write(row, 11, loc_partner_country, normal_left_border)
            worksheet.write(row, 12, location_inst.location_partner_references, normal_left_border)
            worksheet.write(row, 13, date_loc_tz, normal_left_border)

        ### Ubicaciones Destino ###
        row += 3
        worksheet.write_merge(row, row, 0, 13, 'Ubicaciones Destino', heading_format_left)
        row += 2
        worksheet.write(row, 0, "Clave", tags_data_gray_center_border)
        worksheet.write(row, 1, "Nombre", tags_data_gray_center_border)
        worksheet.write(row, 2, "RFC", tags_data_gray_center_border)
        worksheet.write(row, 3, "Calle", tags_data_gray_center_border)
        worksheet.write(row, 4, "Num Ext.", tags_data_gray_center_border)
        worksheet.write(row, 5, "Número Int.", tags_data_gray_center_border)
        worksheet.write(row, 6, "Colonia (Clave SAT)", tags_data_gray_center_border)
        worksheet.write(row, 7, "CP", tags_data_gray_center_border)
        worksheet.write(row, 8, "Localidad", tags_data_gray_center_border)
        worksheet.write(row, 9, "Municipio", tags_data_gray_center_border)
        worksheet.write(row, 10, "Estado (Código SAT)", tags_data_gray_center_border)
        worksheet.write(row, 11, "País (Código)", tags_data_gray_center_border)
        worksheet.write(row, 12, "Referencias", tags_data_gray_center_border)
        worksheet.write(row, 13, "Fecha/Hora Salida", tags_data_gray_center_border)

        for location_dest in self.location_destiny_ids:
            tz = self.env.user.partner_id.tz or 'Mexico/General'
            location_partner_select = location_dest.location_partner_id

            loc_partner_state = ""
            if location_partner_select.state_id and location_partner_select.state_id.code:
                loc_partner_state = location_partner_select.state_id.code

            loc_partner_country = ""
            if location_partner_select.country_id and location_partner_select.country_id.l10n_mx_edi_code:
                loc_partner_country = location_partner_select.country_id.l10n_mx_edi_code

            loc_partner_zip = ""
            if location_partner_select.zip_sat_id:
                loc_partner_zip = location_partner_select.zip_sat_id.code
            if not loc_partner_zip:
                loc_partner_zip = location_partner_select.zip
            
            #### Dirección/Domicilio ####
            loc_partner_street = location_partner_select.street_name

            loc_partner_ext_number = location_partner_select.street_number

            loc_partner_int_number = location_partner_select.street_number2

            loc_partner_colony = location_partner_select.colonia_sat_id.code if location_partner_select.colonia_sat_id else ""

            loc_partner_locality = location_partner_select.zip_sat_id.locality_sat_code.code if location_partner_select.zip_sat_id.locality_sat_code else ""

            loc_partner_township = location_partner_select.city_id.l10n_mx_edi_code if location_partner_select.city_id.l10n_mx_edi_code else ""

            loc_partner_vat = location_partner_select.vat
            if not loc_partner_vat:
                if location_partner_select.parent_id:
                    loc_partner_vat = location_partner_select.parent_id.vat
            num_reg_trib = location_partner_select.num_reg_trib
            if not num_reg_trib:
                if location_partner_select.parent_id:
                    num_reg_trib = location_partner_select.parent_id.num_reg_trib
            loc_partner_name = location_partner_select.name

            location_date_tz = location_dest.location_date and self.get_complement_server_to_local_timestamp(
                    location_dest.location_date, tz) or False

            if location_date_tz:
                location_date_tz = str(location_date_tz)[0:19]
                location_date_tz.replace(' ','T')
                date_loc = location_date_tz.split(' ')
                date_loc_tz = date_loc[0]+'T'+date_loc[1]
            else:
                date_loc_tz = ""

            row += 1
            worksheet.write(row, 0, location_dest.id_location, tags_data_gray_left_border)
            worksheet.write(row, 1, loc_partner_name, normal_left_border)
            worksheet.write(row, 2, loc_partner_vat, normal_left_border)
            worksheet.write(row, 3, loc_partner_street, normal_left_border)
            worksheet.write(row, 4, loc_partner_int_number, normal_left_border)
            worksheet.write(row, 5, country_code, normal_left_border)
            worksheet.write(row, 6, loc_partner_colony, normal_left_border)
            worksheet.write(row, 7, loc_partner_zip, normal_left_border)
            worksheet.write(row, 8, loc_partner_locality, normal_left_border)
            worksheet.write(row, 9, loc_partner_township, normal_left_border)
            worksheet.write(row, 10, loc_partner_state, normal_left_border)
            worksheet.write(row, 11, loc_partner_country, normal_left_border)
            worksheet.write(row, 12, location_dest.location_partner_references, normal_left_border)
            worksheet.write(row, 13, date_loc_tz, normal_left_border)

        ### Mercancias ###
        row += 3
        worksheet.write_merge(row, row, 0, 19, 'Mercancias', heading_format_left)
        row += 2
        worksheet.write(row, 0, "Peso Bruto Total", tags_data_gray_center_border)
        worksheet.write(row, 1, self.weight_charge_total if self.weight_charge_total else "", normal_left_border)

        worksheet.write(row, 4, "Unidad de Peso", tags_data_gray_center_border)
        worksheet.write(row, 5, self.uom_weight_id.code if self.uom_weight_id else "", normal_left_border)

        row += 2

        worksheet.write(row, 0, "Referencia Interna", tags_data_gray_center_border)
        worksheet.write(row, 1, "Descripcion", tags_data_gray_center_border)
        worksheet.write(row, 2, "Clave Producto (SAT)", tags_data_gray_center_border)
        worksheet.write(row, 3, "Cantidad", tags_data_gray_center_border)
        worksheet.write(row, 4, "UdM Clave (SAT)", tags_data_gray_center_border)
        worksheet.write(row, 5, "Clave STC (SAT)", tags_data_gray_center_border)
        worksheet.write(row, 6, "Peso KG", tags_data_gray_center_border)
        worksheet.write(row, 7, "Largo CM", tags_data_gray_center_border)
        worksheet.write(row, 8, "Ancho CM", tags_data_gray_center_border)
        worksheet.write(row, 9, "Alto CM", tags_data_gray_center_border)
        worksheet.write(row, 10, "Material Peligroso", tags_data_gray_center_border)
        worksheet.write(row, 11, "Clave M.P.", tags_data_gray_center_border)
        worksheet.write(row, 12, "Embalaje", tags_data_gray_center_border)
        worksheet.write(row, 13, "Valor Mercancia", tags_data_gray_center_border)
        worksheet.write(row, 14, "Clave Arancel", tags_data_gray_center_border)
        worksheet.write(row, 15, "UUID Factura Comercio Ext.", tags_data_gray_center_border)
        worksheet.write(row, 16, "Cantidad Transportada", tags_data_gray_center_border)
        worksheet.write(row, 17, "Pedimento", tags_data_gray_center_border)
        worksheet.write(row, 18, "ID Origen", tags_data_gray_center_border)
        worksheet.write(row, 19, "ID Destino", tags_data_gray_center_border)
        worksheet.write(row, 20, "Numero Guia", tags_data_gray_center_border)
        worksheet.write(row, 21, "Descripción Guia", tags_data_gray_center_border)
        worksheet.write(row, 22, "Peso Guia", tags_data_gray_center_border)

        for line in self.invoice_line_complement_cp_ids:
            default_code = ""
            if line.product_id and line.product_id.default_code:
                default_code = line.product_id.default_code
            else:
                if line.product_id and not line.product_id.default_code:
                   default_code = "ID:%s" % line.product_id.id

            ### Exportación Lineas ####
            pedimentos_list = []
            if line.pedimentos_ids:
                for pedimento in line.pedimentos_ids:
                    pedimentos_list.append(pedimento.waybill_pedimento)

            cantidades_transportadas_list = []
            if line.pedimentos_ids:
                for cant_tr in line.cantidades_ids:
                    cantidad = cant_tr.cantidad if cant_tr.cantidad else 0.0
                    idorigen = cant_tr.idorigen if cant_tr.idorigen else ""
                    iddestino = cant_tr.iddestino if cant_tr.iddestino else ""
                    list_cantidad_info = [cantidad,
                                          idorigen,
                                          iddestino]
                    cantidades_transportadas_list.append(list_cantidad_info)

            ### Agregando Guias de Identificación ####
            guias_list =  []
            if line.guia_ids:
                for guia in line.guia_ids:
                    guia_data  =  [guia.numero_guia,guia.descripcion_guia,guia.peso_paquete]
                    guias_list.append(guia_data)

            extra_lines_final_list = []
            if pedimentos_list or cantidades_transportadas_list or guias_list:
                for x, y, z in zip_longest(pedimentos_list, cantidades_transportadas_list, guias_list):
                    extra_line_info = []
                    if x:
                        extra_line_info.append(x)
                    else:
                        extra_line_info.append(False)
                    if y:
                        extra_line_info.append(y)
                    else:
                        extra_line_info.append(False)
                    if z:
                        extra_line_info.append(z)
                    else:
                        extra_line_info.append(False)
                    extra_lines_final_list.append(extra_line_info)

            if extra_lines_final_list:
                i  = 0
                for extra_line in extra_lines_final_list:
                    pedimento = extra_line[0]
                    cantidad_transportada = extra_line[1]
                    guia_identificacion = extra_line[2]

                    line_data = []
                    if i == 0:
                        line_data = [
                                          str(default_code),
                                          str(line.description if line.description else ""),
                                          str(line.sat_product_id.code if line.sat_product_id else ""),
                                          str(line.quantity),
                                          str(line.sat_uom_id.code if line.sat_uom_id else ''),
                                          str(line.clave_stcc_id.code if line.clave_stcc_id else ''),
                                          str(line.weight_charge if line.weight_charge else ''),
                                          str(line.product_id.product_length if line.product_id else ''),
                                          str(line.product_id.product_height if line.product_id else ''),
                                          str(line.product_id.product_width if line.product_id else ''),
                                          str(line.hazardous_material if line.hazardous_material else ''),
                                          str(line.hazardous_key_product_id.code if line.hazardous_key_product_id else ''),
                                          str(line.tipo_embalaje_id.code if line.tipo_embalaje_id else ''),
                                          str(line.charge_value if line.charge_value else ''),
                                          str(line.fraccion_arancelaria) if line.fraccion_arancelaria else "", # Arancel
                                          str(line.comercio_ext_uuid) if line.comercio_ext_uuid else "", # UUID CE
                                          str(pedimento) if pedimento else "", # Pedimento
                                          str(cantidad_transportada[0]) if cantidad_transportada else "", # Cantidad Transportada
                                          str(cantidad_transportada[1]) if cantidad_transportada else "", # ID Origen
                                          str(cantidad_transportada[2]) if cantidad_transportada else "", # ID Destino
                                          str(guia_identificacion[0]) if guia_identificacion else "", # NumeroGuiaIdentificacion
                                          str(guia_identificacion[1]) if guia_identificacion else "", # DescripGuiaIdentificacion
                                          str(guia_identificacion[2]) if guia_identificacion else "", # PesoGuiaIdentificacion
                                    ]
                    else:
                        line_data = [
                                          "",
                                          "",
                                          "",
                                          "",
                                          "",
                                          "",
                                          "",
                                          "",
                                          "",
                                          "",
                                          "",
                                          "",
                                          "",
                                          "",
                                          "", # Arancel
                                          "", # UUID CE
                                          str(pedimento) if pedimento else "", # Pedimento
                                          str(cantidad_transportada[0]) if cantidad_transportada else "", # Cantidad Transportada
                                          str(cantidad_transportada[1]) if cantidad_transportada else "", # ID Origen
                                          str(cantidad_transportada[2]) if cantidad_transportada else "", # ID Destino
                                          str(guia_identificacion[0]) if guia_identificacion else "", # NumeroGuiaIdentificacion
                                          str(guia_identificacion[1]) if guia_identificacion else "", # DescripGuiaIdentificacion
                                          str(guia_identificacion[2]) if guia_identificacion else "", # PesoGuiaIdentificacion
                                    ]
                    i+=1
            else:
                line_data = [
                              str(default_code),
                              str(line.description if line.description else ""),
                              str(line.sat_product_id.code if line.sat_product_id else ""),
                              str(line.quantity),
                              str(line.sat_uom_id.code if line.sat_uom_id else ''),
                              str(line.clave_stcc_id.code if line.clave_stcc_id else ''),
                              str(line.weight_charge if line.weight_charge else ''),
                              str(line.product_id.product_length if line.product_id else ''),
                              str(line.product_id.product_height if line.product_id else ''),
                              str(line.product_id.product_width if line.product_id else ''),
                              str(line.hazardous_material if line.hazardous_material else ''),
                              str(line.hazardous_key_product_id.code if line.hazardous_key_product_id else ''),
                              str(line.tipo_embalaje_id.code if line.tipo_embalaje_id else ''),
                              str(line.charge_value if line.charge_value else ''),
                              str(line.fraccion_arancelaria) if line.fraccion_arancelaria else "", # Arancel
                              str(line.comercio_ext_uuid) if line.comercio_ext_uuid else "", # UUID CE
                              "", # Pedimento
                              "", # Cantidad Transportada
                              "", # ID Origen
                              "", # ID Destino
                              "", # NumeroGuiaIdentificacion
                              "", # DescripGuiaIdentificacion
                              "", # PesoGuiaIdentificacion
                            ]

            row += 1
            worksheet.write(row, 0, line_data[0], normal_left_border)
            worksheet.write(row, 1, line_data[1], normal_left_border)
            worksheet.write(row, 2, line_data[2], normal_left_border)
            worksheet.write(row, 3, line_data[3], normal_left_border)
            worksheet.write(row, 4, line_data[4], normal_left_border)
            worksheet.write(row, 5, line_data[5], normal_left_border)
            worksheet.write(row, 6, line_data[6], normal_left_border)
            worksheet.write(row, 7, line_data[7], normal_left_border)
            worksheet.write(row, 8, line_data[8], normal_left_border)
            worksheet.write(row, 9, line_data[9], normal_left_border)
            worksheet.write(row, 10, line_data[10], normal_left_border)
            worksheet.write(row, 11, line_data[11], normal_left_border)
            worksheet.write(row, 12, line_data[12], normal_left_border)
            worksheet.write(row, 13, line_data[13], normal_left_border)
            worksheet.write(row, 14, line_data[14], normal_left_border)
            worksheet.write(row, 15, line_data[15], normal_left_border)
            worksheet.write(row, 16, line_data[16], normal_left_border)
            worksheet.write(row, 17, line_data[17], normal_left_border)
            worksheet.write(row, 18, line_data[18], normal_left_border)
            worksheet.write(row, 19, line_data[19], normal_left_border)
            worksheet.write(row, 20, line_data[20], normal_left_border)
            worksheet.write(row, 21, line_data[21], normal_left_border)
            worksheet.write(row, 22, line_data[22], normal_left_border)


        invoice_name = self.name.replace('/','_') if self.name else 'SN'
        filename = ('Plantilla Datos Carta Porte '+str(invoice_name) + '.xls') 
        fp = BytesIO()
        workbook.save(fp)
        
        self.write({
                        'waybill_file': base64.encodestring(fp.getvalue()),
                        'waybill_datas_fname': filename,
                    })
        
        fp.close()
        return True