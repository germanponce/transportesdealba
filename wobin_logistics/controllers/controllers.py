# -*- coding: utf-8 -*-
from odoo import http

# class WobinLogistics(http.Controller):
#     @http.route('/wobin_logistics/wobin_logistics/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wobin_logistics/wobin_logistics/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wobin_logistics.listing', {
#             'root': '/wobin_logistics/wobin_logistics',
#             'objects': http.request.env['wobin_logistics.wobin_logistics'].search([]),
#         })

#     @http.route('/wobin_logistics/wobin_logistics/objects/<model("wobin_logistics.wobin_logistics"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wobin_logistics.object', {
#             'object': obj
#         })