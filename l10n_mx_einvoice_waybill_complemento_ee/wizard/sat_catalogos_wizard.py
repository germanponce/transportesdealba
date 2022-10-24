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

from odoo import api, fields, models, _



class SAT_CatalogosWizard(models.TransientModel):
    _name = 'sat.catalogos.wizard'
    _description = 'Catalogos del SAT para Complemento de Carta Porte'

    catalogo = fields.Selection([
                                                ('action_waybill_parte_transporte', 'Partes Transporte'),
                                                ('action_waybill_figura_transporte', 'Figuras Transporte'),
                                                ('action_waybill_unidad_peso', 'Unidades de Peso'),
                                                ('action_waybill_tipo_contenedor', 'Tipos de Contenedor'),
                                                ('action_waybill_tipo_permiso', 'Tipos de Permiso'),
                                                ('action_waybill_tipo_embalaje', 'Tipos de Embalaje'),
                                                ('action_waybill_materiales_peligrosos', 'Materiales Peligrosos'),
                                                ('action_waybill_clave_transporte', 'Claves de Transporte'),
                                                ('action_waybill_complemento_estacion', 'Estaciones'),
                                                ('action_waybill_tipo_estacion', 'Tipos de Estacion'),
                                                ('action_waybill_configuracion_autotransporte_federal', 'Configuracion Autotransporte Federal'),
                                                ('action_waybill_tipo_remolque', 'Tipos de Remolque'),
                                                ('action_waybill_configuracion_maritima', 'Configuracion Maritima'),
                                                ('action_waybill_tipo_carga', 'Tipos de Carga'),
                                                ('action_waybill_contenedor_maritimo', 'Contenedores Maritimos'),
                                                ('action_waybill_numero_autorizacion_naviera', 'Num. Autorizacion Naviera Consignatario'),
                                                ('action_waybill_waybill_codigo_transporte_aereo', 'Codigos de Transporte Aereo'),
                                                ('action_waybill_productos_stcc', 'Productos y Servicios STCC'),
                                                ('action_waybill_tipo_servicio', 'Tipos de Servicio'),
                                                ('action_waybill_codigo_derecho_paso', 'Codigos de Derecho de Paso'),
                                                ('action_waybill_tipo_carro', 'Tipos de Carro'),
                                                # ('action_sat_country_township_codes', 'Municipios'),
                                                # ('action_sat_country_locality_codes', 'Localidades'),
                                                ('action_sat_country_zip_codes', 'Códigos Postales'),
                                                ('action_sat_colonia_zip_codes', 'Colonias'),

                                              ], string="Selecciona el Catalogo",
                                                 ondelete={
                                                    'action_waybill_parte_transporte': 'set default',
                                                    'action_waybill_figura_transporte': 'set default',
                                                    'action_waybill_unidad_peso': 'set default',
                                                    'action_waybill_tipo_contenedor': 'set default',
                                                    'action_waybill_tipo_permiso': 'set default',
                                                    'action_waybill_tipo_embalaje': 'set default',
                                                    'action_waybill_materiales_peligrosos': 'set default',
                                                    'action_waybill_clave_transporte': 'set default',
                                                    'action_waybill_complemento_estacion': 'set default',
                                                    'action_waybill_tipo_estacion': 'set default',
                                                    'action_waybill_configuracion_autotransporte_federal': 'set default',
                                                    'action_waybill_tipo_remolque': 'set default',
                                                    'action_waybill_configuracion_maritima': 'set default',
                                                    'action_waybill_tipo_carga': 'set default',
                                                    'action_waybill_contenedor_maritimo': 'set default',
                                                    'action_waybill_numero_autorizacion_naviera': 'set default',
                                                    'action_waybill_waybill_codigo_transporte_aereo': 'set default',
                                                    'action_waybill_productos_stcc': 'set default',
                                                    'action_waybill_tipo_servicio': 'set default',
                                                    'action_waybill_codigo_derecho_paso': 'set default',
                                                    'action_waybill_tipo_carro': 'set default',
                                                    'action_sat_country_zip_codes': 'set default',
                                                    'action_sat_colonia_zip_codes': 'set default',
                                                          })   

    def open_catalog(self):
        data = {
                'action_waybill_parte_transporte': {
                                                    'tree': 'waybill_parte_transporte_tree',
                                                    'form': 'waybill_parte_transporte_form',
                                                    },
                'action_waybill_figura_transporte': {
                                                    'tree': 'waybill_figura_transporte_tree',
                                                    'form': 'waybill_figura_transporte_form',
                                                    },
                'action_waybill_unidad_peso': {
                                                    'tree': 'waybill_unidad_peso_tree',
                                                    'form': 'waybill_unidad_peso_form',
                                                    },
                'action_waybill_tipo_contenedor': {
                                                    'tree': 'waybill_tipo_contenedor_tree',
                                                    'form': 'waybill_tipo_contenedor_form',
                                                    },
                'action_waybill_tipo_permiso': {
                                                    'tree': 'waybill_tipo_permiso_tree',
                                                    'form': 'waybill_tipo_permiso_form',
                                                    },
                'action_waybill_tipo_embalaje': {
                                                    'tree': 'waybill_tipo_embalaje_tree',
                                                    'form': 'waybill_tipo_embalaje_form',
                                                    },
                'action_waybill_materiales_peligrosos': {
                                                    'tree': 'waybill_materiales_peligrosos_tree',
                                                    'form': 'waybill_materiales_peligrosos_form',
                                                    },
                'action_waybill_clave_transporte': {
                                                    'tree': 'waybill_clave_transporte_tree',
                                                    'form': 'waybill_clave_transporte_form',
                                                    },
                'action_waybill_complemento_estacion': {
                                                    'tree': 'waybill_complemento_estacion_tree',
                                                    'form': 'waybill_complemento_estacion_form',
                                                    },
                'action_waybill_tipo_estacion': {
                                                    'tree': 'waybill_tipo_estacion_tree',
                                                    'form': 'waybill_tipo_estacion_form',
                                                    },
                'action_waybill_configuracion_autotransporte_federal': {
                                                    'tree': 'waybill_configuracion_autotransporte_federal_tree',
                                                    'form': 'waybill_configuracion_autotransporte_federal_form',
                                                    },
                'action_waybill_tipo_remolque': {
                                                    'tree': 'waybill_tipo_remolque_tree',
                                                    'form': 'waybill_tipo_remolque_form',
                                                    },
                'action_waybill_configuracion_maritima': {
                                                    'tree': 'waybill_configuracion_maritima_tree',
                                                    'form': 'waybill_configuracion_maritima_form',
                                                    },
                'action_waybill_tipo_carga': {
                                                    'tree': 'waybill_tipo_carga_tree',
                                                    'form': 'waybill_tipo_carga_form',
                                                    },
                'action_waybill_contenedor_maritimo': {
                                                    'tree': 'waybill_contenedor_maritimo_tree',
                                                    'form': 'waybill_contenedor_maritimo_form',
                                                    },
                'action_waybill_numero_autorizacion_naviera': {
                                                    'tree': 'waybill_numero_autorizacion_naviera_tree',
                                                    'form': 'waybill_numero_autorizacion_naviera_form',
                                                    },
                'action_waybill_waybill_codigo_transporte_aereo': {
                                                    'tree': 'waybill_waybill_codigo_transporte_aereo_tree',
                                                    'form': 'waybill_waybill_codigo_transporte_aereo_form',
                                                    },
                'action_waybill_productos_stcc': {
                                                    'tree': 'waybill_productos_stcc_tree',
                                                    'form': 'waybill_productos_stcc_form',
                                                    },
                'action_waybill_tipo_servicio': {
                                                    'tree': 'waybill_tipo_servicio_tree',
                                                    'form': 'waybill_tipo_servicio_form',
                                                    },
                'action_waybill_codigo_derecho_paso': {
                                                    'tree': 'waybill_codigo_derecho_paso_tree',
                                                    'form': 'waybill_codigo_derecho_paso_form',
                                                    },
                'action_waybill_tipo_carro': {
                                                    'tree': 'waybill_tipo_carro_tree',
                                                    'form': 'waybill_tipo_carro_form',
                                                    },
                'action_sat_country_township_codes' : {
                                                       'tree' : 'res_country_township_sat_code_tree',
                                                       'form' : 'res_country_township_sat_code_form'
                                                       },
                'action_sat_country_locality_codes' : {
                                                        'tree' : 'res_country_locality_sat_code_tree',
                                                        'form' : 'res_country_locality_sat_code_form'
                                                        },                
                'action_sat_country_zip_codes' : {
                                                        'tree' : 'res_country_zip_sat_code_tree',
                                                        'form' : 'res_country_zip_sat_code_form'
                                                        },                
                'action_sat_colonia_zip_codes' : {
                                                        'tree' : 'res_colonia_zip_sat_code_tree',
                                                        'form' : 'res_colonia_zip_sat_code_form'
                                                        },
               }
        if 'waybill' in self.catalogo:
            imd = self.env['ir.model.data']
            action = imd._xmlid_to_res_model_res_id('l10n_mx_einvoice_waybill_base.' + self.catalogo)
            action = self.env[action[0]].browse(action[1])
            list_view_id = imd._xmlid_to_res_id('l10n_mx_einvoice_waybill_base.' + data[self.catalogo]['tree'])
            form_view_id = imd._xmlid_to_res_id('l10n_mx_einvoice_waybill_base.' + data[self.catalogo]['form'])

            return {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
                'target': action.target,
                'context': action.context,
                'res_model': action.res_model,
            }
        else:
            imd = self.env['ir.model.data']
            action = imd._xmlid_to_res_model_res_id('l10n_mx_einvoice_waybill_base_address_data.' + self.catalogo)
            action = self.env[action[0]].browse(action[1])
            list_view_id = imd._xmlid_to_res_id('l10n_mx_einvoice_waybill_base_address_data.' + data[self.catalogo]['tree'])
            form_view_id = imd._xmlid_to_res_id('l10n_mx_einvoice_waybill_base_address_data.' + data[self.catalogo]['form'])

            return {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
                'target': action.target,
                'context': action.context,
                'res_model': action.res_model,
            }