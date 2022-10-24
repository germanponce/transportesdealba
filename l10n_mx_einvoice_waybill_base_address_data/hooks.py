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

import logging
from os.path import join, dirname, realpath
import csv
from odoo import api, tools, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _load_res_country_zip_sat_code(cr, registry) # Codigos Postales
    _load_res_colonia_zip_sat_code(cr, registry) # Colonias

def _load_res_country_zip_sat_code(cr, registry):
    """Codigos Postales (Catalogo SAT)"""
    _logger.info("\nCargando: Codigos Postales (Catalogo SAT) - Puede tardar de 2 a 4 minutos (dependiendo los recursos del servidor)")
    env = api.Environment(cr, SUPERUSER_ID, {})
    csv_path = join(dirname(realpath(__file__)), 'data', 'res.country.zip.sat.code.csv')
    zip_vals_list = []
    #_logger.info("\nConstruyendo Dict: Codigos Postales (Catalogo SAT)")
    with open(csv_path, 'r') as csv_file:
        for row in csv.DictReader(csv_file, delimiter='|', 
                                  fieldnames=['xml_id', 'code', 'state_sat_code', 'township_sat_code', 'locality_sat_code']):
            state = env.ref('base.%s' % row['state_sat_code'], raise_if_not_found=False)
            township = env.ref('l10n_mx_einvoice_waybill_base_address_data.%s' % row['township_sat_code'], raise_if_not_found=False)
            locality = env.ref('l10n_mx_einvoice_waybill_base_address_data.%s' % row['locality_sat_code'], raise_if_not_found=False)
            
            zip_vals_list.append({
                'code': row['code'],
                'state_sat_code'    : state.id if state else False,
                'township_sat_code' : township.id if township else False,
                'locality_sat_code' : locality.id if locality else False,
                'xml_id'            : row['xml_id']
            })
    

    _logger.info("\nAun cargando: Codigos Postales (Catalogo SAT)")
    zip_codes = env['res.country.zip.sat.code'].create(zip_vals_list)
    #_logger.info("\nFin de Carga Base: Codigos Postales (Catalogo SAT)")
    if zip_codes:
        cr.execute('''
           INSERT INTO ir_model_data (name, res_id, module, model, noupdate)
               SELECT 
                    res_country_zip_sat_code.xml_id,
                    res_country_zip_sat_code.id,
                    'l10n_mx_einvoice_waybill_base_address_data',
                    'res.country.zip.sat.code',
                    TRUE
               FROM res_country_zip_sat_code
               WHERE res_country_zip_sat_code.id IN %s
        ''', [tuple(zip_codes.ids)])
        
        cr.execute('''
            update res_partner set zip_sat_id=res_country_zip_sat_code.id 
            from res_country_zip_sat_code 
            where res_partner.zip is not null and res_country_zip_sat_code.code = res_partner.zip
                and res_partner.zip_sat_id is null;''')

    _logger.info("\nFin Carga: Codigos Postales (Catalogo SAT)")
    
def _load_res_colonia_zip_sat_code(cr, registry):
    """Colonias (Catalogo SAT)"""
    _logger.info("\nCargando: Colonias (Catalogo SAT) - Puede tardar de 2 a 4 minutos (dependiendo los recursos del servidor)")
    env = api.Environment(cr, SUPERUSER_ID, {})
    csv_path = join(dirname(realpath(__file__)), 'data', 'res.colonia.zip.sat.code.csv')
    colonias_vals_list = []
    _logger.info("\nConstruyendo Dict: Colonias (Catalogo SAT)")

    with open(csv_path, 'r') as csv_file:
        for row in csv.DictReader(csv_file, delimiter='|', 
                                  fieldnames=['xml_id', 'code', 'name', 'zip_sat_code']):
            zip_code = env.ref('l10n_mx_einvoice_waybill_base_address_data.%s' % row['zip_sat_code'], raise_if_not_found=False)
            colonias_vals_list.append({
                'code'              : row['code'],
                'name'              : row['name'],
                'zip_sat_code'      : zip_code.id if zip_code else False,
                'xml_id'            : row['xml_id']
            })
    

    _logger.info("\nAun Cargando: Colonias (Catalogo SAT)")
    zip_codes = env['res.colonia.zip.sat.code'].create(colonias_vals_list)
    #_logger.info("\nFin de Carga Base: Colonias (Catalogo SAT)")
    if zip_codes:
        cr.execute('''
           INSERT INTO ir_model_data (name, res_id, module, model, noupdate)
               SELECT 
                    res_colonia_zip_sat_code.xml_id,
                    res_colonia_zip_sat_code.id,
                    'l10n_mx_einvoice_waybill_base_address_data',
                    'res.colonia.zip.sat.code',
                    TRUE
               FROM res_colonia_zip_sat_code
               WHERE res_colonia_zip_sat_code.id IN %s
        ''', [tuple(zip_codes.ids)])

    _logger.info("\nFin Carga: Colonias (Catalogo SAT)")
    