from odoo import models, fields, api

class NotebookLine(models.Model):
    _name = 'notebook.line'
    _description = 'notebook.line'

    move_id = fields.Many2one('account.move', string='Vendor Invoice', domain=[('move_type', 'in', ('in_invoice', 'in_refund'))])
    vendor_id = fields.Many2one('res.partner', string='Vendor', compute='_compute_vendor_id', store=True, readonly=True)
    invoice_date = fields.Date(string='Invoice Date', compute='_compute_invoice_date', store=True, readonly=True)
    vendor_vat = fields.Char(string='VAT', compute='_compute_vendor_vat', store=True, readonly=True)
    vendor_bank = fields.Char(string='Bank Account', compute='_compute_vendor_bank', store=True, readonly=True)

    vendor_payment_id = fields.Many2one('vendor.payment', string='Vendor Payment', readonly=True, copy=False)

    @api.depends('move_id')
    def _compute_vendor_id(self):
        for line in self:
            if line.move_id and line.move_id.partner_id:
                line.vendor_id = line.move_id.partner_id.id
            else:
                line.vendor_id = False

    @api.depends('move_id')
    def _compute_invoice_date(self):
        for line in self:
            if line.move_id and line.move_id.invoice_date:
                line.invoice_date = line.move_id.invoice_date
            else:
                line.invoice_date = False

    @api.depends('move_id')
    def _compute_vendor_bank(self):
        for line in self:
            if line.move_id and line.move_id.partner_id and line.move_id.partner_id.bank_ids:
                line.vendor_bank = line.move_id.partner_id.bank_ids
            else:
                line.vendor_bank = False
