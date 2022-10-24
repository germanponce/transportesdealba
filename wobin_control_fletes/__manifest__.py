# -*- coding: utf-8 -*-
{
    'name': "wobin_control_fletes",
    'summary': """Wobin Control Fletes""",
    'description': """Gestión de los fletes con el fin de auxiliar el control de transferencias de Inventario""",
    'author': "Sebastian Ayala Mendez",
    'website': "https://fertinova.odoo.com/web",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.1.0.1',
    # any module necessary for this one to work correctly
    'depends': ['account', 'purchase_stock'],
    # always loaded
    'data': [
        #security
        'security/ir.model.access.csv',
        'security/logistics_groups.xml',

        #Views:
        'views/control_fletes.xml',
        'views/privileges.xml',

        #reports 
        'reports/reporte_orden_servicio_fletes.xml',         
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,    
}
