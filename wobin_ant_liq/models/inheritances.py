# -*- coding: utf-8 -*-
from odoo import models, fields, api


# *******************************************************************
#  Some inheritances made to Account & Res Partner Models
# *******************************************************************
class AccountPayment(models.Model):
    _inherit = 'account.payment'

    advances_ids    = fields.One2many('wobin.advances', 'payment_related_id',
                                      string='Anticipo')     
    settlements_ids = fields.One2many('wobin.settlements', 'payment_related_id',
                                      string='Liquidación')





class AccountMove(models.Model):
    _inherit = 'account.move'

    comprobations_ids = fields.One2many('wobin.comprobations', 'acc_mov_related_id',
                                        string='Comprobación')     





class ResPartner(models.Model):
    _inherit = 'res.partner'

    enterprise_id        = fields.Many2one('res.partner', 
                                           string='Empresa')
    flag_employee_active = fields.Boolean(string='Flag')