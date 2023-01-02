# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountAnalyticTag(models.Model):
    _inherit = "account.analytic.tag"

    #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # Aggregation of a new selection field in Analytic Tags to manage types
    #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::       
    analytic_tag_type = fields.Selection([('trip', 'Viaje'), 
                                          ('route', 'Ruta'), 
                                          ('operator', 'Operador')], 
                                         string='Tipo de Etiqueta Analítica')                                                               
                                               


    

class AccountMove(models.Model):
    _inherit = "account.move"

    #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # Aggregation of new relational fields
    #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::  
    trips_acc_move_ids = fields.One2many('wobin.logistics.trips', 'account_move_id',
                                         string='Viaje')                                                                                

    



class SaleOrder(models.Model):
    _inherit = "sale.order"

    #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # Aggregation of a new many2one field of Trips in Sale Orders
    #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::   
    trips_sales_ids = fields.One2many('wobin.logistics.trips', 'sale_order_id', 
                                      string='Viaje')                                    
    
    
    #SQL Constraint in order to avoid duplicate trips in different Order Sales:
    """
    _sql_constraints = [('viajes_no_duplicados', 
                         'unique (trips_id)',     
                         'Este viaje está duplicado, ya se asignó en otra Orden de Venta.')]  
    """