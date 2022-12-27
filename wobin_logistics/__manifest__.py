# -*- coding: utf-8 -*-
{
    'name': "wobin_logistics",

    'summary': """Gestión del Área de Logística para Transportes de Alba""",

    'description': """Esta aplicación busca brindar una nueva herramienta para
     para dar una mejor administración de fletes, transportes, gastos, documentos 
     comerciales y contables en los procesos de Transportes de Alba""",

    'author': "Wobin Simple Cloud",
    'website': "https://transportesdealba.odoo.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'sale', 'purchase', 'stock', 'contacts'],

    # always loaded
    'data': [        
        #security
        'security/ir.model.access.csv',
        'security/logistics_groups.xml',
        'security/security_rules.xml',

        #views
        'views/sequences.xml',
        'views/routes.xml',        
        'views/contracts.xml',
        'views/trips.xml',
        'views/vehicles.xml',
        'views/inheritances.xml',
        'views/reports.xml',
        'views/views.xml',
        #'views/privileges.xml',

        #reports
        'reports/contract_conditions.xml',
        'reports/waybill.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}