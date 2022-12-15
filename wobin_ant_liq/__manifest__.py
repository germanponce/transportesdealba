# -*- coding: utf-8 -*-
{
    'name': "wobin_ant_liq",
    'summary': """Module for management of advances and settlements""",
    'description': """This module has been intended in order to improve experience in administration
    of payments, cycles, operators, expenses and settlements""",
    'author': "Wobin Simple Cloud",
    'website': "https://fertinova.odoo.com",

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

        #Views:
        'views/sequences.xml',        
        'views/advances.xml',
        'views/comprobations.xml',
        'views/settlements.xml',
        'views/inheritances.xml',
        'views/informs.xml', 
        'views/views.xml',        

        #reports
        #'reports/liquidacion_formato.xml',                       
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,    
}