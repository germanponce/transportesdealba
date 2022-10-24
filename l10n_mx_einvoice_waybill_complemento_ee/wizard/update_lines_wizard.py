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

import time
from datetime import datetime
import tempfile
import binascii
import xlrd
from datetime import date, datetime
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
import logging
_logger = logging.getLogger(__name__)
import io
try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')

try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

from itertools import zip_longest


class ImportLinesDetailWaybill(models.TransientModel):
    _name = "import.lines.detail.waybill"
    _description = "Asistente para la Importación y Actualizacion de información de Carga"

    action_type = fields.Selection([
                                    ('import', 'Importación por CSV'),
                                    ('download', 'Descarga de la Plantilla CSV'),
                                    ('export_to_invoice_line', 'Crear lineas de Factura'),
                                    ('import_to_merchandise_line', 'Crear lineas de Mercancia'),
                                    ], 
                                    string='Acción a ejecutar', default="download")
    
    file_import = fields.Binary(string="Archivo a Importar")
    file_download = fields.Binary(string="Archivo a Descargar")
    datas_fname = fields.Char('Nombre Archivo')

    def export_to_invoice_line(self):
        active_ids = self._context.get('active_ids')
        invoices = self.env['account.move'].browse(active_ids)
        invoice_line = self.env['account.move.line']
        for invoice in invoices:
            if invoice.l10n_mx_edi_cfdi_uuid:
                raise UserError("La Factura ya cuenta con Folio Fiscal.")
            if not invoice.transport_document_cfdi:
                raise UserError("Esta opción solo funciona con el CFDI de Traslado.")
            if invoice.state != 'draft':
                raise UserError("Esta opción solo puede ejecutarse en una Factura en estado Borrador.")
            if not invoice.invoice_line_complement_cp_ids:
                raise UserError("No existen lineas de Mercancia Transportada.")
            if invoice.invoice_line_ids:
                invoice.invoice_line_ids.unlink()
            for mercancia in invoice.invoice_line_complement_cp_ids:
                if mercancia.product_id:
                    fpos = invoice.fiscal_position_id
                    company = invoice.company_id
                    accounts = mercancia.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fpos)
                    account_id = accounts['income']

                    invoice_line_vals = {
                                            'product_id': mercancia.product_id.id,
                                            'product_uom_id': mercancia.product_id.uom_id.id,
                                            'name': mercancia.product_id.name_get()[0][1],
                                            'move_id': invoice.id,
                                            'account_id': account_id.id if accounts else False,
                                            'quantity': mercancia.quantity,
                                            'price_unit': 0.0,
                                        }
                    invoice_line_id = invoice_line.create(invoice_line_vals)
        return True

    def import_to_merchandise_line(self):
        active_ids = self._context.get('active_ids')
        invoices = self.env['account.move'].browse(active_ids)
        invoice_line = self.env['account.move.line']
        merchansise_line_obj = self.env['invoice.line.complement.cp']
        for invoice in invoices:
            if invoice.l10n_mx_edi_cfdi_uuid:
                raise UserError("La Factura ya cuenta con Folio Fiscal.")
            if not invoice.transport_document_cfdi:
                raise UserError("Esta opción solo funciona con el CFDI de Traslado.")
            if invoice.state != 'draft':
                raise UserError("Esta opción solo puede ejecutarse en una Factura en estado Borrador.")
            if not invoice.invoice_line_ids:
                raise UserError("No existen lineas de Factura.")
            if invoice.invoice_line_complement_cp_ids:
                invoice.invoice_line_complement_cp_ids.unlink()
            for line in invoice.invoice_line_ids:
                merchandise_vals = {
                                        'invoice_id': invoice.id,
                                        'product_id': line.product_id.id,
                                        'description': line.product_id.name,
                                        'sat_product_id': line.product_id.unspsc_code_id.id if line.product_id.unspsc_code_id else False,
                                        'quantity': line.quantity,
                                        'sat_uom_id': line.product_uom_id.unspsc_code_id.id if line.product_uom_id.unspsc_code_id else False,
                                        'weight_charge': line.product_id.weight,
                                        'dimensions_charge':  line.product_id.dimensiones_plg,
                                        'clave_stcc_id': line.product_id.clave_stcc_id.id if line.product_id.clave_stcc_id else False,
                                        'tipo_embalaje_id': line.product_id.tipo_embalaje_id.id if line.product_id.tipo_embalaje_id else False,
                                        'fraccion_arancelaria':  line.product_id.l10n_mx_edi_tariff_fraction_id.code if line.product_id.l10n_mx_edi_tariff_fraction_id else False,
                                        'hazardous_material': line.product_id.hazardous_material,

                                    }
                merchansise_line_id = merchansise_line_obj.create(merchandise_vals)
        return True
        
    def download_data(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        file_url = base_url+"/web/content?model=import.lines.detail.waybill&field=file_download&filename_field=datas_fname&id=%s&&download=true" % (self.id,)

        with open('/tmp/actualizacion_lineas_complemento.csv', 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            active_ids = self._context.get('active_ids')
            invoices = self.env['account.move'].browse(active_ids)
            for invoice in invoices:
                ### Actualizamos las Lineas ###
                invoice.refresh_complement_waybill_data()
                #product_id, quantity, sat_uom_id
                header = [
                          'referencia_interna_producto(opcional)',
                          'descripcion_mercancia(opcional)',
                          'clave_producto_sat','cantidad', 
                          'clave_udm_sat', 'clave_stcc', 'peso_kg', 
                          'largo_cm', 'ancho_cm', 'alto_cm',
                          'material_peligroso', 
                          'clave_material_peligroso', 'embalaje',
                          'valor_mercancia',
                          ######### Nuevos Datos ##########
                          'clave_arancel', 'uuid_factura_comercio_exterior',
                          'pedimento', # Pedimentos #
                          'cantidad_transportada', 'id_origen', 'id_destino', # Mercancia Transportada #
                          "numero_guia", "descripcion_guia", "peso_guia", #### Guias Identificacion
                          "enviar_mp_no_pac", ### Envia el Material Peligroso No al PAC
                          ]

                writer.writerow(header)

                for line in invoice.invoice_line_complement_cp_ids:
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
                    if line.cantidades_ids:
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

                            line_data = [[]]
                            if i == 0:
                                line_data = [[
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
                                                  str('Si') if line.force_hazardous_pac else "No", # Enviar MaterialPeligroso=No
                                            ]]
                            else:
                                line_data = [[
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
                                                  str('Si') if line.force_hazardous_pac else "No", # Enviar MaterialPeligroso=No
                                            ]]

                            writer.writerows(line_data)
                            i+=1

                    else:
                        line_data = [[
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
                                      str('Si') if line.force_hazardous_pac else "No", # Enviar MaterialPeligroso=No
                                    ]]

                        writer.writerows(line_data)

                new_line = '\n'
                writer.writerows(new_line)
        csvFile.close()

        saved_csvfile = base64.b64encode(open('/tmp/actualizacion_lineas_complemento.csv' , 'rb+').read())
        result_id = self.write({'file_download': saved_csvfile ,'datas_fname': 'Lineas Complemento CP.csv'})
        
        return {
                    'type': 'ir.actions.act_url',
                    'url': file_url,
                    'target': 'new'
                }

    def import_data(self):
        #product_id, quantity, sat_uom_id
        keys = [
                  'referencia_interna_producto(opcional)',
                  'descripcion_mercancia(opcional)',
                  'clave_producto_sat','cantidad', 
                  'clave_udm_sat', 'clave_stcc', 'peso_kg', 
                  'largo_cm', 'ancho_cm', 'alto_cm',
                  'material_peligroso', 
                  'clave_material_peligroso', 'embalaje',
                  'valor_mercancia',
                  ######### Nuevos Datos ##########
                  'clave_arancel', 'uuid_factura_comercio_exterior',
                  'pedimento', # Pedimentos #
                  'cantidad_transportada', 'id_origen', 'id_destino',# Mercancia Transportada #
                  'numero_guia', 'descripcion_guia', 'peso_guia', #### Guias Identificacion
                  "enviar_mp_no_pac", ### Envia el Material Peligroso No al PAC
                ]

        try:
            csv_data = base64.b64decode(self.file_import)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            file_reader = []
            values = {}
            csv_reader = csv.reader(data_file, delimiter=',')
            file_reader.extend(csv_reader)

        except:
            raise Warning(_("Archivo Invalido!"))

        active_ids = self._context.get('active_ids')
        invoices = self.env['account.move'].browse(active_ids)
        for invoice in invoices:
            if invoice.invoice_line_complement_cp_ids:
                invoice.invoice_line_complement_cp_ids.unlink()

        prev_line_complement_id = False
        for i in range(len(file_reader)):
            field = list(map(str, file_reader[i]))
            values = dict(zip(keys, field))
            if values:
                if i == 0:
                    continue
                else:
                    if len(field) <= 1:
                        continue
                    # transport_dangerous
                    # clave_dangerous_product_id
                    pedimento = field[16]
                    cantidad_transportada = field[17]
                    id_origen = field[18]
                    id_destino = field[19]
                    ### guias
                    numero_guia = field[20]
                    descripcion_guia = field[21]
                    peso_guia = field[22]

                    if not field[2] and not field[3] and not field[4]:
                        _logger.info("\n#### Es una Linea de Detalle (Pedimentos o Cantidad Transportada ) >>>>>>>> ")

                        ####  Creando las Lineas de Pedimento y Cantidad Transportada #####

                        if pedimento and prev_line_complement_id:
                            pedimento_vals = {
                                                'invoice_line_merchandise_id': prev_line_complement_id.id,
                                                'waybill_pedimento': str(pedimento),
                                             }
                            line_pedimento_id = self.create_pedimento_rel(pedimento_vals)

                        if cantidad_transportada and id_origen and id_destino:
                            if prev_line_complement_id:
                                cantidad_transporta_vals = {
                                                                'invoice_line_merchandise_id': prev_line_complement_id.id,
                                                                'cantidad': float(cantidad_transportada) if cantidad_transportada else 0.0,
                                                                'idorigen': str(id_origen),
                                                                'iddestino': str(id_destino),
                                                            }
                                line_cantidad_id = self.create_cant_transportada_rel(cantidad_transporta_vals)
                                
                        ##### Guias 
                        if numero_guia and descripcion_guia and peso_guia:
                            if prev_line_complement_id:
                                guia_identificacion_vals = {
                                                                'invoice_line_merchandise_id': prev_line_complement_id.id,
                                                                'peso_paquete': float(peso_guia) if peso_guia else 0.0,
                                                                'numero_guia': str(numero_guia),
                                                                'descripcion_guia': str(descripcion_guia),
                                                            }
                                guia_identificacion_id = self.create_guia_identificacion(guia_identificacion_vals)
                    else:
                        values.update({
                                        'referencia_interna_producto': field[0],
                                        'description': field[1],
                                        'clave_producto_sat': field[2],
                                        'cantidad': field[3],
                                        'clave_udm_sat': field[4],
                                        'clave_stcc' : field[5],
                                        'peso_kg'  : field[6],
                                        'largo_cm'  : field[7],
                                        'ancho_cm'  : field[8],
                                        'alto_cm'  : field[9],
                                        'material_peligroso'  : field[10],
                                        'clave_material_peligroso'  : field[11],
                                        'embalaje'  : field[12],
                                        'valor_mercancia'  : field[13],
                                        #### Nuevos Datos ####
                                        'clave_arancel'  : field[14], # fraccion_arancelaria
                                        'uuid_factura_comercio_exterior'  : field[15], # comercio_ext_uuid
                                        'enviar_mp_no_pac' : field[23], # Envia el Material Peligroso
                                        })
                        prev_line_complement_id = self.create_stcc_info(values)

                        ####  Creando las Lineas de Pedimento y Cantidad Transportada #####

                        if pedimento and prev_line_complement_id:
                            pedimento_vals = {
                                                'invoice_line_merchandise_id': prev_line_complement_id.id,
                                                'waybill_pedimento': str(pedimento),
                                             }
                            line_pedimento_id = self.create_pedimento_rel(pedimento_vals)

                        if cantidad_transportada and id_origen and id_destino:
                            if prev_line_complement_id:
                                cantidad_transporta_vals = {
                                                                'invoice_line_merchandise_id': prev_line_complement_id.id,
                                                                'cantidad': float(cantidad_transportada) if cantidad_transportada else 0.0,
                                                                'idorigen': str(id_origen),
                                                                'iddestino': str(id_destino),
                                                            }
                                line_cantidad_id = self.create_cant_transportada_rel(cantidad_transporta_vals)

                        ##### Guias 
                        if numero_guia and descripcion_guia and peso_guia:
                            if prev_line_complement_id:
                                guia_identificacion_vals = {
                                                                'invoice_line_merchandise_id': prev_line_complement_id.id,
                                                                'peso_paquete': float(peso_guia) if peso_guia else 0.0,
                                                                'numero_guia': str(numero_guia),
                                                                'descripcion_guia': str(descripcion_guia),
                                                            }
                                guia_identificacion_id = self.create_guia_identificacion(guia_identificacion_vals)

        return {'type': 'ir.actions.act_window_close'}

    def create_guia_identificacion(self, values):
        line_id = self.env['invoice.line.complement.guia'].create(values)
        return line_id

    def create_cant_transportada_rel(self,values):
        line_id = self.env['invoice.line.complement.cantidad.transporta'].create(values)
        return line_id

    def create_pedimento_rel(self,values):
        line_id = self.env['invoice.line.complement.pedimento'].create(values)
        return line_id

    def create_stcc_info(self,values):
        # invoice_line_obj = self.env['account.move.line']
        # invoice_line_id = values.get('invoice_line_id')
        # invoice_line_br = invoice_line_obj.browse(invoice_line_id)
        product_obj = self.env['product.template']
        product_product_obj = self.env['product.product']

        default_code = values.get('referencia_interna_producto', '')
        product_record = False
        if default_code:
            if 'ID:' in default_code:
                try:
                    product_id_spl = default_code.replace(' ','').split('ID:')
                    product_id = int(product_id_spl[-1])
                    product_record = product_product_obj.browse(product_id)
                except:
                    product_record = False
            else:
                product_record = self.find_product_record(default_code)

        description = values.get('description', '')

        clave_producto_sat = values.get('clave_producto_sat', '')
        sat_product_id = False
        if clave_producto_sat:
            sat_product_id = self.find_sat_product_record(clave_producto_sat)

        cantidad = values.get('cantidad', '')
        try:
            quantity = float(cantidad)
        except:
            raise UserError("Ocurrio un error durante la conversión de la cantida para el producto %s" % default_code)
        
        clave_udm_sat = values.get('clave_udm_sat', '')
        sat_uom_id = False
        if clave_udm_sat:
            sat_uom_id = self.find_sat_uom_code_record(clave_udm_sat)


        clave_stcc =  values.get('clave_stcc','')
        clave_stcc_id = False
        if clave_stcc:
            clave_stcc_id = self.find_stcc_record(clave_stcc)

        weight_charge =  values.get('peso_kg','')
        
        dimensions_charge = ""
        largo_cm = values.get('largo_cm', 0)
        ancho_cm = values.get('ancho_cm', 0)
        alto_cm = values.get('alto_cm', 0)
        if largo_cm or ancho_cm or alto_cm:
            try:
                largo_cm = float(largo_cm)
            except:
                largo_cm = 0.0
            try:
                ancho_cm = float(ancho_cm)
            except:
                ancho_cm = 0.0
            try:
                alto_cm = float(alto_cm)
            except:
                alto_cm = 0.0
            dimensions_charge = product_obj.dimensions_to_plg(largo_cm, ancho_cm, alto_cm)
        #dimensions_charge =  values.get('dimensiones')
        
        charge_value =  values.get('valor_mercancia')

        hazardous_material = values.get('material_peligroso')
        clave_material_peligroso = values.get('clave_material_peligroso')
        hazardous_key_product_id = False
        if clave_material_peligroso:
            hazardous_key_product_id = self.find_hazardous_key_record(clave_material_peligroso)

        if weight_charge:
            weight_charge = float(weight_charge)
        else:
            weight_charge = 0.0

        if charge_value:
            charge_value = float(charge_value)
        else:
            charge_value = 0.0

        active_ids = self._context.get('active_ids')

        #### Validación de los datos Importados ####
        #### Si existe un registro de Producto #####
        if product_record:
            if not sat_product_id:
                ### Campo LdM E.E.
                sat_product_id = product_record.unspsc_code_id.id if product_record.unspsc_code_id else False
            if not sat_uom_id:
                ### Campo LdM E.E.
                sat_uom_id = product_record.uom_id.unspsc_code_id.id if product_record.uom_id.unspsc_code_id else False
            if not clave_stcc_id:
                clave_stcc_id = product_record.clave_stcc_id.id if product_record.clave_stcc_id else False
            if not weight_charge:
                weight_charge = product_record.weight if product_record.weight else ''
            if not dimensions_charge:
                dimensions_charge = product_record.dimensiones_plg if product_record.dimensiones_plg else ''
            if not description:
                description = product_record.name

        #### Nuevos Datos ####
        fraccion_arancelaria = values.get('clave_arancel')
        comercio_ext_uuid = values.get('uuid_factura_comercio_exterior')
        if product_record:
            if product_record.l10n_mx_edi_tariff_fraction_id:
                fraccion_arancelaria = product_record.l10n_mx_edi_tariff_fraction_id.code

        #### Embalaje ####
        embalaje = values.get('embalaje', False)
        tipo_embalaje_id = self.find_embalaje_record(embalaje)

        enviar_mp_no_pac = values.get('enviar_mp_no_pac', 'NO')

        data={
                'product_id': product_record.id if product_record else False,
                'description': description,
                'sat_product_id' :  sat_product_id,
                'quantity' :  quantity,
                'sat_uom_id' :  sat_uom_id,
                'clave_stcc_id': clave_stcc_id,
                'weight_charge' :  weight_charge,
                'dimensions_charge': dimensions_charge,
                'hazardous_material': hazardous_material,
                'hazardous_key_product_id': hazardous_key_product_id,
                'charge_value': charge_value,
                'invoice_id': active_ids[0],
                #### Nuevos Datos ###
                'fraccion_arancelaria': fraccion_arancelaria,
                'comercio_ext_uuid': comercio_ext_uuid,
                ## Tipo Embajale ###
                'tipo_embalaje_id': tipo_embalaje_id,
                'force_hazardous_pac': True if enviar_mp_no_pac.upper() == 'SI' else False,
                }

        line_complement_obj = self.env['invoice.line.complement.cp']
        line_complement_id = line_complement_obj.create(data)

        return line_complement_id

    def find_embalaje_record(self, code):
        if not code:
            return False
        code=code.replace(' ','').replace('\n','')
        tipo_embalaje_obj = self.env['waybill.tipo.embalaje']
        #Odoo10 : Bussines Process into API Odoo v10 
        tipo_embalaje_id = tipo_embalaje_obj.search([('code','ilike',code)], limit=1)
        if not tipo_embalaje_id:
            raise UserError("No se encontro información dentro del Catálogo de Tipos de Embalajes relacionados con la clave %s" % code)
        return tipo_embalaje_id.id


    def find_product_record(self, code):
        code=code.replace(' ','').replace('\n','')
        product_obj = self.env['product.product']
        #Odoo10 : Bussines Process into API Odoo v10 
        product_id = product_obj.search([('default_code','ilike',code)], limit=1)
        if not product_id:
            return False
            # raise UserError("No se encontro información dentro del Catálogo de productos SAT relacionados con la clave %s" % code)
        return product_id

    def find_sat_product_record(self, code):
        code=code.replace(' ','').replace('\n','')
        sat_product_obj = self.env['product.unspsc.code']
        #Odoo10 : Bussines Process into API Odoo v10 
        sat_product_id = sat_product_obj.search([('code','ilike',code)], limit=1)
        if not sat_product_id:
            raise UserError("No se encontro información dentro del Catálogo de productos SAT relacionados con la clave %s" % code)
        return sat_product_id.id

    def find_sat_uom_code_record(self, code):
        sat_code_obj = self.env['product.unspsc.code']
        product_obj = self.env['product.product']
        #Odoo10 : Bussines Process into API Odoo v10 
        if code:
            code=code.replace(' ','').replace('\n','')
            sat_code_id = sat_code_obj.search([('code','ilike',code)], limit=1)
            if not sat_code_id:
                raise UserError("No se encontro información dentro del Catálogo Unidades de Medida SAT para la clave %s" % code)

        return sat_code_id.id


    def find_stcc_record(self, code):
        code=code.replace(' ','').replace('\n','')
        stcc_obj = self.env['waybill.producto.stcc']
        #Odoo10 : Bussines Process into API Odoo v10 
        stcc_id = stcc_obj.search([('code','ilike',code)], limit=1)
        if code:
            if not stcc_id:
                code = '0'+str(code)
                stcc_id = stcc_obj.search([('code','ilike',code)], limit=1)
                if not stcc_id:
                    raise UserError("No se encontro información dentro del Catálogo de productos y servicios carta porte para la clave %s" % code)
        return stcc_id.id

    def find_hazardous_key_record(self, code):
        code=code.replace(' ','').replace('\n','')
        dang_code_obj = self.env['waybill.materiales.peligrosos']
        #Odoo10 : Bussines Process into API Odoo v10 
        dang_code_id = dang_code_obj.search([('code','ilike',code)], limit=1)
        if not dang_code_id:
            code = '0'+str(code)
            dang_code_id = dang_code_obj.search([('code','ilike',code)], limit=1)
            if not dang_code_id:
                raise UserError("No se encontro información dentro del Catálogo de Materiales Peligrosos para la clave %s" % code)
        return dang_code_id.id
