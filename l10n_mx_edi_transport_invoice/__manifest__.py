# -*- coding: utf-8 -*-

{
    "name"      : "Comprobante Electronico para Traslados (EE)",
    "version"   : "1.0",
    "author"    : "German Ponce Dominguez",
    "website"   : "https://www.argil.mx",
    "license"   : "Other proprietary",
    "category"  : "Localization/Mexico",
    "description": """

Comprobante Traslado
====================

Este modulo permite incorporar el CFDI de Traslado para la Facturación Electronica 4.0

""",
    
    "depends": [
        "l10n_mx_edi",
        "l10n_mx_edi_40",
        ],
    "data"    : [
                 "account_invoice_view.xml",
                 "report_invoice_facturae.xml",
                 # "data/transport_complement.xml",
    ],
    "installable": True,
}
