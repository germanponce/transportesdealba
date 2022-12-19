# -*- coding: utf-8 -*-
{
    'name': "wobin_ant_liq",
    'summary': """Módulo para la gestión de anticipos, comprobaciones y liquidaciones del área de Logística""",
    'description': """Este módulo ha sido diseñado con el fin de mejorar la experiencia en la administración
    de pagos, viajes, operadores, anticipos, gastos, comprobaciones y liquidaciones del rubro de Logística""",
    'author': "Wobin Simple Cloud",
    'website': "https://transportesdealba.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'account', 'wobin_logistics', 'contacts'],

    # always loaded
    'data': [
        #Security:
        'security/ir.model.access.csv',
        'security/adv_set_groups.xml',
        'security/security_rules.xml',

        #Views:
        'views/sequences.xml',        
        'views/advances.xml',
        'views/comprobations.xml',
        'views/concepts.xml',
        'views/settlements.xml',
        'views/inheritances.xml',
        'views/informs.xml', 
        'views/views.xml',        

        #reports
        #'reports/settlement_format.xml',                       
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,    
}