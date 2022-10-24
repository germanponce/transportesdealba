# -*- encoding: utf-8 -*-


from odoo import api, fields, models, _, tools, release
from datetime import datetime
from datetime import datetime, date
from odoo.exceptions import UserError, RedirectWarning, ValidationError

## Manejo de Fechas y Horas ##
from pytz import timezone
import pytz
import base64

from xml.dom import minidom

import re

import logging
_logger = logging.getLogger(__name__)

import re


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_mx_edi_get_invoice_cfdi_values(self, invoice):
        res  = super(AccountEdiFormat, self)._l10n_mx_edi_get_invoice_cfdi_values(invoice)
        if invoice.transport_document_cfdi:
            if invoice.invoice_payment_term_id:
                invoice.invoice_payment_term_id = False
            res.update({
                         'document_type': 'T',
                         'payment_method_code': False,
                         'payment_policy': False,
                         'total_tax_details_transferred': False,
                         'total_tax_details_withholding': False,
                       })
        return res


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    @api.depends('edi_document_ids')
    def _compute_cfdi_values_extend(self):
        '''Fill the invoice fields from the cfdi values.
        '''
        attachment_obj = self.env['ir.attachment']
        for rec in self:
            if rec.move_type in ('out_invoice','out_refund'):
                if rec.transport_document_cfdi:
                    xml_data = rec._get_attach_xml_file_content()
                    if xml_data:
                        cfdi_minidom = minidom.parseString(xml_data)
                        if cfdi_minidom.getElementsByTagName('tfd:TimbreFiscalDigital'):
                            subnode = cfdi_minidom.getElementsByTagName('tfd:TimbreFiscalDigital')[0]
                            rfcprovcertif = subnode.getAttribute('RfcProvCertif') if subnode.getAttribute('RfcProvCertif') else ''
                            rec.rfcprovcertif = rfcprovcertif
                    else:
                        rec.rfcprovcertif = False
                else:
                    rec.rfcprovcertif = False
            else:
                rec.rfcprovcertif = False

    transport_document_cfdi = fields.Boolean('CFDI Traslado')
    rfcprovcertif = fields.Char('RfcProvCertif', size=64, copy=False, readonly=True,
                                 compute="_compute_cfdi_values_extend")


    def _get_attach_xml_file_content(self):
        attachment = self.env['ir.attachment'].search([('res_model', '=', 'account.move'), 
                                                       ('res_id', '=', self.id), 
                                                       ('name', 'ilike', '.xml')], order="id desc", limit=1)
        if not attachment:
            return False
        try:
            file_path = self.env['ir.attachment']._full_path('checklist').replace('checklist','') + attachment.store_fname
            attach_file = open(file_path, 'rb')
            xml_data = attach_file.read()
            attach_file.close()
            return xml_data
        except:
            _logger.error("No se pudo leer el archivo XML adjunto a esta factura, favor de revisar...")
            return False

    @api.onchange('transport_document_cfdi','move_type')
    def onchange_transport_dodument(self):
        if self.transport_document_cfdi:
            if self.transport_document_cfdi == True:
                self.l10n_mx_edi_usage = 'S01'
                self.l10n_mx_edi_payment_method_id = False
                self.invoice_payment_term_id = False
            else:
                if self.move_type in ('out_invoice','out_refund'):
                    if not self.l10n_mx_edi_usage:
                        raise UserError('Error!\nEl campo Uso CFDI es Obligatorio.')
        
    def action_post(self):
        res = super(AccountInvoice, self).action_post()   
        cr = self.env.cr
        for rec in self:
            if rec.move_type in ('out_invoice','out_refund'):
                if rec.transport_document_cfdi:
                    update_move_line_list_ids = []  
                    if rec.line_ids:  
                        for line in rec.line_ids:
                            if line.exclude_from_invoice_tab:
                                update_move_line_list_ids.append(line.id)
                        cr.execute("""
                            delete from account_move_line
                                   where id in %s;
                            """,(tuple(update_move_line_list_ids),))
        return res

    # def _post(self, soft=True):
    #     for rec in self:
    #         if rec.move_type in ('out_invoice','out_refund'):
    #             if self.transport_document_cfdi == False:
    #                 if not self.l10n_mx_edi_usage:
    #                     raise UserError('Error!\nEl campo Uso CFDI es Obligatorio.')

    #     res = super(AccountInvoice, self)._post(soft=soft)
    #     return res


    @api.constrains('transport_document_cfdi','l10n_mx_edi_payment_method_id', 'invoice_payment_term_id')
    def _constraint_transport_document(self):
        for rec in self:
            if rec.transport_document_cfdi:
                if rec.l10n_mx_edi_payment_method_id and rec.l10n_mx_edi_payment_method_id.code != '99':
                    raise UserError(_("La Factura de traslado no requiere Forma de Pago."))
                if rec.amount_total != 0.0:
                    raise UserError(_("La Factura de traslado no requiere especificar Montos, debe ser igual 0.0."))
                # if self.invoice_payment_term_id:
                #     raise UserError(_("La Factura de traslado no requiere debe contener Condiciones de Pago."))
                for line in rec.invoice_line_ids:
                    if line.tax_ids:
                        raise UserError(_("La Factura de traslado no requiere Impuestos."))
        return True


    # def _l10n_mx_edi_create_taxes_cfdi_values(self):
    #     if self.transport_document_cfdi:
    #         values = {
    #             'total_withhold': 0,
    #             'total_transferred': 0,
    #             'withholding': [],
    #             'transferred': [],
    #         }
    #         print ("### values >>>>>>>>>>> ", values)
    #         return values
    #     res  = super(AccountInvoice, self)._l10n_mx_edi_create_taxes_cfdi_values()
    #     print ("########## RES >>>>>>>>>>>>>>>> ", res)
    #     return res