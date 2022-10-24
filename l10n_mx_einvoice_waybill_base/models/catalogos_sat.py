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

###### Parte Transporte ######

class WaybillParteEmbalaje(models.Model):
    _name = "waybill.parte.transporte"
    _description = "Carta Porte -  Parte Transporte"
    _rec_name = 'code' 

    code      = fields.Char("Clave de designación", required=True, size=128 )
    name            = fields.Char('Descripción', size=128, required=True )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

        return super(WaybillParteEmbalaje, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
                result.append((rec.id, name))
        return result

###### Figura Transporte ######

class WaybillFiguraTransporte(models.Model):
    _name = "waybill.figura.transporte"
    _description = "Carta Porte -  Figura Transporte"
    _rec_name = 'code' 

    code      = fields.Char("Clave de designación", required=True, size=128 )
    name            = fields.Char('Descripción', size=128, required=True )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

        return super(WaybillFiguraTransporte, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
                result.append((rec.id, name))
        return result
        
###### Unidades Peso ######

class WaybillUnidadPeso(models.Model):
    _name = "waybill.unidad.peso"
    _description = "Carta Porte - Unidades de Peso"
    _rec_name = 'code' 

    code      = fields.Char("Clave", required=True, size=128 )
    name      = fields.Char('Descripción', size=128, required=True )
    comments  = fields.Text('Notas')
    start_date  = fields.Date(string="Inicio de Vigencia", required=False, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    simbol      = fields.Char('Simbolo', size=128, required=False )
    bandera     = fields.Char('Bandera', size=128, required=False )

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

        return super(WaybillUnidadPeso, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
                result.append((rec.id, name))
        return result

###### Tipo de Permiso ######

class WaybillTipoPermiso(models.Model):
    _name = "waybill.tipo.permiso"
    _description = "Carta Porte - Tipos de Permiso"
    _rec_name = 'code' 

    code      = fields.Char("Clave", required=True, size=128 )
    name      = fields.Char('Descripción', size=128, required=True )
    transport_key = fields.Char('Clave transporte', size=128, required=False )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

        return super(WaybillTipoPermiso, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
                result.append((rec.id, name))
        return result


###### Tipo de Embalaje ######

class WaybillTipoEmbalaje(models.Model):
    _name = "waybill.tipo.embalaje"
    _description = "Carta Porte -  Tipos de Embalajes"
    _rec_name = 'code' 

    code      = fields.Char("Clave de designación", required=True, size=128 )
    name            = fields.Char('Descripción', size=128, required=True )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]
    
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
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

        return super(WaybillTipoEmbalaje, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


###### Materiales Peligrosos ######

class WaybillMaterialesPeligrosos(models.Model):
    _name = "waybill.materiales.peligrosos"
    _description = "Carta Porte - Catalogo de Materiales Peligrosos"
    _rec_name = 'code' 

    code      = fields.Char("Clave material", required=True, size=128 )
    name      = fields.Char('Descripción', size=128, required=True )
    class_div      = fields.Char('Clase o div.  ', size=128, )
    danger_sec      = fields.Char('Peligro  secundario', size=128, )
    group_env_onu = fields.Char('Grupo de emb/env ONU', size=128)
    group_env_onu_disp_esp = fields.Char('Disp. espec.', size=128)

    qty_limit = fields.Char('Cantidades limitadas', size=128)
    qty_except = fields.Char('Cantidades exceptuadas', size=128)

    ### Embalajes/envases y RIG ####
    int_emb_env = fields.Char('Inst. de  emb/env', size=128, help="Embalajes/envases y RIG")
    int_emb_env_disp_esp = fields.Char('Disp. espec.', size=128, help="Embalajes/envases y RIG")

    ### Cisternas portátiles y contenedores para graneles ####
    int_trasp = fields.Char('Inst. de transp.', size=128, help="Cisternas portátiles y contenedores para graneles")
    int_trasp_disp_esp = fields.Char('Disp. espec.', size=128, help="Cisternas portátiles y contenedores para graneles")

    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'CHECK(1=1)',
         'El Código debe ser único')]


    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

        return super(WaybillMaterialesPeligrosos, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
                result.append((rec.id, name))
        return result



###### Tipo de Remolque ######

class WaybillClaveTransporte(models.Model):
    _name = "waybill.clave.transporte"
    _description = "Carta Porte -  Claves de Transporte"
    _rec_name = 'code' 

    code      = fields.Char("Clave", required=True, size=128 )
    name            = fields.Char('Descripción del tipo de transporte', size=128, required=True )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]
    
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
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

        return super(WaybillClaveTransporte, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


###### Estación ######
class WaybillComplementoEstacion(models.Model):
    _name = "waybill.complemento.estacion"
    _description = "Carta Porte - Estaciones"
    _rec_name = 'code' 

    code      = fields.Char("Clave transporte", required=True, size=128 )
    code_identification = fields.Char("Clave identificación", required=True, size=128 )
    name      = fields.Char('Descripción', size=128, required=True )
    nationality      = fields.Char('Nacionalidad', size=128, required=True )
    designer_iata = fields.Char('Designador IATA', size=128)
    iron_line = fields.Char('Línea férrea', size=128)
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code_identification)',
         'El Código debe ser único')]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code_identification', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

        return super(WaybillComplementoEstacion, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    @api.depends('name', 'code', 'code_identification')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+'/'+rec.code_identification+' ]' + ' ' + rec.name
                result.append((rec.id, name))
        return result

###### Tipo de Estación ######

class WaybillTipoEstacion(models.Model):
    _name = "waybill.tipo.estacion"
    _description = "Carta Porte - Tipos de Estaciones"
    _rec_name = 'code' 

    code      = fields.Char("Clave", required=True, size=128 )
    name      = fields.Char('Descripción del tipo de estación', size=128, required=True )
    charge_key = fields.Char('Clave transporte', size=128, required=False )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

        return super(WaybillTipoEstacion, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
  

    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
                result.append((rec.id, name))
        return result

###### Tipo de Remolque ######
class WaybillConfiguracionAutotransporteFederal(models.Model):
    _name = "waybill.configuracion.autotransporte.federal"
    _description = "Carta Porte -  Configuración de Autotransporte Federal"
    _rec_name = 'code' 

    code      = fields.Char("Clave nomenclatura", required=True, size=128 )
    name      = fields.Char('Descripción', size=128, required=True )
    axis_number = fields.Char('Numero de Ejes', size=128, required=False )
    tires_number = fields.Char('Numero de Llantas', size=128, required=False )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

        return super(WaybillConfiguracionAutotransporteFederal, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
                result.append((rec.id, name))
        return result


###### Tipo de Remolque ######
class WaybillTipoRemolque(models.Model):
    _name = "waybill.tipo.remolque"
    _description = "Carta Porte -  Tipos Remolque"
    _rec_name = 'code' 

    code      = fields.Char("Clave", required=True, size=128 )
    name            = fields.Char('Descripción', size=128, required=True )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]
    
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
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

        return super(WaybillTipoRemolque, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

###### Configuracion Maritima ######
class WaybillConfiguracionMaritima(models.Model):
    _name = "waybill.configuracion.maritima"
    _description = "Carta Porte - Configuracion Maritima"
    _rec_name = 'code' 

    code      = fields.Char("Clave", required=True, size=128 )
    name            = fields.Char('Descripción', size=128, required=True )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]
    
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
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

        return super(WaybillConfiguracionMaritima, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


###### Tipo de Carga ######
class WaybillTipoCarga(models.Model):
    _name = "waybill.tipo.carga"
    _description = "Carta Porte -  Tipos de Carga"
    _rec_name = 'code' 

    code      = fields.Char("Clave", required=True, size=128 )
    name            = fields.Char('Descripción', size=128, required=True )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]
    
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
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

        return super(WaybillTipoCarga, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


###### Numero de Autorizacion Naviero Consignatario ######
class WaybillNumeroAutorizacionNaviera(models.Model):
    _name = "waybill.numero.autorizacion.naviera"
    _description = "Carta Porte -  Numero de Autorizacion Naviero Consignatario"
    _rec_name = 'code' 

    code      = fields.Char("Número de Autorización", required=True, size=128 )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El numero de autorizacion debe ser único')]


###### Codigos de Transporte Aereo ######
# Clave identificación
# Nacionalidad
# Nombre de la aerolínea
# Designador OACI 
# Fecha de inicio de vigencia 
# Fecha de fin de vigencia

class WaybillCodigosTransporteAereo(models.Model):
    _name = "waybill.codigo.transporte.aereo"
    _description = "Carta Porte -  Codigos de Transporte Aereo"
    _rec_name = 'code' 

    code      = fields.Char("Clave", required=True, size=128 )
    country_nationality = fields.Char('Nacionalidad', size=128, required=True )
    name      = fields.Char('Nombre Aerolinea', size=128, required=True )
    oaci_name = fields.Char('Designador OACI', size=128, required=True )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date   = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]
    
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code and rec.country_nationality:
                name = '[ '+rec.code+' ] ' + rec.country_nationality+" / " + rec.name
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

        return super(WaybillCodigosTransporteAereo, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


###### Contenedor Maritimo ######
class WaybillContenedorMaritimo(models.Model):
    _name = "waybill.contenedor.maritimo"
    _description = "Carta Porte -  Contenedor Maritimo"
    _rec_name = 'code' 

    code      = fields.Char("Clave", required=True, size=128 )
    name            = fields.Char('Descripción', size=128, required=True )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]
    
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
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

        return super(WaybillContenedorMaritimo, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


###### Productos y Servicios STCC ######
class WaybillProductoSTCC(models.Model):
    _name = "waybill.producto.stcc"
    _description = "Carta Porte -  Productos y Servicios STCC"
    _rec_name = 'code' 

    code      = fields.Char("Clave STCC", required=True, size=128 )
    name            = fields.Char('Descripción', size=128, required=True )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]
    
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
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

        return super(WaybillProductoSTCC, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


###### Tipos de Servicio ######

class WaybillTipoServicio(models.Model):
    _name = "waybill.tipo.servicio"
    _description = "Carta Porte -  Tipos de Servicio"
    _rec_name = 'code' 

    code      = fields.Char("Clave", required=True, size=128 )
    name            = fields.Char('Descripción', size=128, required=True )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]
    
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
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

        return super(WaybillTipoServicio, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


###### Tipos de Servicio ######
# id  code    name    between stop_to grant_receive   concessionaire  date_start

class WaybillCodigoDerechoPaso(models.Model):
    _name = "waybill.codigo.derecho.paso"
    _description = "Carta Porte -  Codigos Derecho de Paso"
    _rec_name = 'code' 

    code      = fields.Char("Clave", required=True, size=128 )
    name      = fields.Char('Derecho de Paso', size=128, required=True )
    between   = fields.Char('Entre', size=128, required=True )
    stop_to   = fields.Char('Hasta', size=128, required=True )
    grant_receive = fields.Char('Otorga/Recibe', size=128, required=True )
    concessionaire = fields.Char('Concesionario', size=128, required=True )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date   = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]
    
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code:
                name = '[ '+rec.code+' ]' + ' ' + rec.name
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

        return super(WaybillCodigoDerechoPaso, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


###### Tipos de Carro ######

class WaybillTipoCarro(models.Model):
    _name = "waybill.tipo.carro"
    _description = "Carta Porte -  Tipos de Carro"
    _rec_name = 'code' 

    code      = fields.Char("Clave", required=True, size=128 )
    type      = fields.Char('Tipo', size=128, required=True )
    name      = fields.Char('Descripción', size=128 )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]
    
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code and rec.type:
                name = '[ '+rec.code+' ] ' + rec.type+" / " + rec.name
                result.append((rec.id, name))
            elif rec.code and rec.type:
                name = '[ '+rec.code+' ] ' + rec.type
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

        return super(WaybillTipoCarro, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)


###### Tipos de Contenedor ######

class WaybillTipoContenedeor(models.Model):
    _name = "waybill.tipo.contenedor"
    _description = "Carta Porte -  Tipos de Contenedor"
    _rec_name = 'code' 

    code      = fields.Char("Clave", required=True, size=128 )
    type      = fields.Char('Tipo', size=128, required=True )
    name      = fields.Char('Descripción', size=128 )
    # patente_id      = fields.Many2one('sat.patente', string="Patente Aduanal", required=True )
    start_date = fields.Date(string="Inicio de Vigencia", required=True, default="2021-06-01")
    end_date    = fields.Date(string="Fin de Vigencia", required=False)
    

    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'El Código debe ser único')]
    
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.code and rec.type:
                name = '[ '+rec.code+' ] ' + rec.type+" / " + rec.name
                result.append((rec.id, name))
            elif rec.code and rec.type:
                name = '[ '+rec.code+' ] ' + rec.type
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

        return super(WaybillTipoContenedeor, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

