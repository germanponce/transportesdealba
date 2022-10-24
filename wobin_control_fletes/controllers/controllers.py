# -*- coding: utf-8 -*-
from odoo import http

# class ControlFletes(http.Controller):
#     @http.route('/control_fletes/control_fletes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/control_fletes/control_fletes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('control_fletes.listing', {
#             'root': '/control_fletes/control_fletes',
#             'objects': http.request.env['control_fletes.control_fletes'].search([]),
#         })

#     @http.route('/control_fletes/control_fletes/objects/<model("control_fletes.control_fletes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('control_fletes.object', {
#             'object': obj
#         })