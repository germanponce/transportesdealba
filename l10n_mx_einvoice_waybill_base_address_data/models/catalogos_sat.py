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


import logging
_logger = logging.getLogger(__name__)

###### Codigos Postales #########

class ResCountryZipSatCode(models.Model):
    _name = 'res.country.zip.sat.code'
    _description = 'Codigos de Codigos Postales del SAT'
    _rec_name = 'code'
    _order = 'code'


    code = fields.Char(string='Codigo', size=64, index=True)
    state_sat_code = fields.Many2one('res.country.state', string='Estado/Provincia', index=True)
    township_sat_code = fields.Many2one('res.country.township.sat.code', string='Codigo Municipio SAT', index=True)
    locality_sat_code = fields.Many2one('res.country.locality.sat.code', string='Codigo Localidad SAT', index=True)

    state_sat_code_char = fields.Char(string='Codigo Estado SAT (CADENA)', size=128)
    township_sat_code_char = fields.Char(string='Codigo Municipio SAT (CADENA)', size=128)
    locality_sat_code_char = fields.Char(string='Codigo Localidad SAT (CADENA)', size=128)
    
    xml_id = fields.Char('XML ID', help="Dummy, se usa para cargar los datos mas rapido a la BD")

    
    
    @api.depends('code', 'locality_sat_code', 'state_sat_code', 'township_sat_code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.code:
                """
                code = rec.code
                complete_name = ""
                if rec.locality_sat_code:
                    state_sat_code = rec.state_sat_code.name if rec.state_sat_code else ""
                    township_sat_code = rec.township_sat_code.name if rec.township_sat_code else ""
                    locality_sat_code = rec.locality_sat_code.name if rec.locality_sat_code else ""
                    complete_name = "[ "+str(rec.code)+" ] "+str(locality_sat_code or "")+", "+str(township_sat_code or "")+", "+str(state_sat_code or "")
                else:
                    state_sat_code = rec.state_sat_code.name if rec.state_sat_code else ""
                    township_sat_code = rec.township_sat_code.name if rec.township_sat_code else ""
                    complete_name = "[ "+str(rec.code)+" ] "+str(township_sat_code or "")+", "+str(state_sat_code or "")
                """
                complete_name = "%s%s%s" % ((rec.township_sat_code and (rec.township_sat_code.name + ', ') or ''),
                                            (rec.state_sat_code and (rec.state_sat_code.name + ' ') or ''),
                                            rec.code)
                result.append((rec.id, complete_name))
        return result

   
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = [('code', '=ilike', name.split(' ')[0] + '%')]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

        return super(ResCountryZipSatCode, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
###### Codigos Postales #########

class ResColoniaZipSatCode(models.Model):
    _name = 'res.colonia.zip.sat.code'
    _description = 'Codigos de Codigos colonias del SAT'
    _order = 'zip_sat_code, name'
    
    name = fields.Char('Nombre Colonia', size=256, index=True)    
    code = fields.Char('Codigo', size=64, index=True)
    zip_sat_code = fields.Many2one('res.country.zip.sat.code', 'Codigo Postal SAT', index=True)
    
    zip_sat_code_char = fields.Char('Codigo Colonia SAT (CHAR)', size=64, index=True)
    xml_id = fields.Char('XML ID', help="Dummy, se usa para cargar los datos mas rapido a la BD")
    
    @api.depends('code', 'name', 'zip_sat_code')
    def name_get_bkp(self):
        result = []
        for rec in self:
            if rec.name:# and rec.code and rec.zip_sat_code:
                name = str(rec.name or "") #+ "[ CP: "+str(rec.zip_sat_code.code if rec.zip_sat_code else "") + " Cod: " +str(rec.code)+" ]"
                result.append((rec.id, name))
            """    
            else:
                
                if not rec.zip_sat_code:
                    name = str(rec.name or "") + "[ Cod: "+str(rec.code)+" ]"
                    result.append((rec.id, name))
                else:
                    name = rec.name
                    result.append((rec.id, name))
            """

        return result

    
    @api.model
    def _name_search_bkp(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

        return super(ResColoniaZipSatCode, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

###### Localidades #########

class ResCountryLocalitySatCode(models.Model):
    _name = 'res.country.locality.sat.code'
    _description = 'Codigos de Localidades del SAT'

    code = fields.Char('Codigo', size=64, index=True)
    name = fields.Char('Nombre Localidad', index=True)
    state_sat_code = fields.Many2one('res.country.state', 'Estado/Provincia', index=True)

    
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                code = rec.code
                name = "[ "+code+" ] "+rec.name
                result.append((rec.id, name))
        return result

    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

        return super(ResCountryLocalitySatCode, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


###### MUNICIPIOS #########

class ResCountryTownshipSatCode(models.Model):
    _name = 'res.country.township.sat.code'
    _description = 'Codigos de Municipios del SAT'

    code = fields.Char('Codigo', size=64, index=True)
    name = fields.Char('Nombre Municipio', index=True)
    state_sat_code = fields.Many2one('res.country.state', 'Estado/Provincia', index=True)

    
    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                code = rec.code
                name = "[%s] %s" % (rec.code, rec.name)
                result.append((rec.id, name))
        return result

    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

        return super(ResCountryTownshipSatCode, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


#### Asignación de los Campos en ResPartner ####

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit ='res.partner'
    zip_sat_id      = fields.Many2one('res.country.zip.sat.code', string='CP Sat', 
                                      help='Indica el Codigo del Sat para Comercio Exterior.')
    colonia_sat_id  = fields.Many2one('res.colonia.zip.sat.code', string='Colonia Sat', 
                                      help='Indica el Codigo del Sat para Comercio Exterior.')
    country_code_rel = fields.Char('Codigo Pais', related="country_id.code")

