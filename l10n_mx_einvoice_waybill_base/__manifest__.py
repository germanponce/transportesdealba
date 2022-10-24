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

{
    "name"      : "Catalogos Base para Complemento de Carta Porte",
    "version"   : "14.0",
    "author"    : "Argil Consulting & German Ponce Dominguez",
    "website"   : "https://www.argil.mx",
    "license"   : "Other proprietary",
    "category"  : "Localization/Mexico",
    "description": """

Comprobante Traslado
====================

Este modulo permite incorporar el CFDI de Traslado para la Facturación Electronica 4.0 con Complemento de Carta Porte.

""",
    
    "depends": [
        "base",
        ],
    "data"    : [

                'security/ir.model.access.csv',
                'views/catalogos_sat_view.xml',
                'data/waybill.tipo.remolque.csv',
                'data/waybill.configuracion.maritima.csv',
                'data/waybill.configuracion.autotransporte.federal.csv',
                'data/waybill.tipo.carga.csv',
                'data/waybill.contenedor.maritimo.csv',
                'data/waybill.codigo.transporte.aereo.csv',
                'data/waybill.producto.stcc.csv',
                'data/waybill.tipo.servicio.csv',
                'data/waybill.codigo.derecho.paso.csv',
                'data/waybill.tipo.carro.csv',
                'data/waybill.tipo.contenedor.csv',
                'data/waybill.tipo.estacion.csv',
                'data/waybill.complemento.estacion.csv',
                'data/waybill.clave.transporte.csv',
                'data/waybill.materiales.peligrosos.csv',
                'data/waybill.tipo.embalaje.csv',
                'data/waybill.tipo.permiso.csv',
                'data/waybill.unidad.peso.csv',
                'data/waybill.parte.transporte.csv',
                'data/waybill.figura.transporte.csv',
    ],

    "installable": True,
}
