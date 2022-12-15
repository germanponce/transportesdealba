# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api


# *******************************************************************
#  Some inheritances made to Account Models
# *******************************************************************

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    advance_id    = fields.Many2one('wobin.advances', string='Advance')     
    settlement_id = fields.Many2one('wobin.settlements', string='Settlement')

    @api.model
    def create(self, vals):
        #Try to modify flow in order to upate state in possible settlement related:
        res = super(AccountPayment, self).create(vals)

        #If a new record was created successfully and settlement related exists
        #update that settlement in order to change its state to 'settled':
        if res.settlement_id:
            settlement_obj = self.env['wobin.settlements'].browse(res.settlement_id.id)
            settlement_obj.update({'state': 'ready'})                   
        return res    




class AccountMove(models.Model):
    _inherit = 'account.move'

    settlement_id   = fields.Many2one('wobin.settlements', string='Settlement')
    comprobation_id = fields.Many2one('wobin.comprobations', string='Comprobation')    

    @api.model
    def create(self, vals):
        #Try to modify flow in order to upate state in possible settlement related:
        res = super(AccountMove, self).create(vals)

        #If a new record was created successfully and settlement related exists
        #update that settlement in order to change its state to 'settled':
        if res.settlement_id:
            settlement_obj = self.env['wobin.settlements'].browse(res.settlement_id.id)
            settlement_obj.update({'state': 'ready'})        
        return res
    




#class AccountMoveLine(models.Model):
    #_inherit = 'account.move.line'

    #contact_deb_cred_id = fields.Many2one('res.partner', string='Contact Debtor/Creditor')
    




class ResPartner(models.Model):
    _inherit = 'res.partner'

    #contact_id = fields.Many2one('res.partner', string='Contact')
    enterprise_id = fields.Many2one('res.partner', string='Enterprise')
    flag_employee_active  = fields.Boolean(string='Flag')