# -*- coding: utf-8 -*-

{
    "name"      : "Catalogos Base para Complemento de Carta Porte - Complemento Dirección",
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
        "l10n_mx_einvoice_waybill_base",
        ],
    "data"    : [

                'security/ir.model.access.csv',
                'views/catalogos_sat_view.xml',
                'data/res.country.township.sat.code.csv', 
                "data/res.country.locality.sat.code.csv",
                # "data/res.country.zip.sat.code.csv",
                # "data/res.colonia.zip.sat.code.csv",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
