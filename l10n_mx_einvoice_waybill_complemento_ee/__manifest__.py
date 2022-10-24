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
    "name"      : "Complemento de Carta Porte - EE",
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
        "l10n_mx_edi",
        "l10n_mx_edi_extended",
        "l10n_mx_edi_40",
        "l10n_mx_edi_extended_40",
        "product_unspsc",
        "l10n_mx_einvoice_waybill_base",
        "l10n_mx_einvoice_waybill_base_address_data",
        ],
    "data"    : [

                'security/ir.model.access.csv',
                'wizard/update_lines_wizard_view.xml',
                'wizard/sat_catalogos_wizard_view.xml',
                'views/account_view.xml',
                'views/product_view.xml',
                'views/res_partner_view.xml',
                'data/waybill_complement.xml',
                'reports/invoice_facturae.xml',
    ],
        "installable": True,
}
