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

_inch = 0.39370#

class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit ='product.template'

    @api.depends('product_length', 'product_height', 'product_width')
    def _get_dimensions_waybill(self):
        for rec in self:
            dimensions = ""
            dimensions = rec.dimensions_to_plg(rec.product_length,
                                                rec.product_height,
                                                rec.product_width)
            rec.dimensiones_plg = dimensions

    clave_stcc_id = fields.Many2one('waybill.producto.stcc', 'Clave STCC')
    tipo_embalaje_id  =  fields.Many2one('waybill.tipo.embalaje', 'Tipo de Embalaje')

    product_length = fields.Float("Largo", digits=(14,3))
    product_height = fields.Float("Ancho", digits=(14,3))
    product_width = fields.Float("Alto", digits=(14,3))

    dimensiones_plg = fields.Char('Dimensiones Pulgadas', compute="_get_dimensions_waybill")

    hazardous_material = fields.Selection([('Sí','Sí'),('No','No')], string="Material Peligroso", default="No" )
    
    hazardous_key_product_id = fields.Many2one('waybill.materiales.peligrosos', 'Clave Material Peligroso')

    ######### Materiales Peligrosos ########
    force_hazardous_pac = fields.Boolean("Enviar Valor MP (PAC)", help="Indica si enviaremos el valor de Material Peligroso 'No'  dentro del XML,\
        este valor puede ser obligatorio con algunos PAC que manejan las claves genericas donde el Material Peligroso es 0,1.")
    
    def dimensions_to_plg(self, length, height, width):
        dimensions_string = ""
        if length:
            length_convert = length * _inch
            if length_convert <= 9:
                length_convert_string = "0"+"%.0f" % length_convert
            else:
                length_convert_string = "%.0f" % length_convert
            dimensions_string = length_convert_string+"/"
        else:
            dimensions_string = "0/"
        if height:
            height_convert = height * _inch
            if height_convert <= 9:
                height_convert_string = "0"+"%.0f" % height_convert
            else:
                height_convert_string = "%.0f" % height_convert
            dimensions_string = dimensions_string + height_convert_string+"/"
        else:
            dimensions_string = dimensions_string+"0/"
        if width:
            width_convert = width * _inch
            if width_convert <= 9:
                width_convert_string = "0"+"%.0f" % width_convert
            else:
                width_convert_string = "%.0f" % width_convert
            dimensions_string = dimensions_string + width_convert_string
        else:
            dimensions_string = dimensions_string+"0"
        dimensions_string = dimensions_string + 'plg'
        return dimensions_string

# class ProductProduct(models.Model):
#     _name = 'product.product'
#     _inherit ='product.product'

#     @api.depends('product_length', 'product_height', 'product_width')
#     def _get_dimensions_waybill(self):
#         for rec in self:
#             dimensions = ""
#             dimensions = self.dimensions_to_plg(self.product_length,
#                                                 self.product_height,
#                                                 self.product_width)
#             rec.dimensiones_plg = dimensions

#     clave_stcc_id = fields.Many2one('waybill.producto.stcc', 'Clave STCC')

#     product_length = fields.Float("Largo", digits=(14,3))
#     product_height = fields.Float("Ancho", digits=(14,3))
#     product_width = fields.Float("Alto", digits=(14,3))

#     dimensiones_plg = fields.Char('Dimensiones Pulgadas', compute="_get_dimensions_waybill")

#     def dimensions_to_plg(self, length, height, width):
#         dimensions_string = ""
#         if length:
#             length_convert = length * _inch
#             if length_convert <= 9:
#                 length_convert_string = "0"+"%.0f" % length_convert
#             else:
#                 length_convert_string = "%.0f" % length_convert
#             dimensions_string = length_convert_string+"/"
#         else:
#             dimensions_string = "0/"
#         if height:
#             height_convert = height * _inch
#             if height_convert <= 9:
#                 height_convert_string = "0"+"%.0f" % height_convert
#             else:
#                 height_convert_string = "%.0f" % height_convert
#             dimensions_string = dimensions_string + height_convert_string+"/"
#         else:
#             dimensions_string = dimensions_string+"0/"
#         if width:
#             width_convert = width * _inch
#             if width_convert <= 9:
#                 width_convert_string = "0"+"%.0f" % width_convert
#             else:
#                 width_convert_string = "%.0f" % width_convert
#             dimensions_string = dimensions_string + width_convert_string
#         else:
#             dimensions_string = dimensions_string+"0"
#         dimensions_string = dimensions_string + 'plg'
#         return dimensions_string
#             