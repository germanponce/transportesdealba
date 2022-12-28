# -*- coding: utf-8 -*-
from odoo import models, fields


class WobinConcepts(models.Model):
    _name = 'wobin.concepts'
    _description = 'Wobin Conceptos'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 



    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    #                                     FIELDS
    #°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    name               = fields.Char(string='Concepto', 
                                     track_visibility='always')
    account_account_id = fields.Many2one('account.account', 
                                         string='Cuenta Contable', 
                                         track_visibility='always', 
                                         ondelete='cascade')
    credit_flag = fields.Boolean(string='Concepto como Crédito/Haber')
    company_id  = fields.Many2one('res.company', 
                                  default=lambda self: self.env['res.company']._company_default_get('wobin_ant_liq'))