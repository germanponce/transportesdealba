# -*- coding: utf-8 -*-
from odoo import http

# class WobinAnticiposLiquidaciones(http.Controller):
#     @http.route('/wobin_anticipos_liquidaciones/wobin_anticipos_liquidaciones/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wobin_anticipos_liquidaciones/wobin_anticipos_liquidaciones/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wobin_anticipos_liquidaciones.listing', {
#             'root': '/wobin_anticipos_liquidaciones/wobin_anticipos_liquidaciones',
#             'objects': http.request.env['wobin_anticipos_liquidaciones.wobin_anticipos_liquidaciones'].search([]),
#         })

#     @http.route('/wobin_anticipos_liquidaciones/wobin_anticipos_liquidaciones/objects/<model("wobin_anticipos_liquidaciones.wobin_anticipos_liquidaciones"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wobin_anticipos_liquidaciones.object', {
#             'object': obj
#         })