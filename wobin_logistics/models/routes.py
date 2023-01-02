# -*- coding: utf-8 -*- 
from odoo import models, fields
 

class WobinLogisticsRoutes(models.Model):
    _name = 'wobin.logistics.routes'
    _description = 'Wobin Logística Rutas'


    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                     FIELDS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    name       = fields.Char(string="Ciudad a añadir para Orígenes y Destinos")
    company_id = fields.Many2one('res.company', 
                                 default=lambda self: self.env['res.company']._company_default_get('wobin_logistics'))    
    