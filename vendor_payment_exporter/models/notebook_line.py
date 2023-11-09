from odoo import models, fields, api

class NotebookLineInvoice(models.Model):
    _name = 'notebook.line.invoice'
    _description = 'notebook.line.invoice'

    move_id = fields.Many2one('account.move', string='Vendor Invoice', domain=[('move_type', 'in', ('in_invoice', 'in_refund'))])
    vendor_id = fields.Many2one('res.partner', string='Vendor', compute='_compute_vendor_id', store=True, readonly=True)
    invoice_date = fields.Date(string='Invoice Date', compute='_compute_invoice_date', store=True, readonly=True)
    vendor_vat = fields.Char(string='VAT', compute='_compute_vendor_vat', store=True, readonly=True)
    vendor_bank = fields.Char(string='Bank Account', compute='_compute_vendor_bank', store=True, readonly=True)
    invoice_amount = fields.Float(string='Invoice Amount', compute='_compute_invoice_amount', store=True, readonly=True)

    vendor_payment_id = fields.Many2one('vendor.payment', string='Vendor Payment', readonly=True, copy=False)

    @api.depends('move_id')
    def _compute_vendor_id(self):
        for line in self:
            if line.move_id and line.move_id.partner_id:
                line.vendor_id = line.move_id.partner_id.id
            else:
                line.vendor_id = False

    @api.depends('move_id')
    def _compute_vendor_vat(self):
        for line in self:
            if line.move_id and line.move_id.partner_id:
                line.vendor_vat = line.move_id.partner_id.vat
            else:
                line.vendor_vat = False

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
            if line.move_id and line.move_id.partner_bank_id:
                line.vendor_bank = f"{line.move_id.partner_bank_id.currency_id.name} - {line.move_id.partner_bank_id.acc_number}"
            else:                   
                line.vendor_bank = False

    @api.depends('move_id')
    def _compute_invoice_amount(self):
        for line in self:
            if line.move_id and line.move_id.amount_total_signed:
                line.invoice_amount = line.move_id.amount_total_signed
            else:
                line.invoice_amount = 0.0


class NotebookLinePayments(models.Model):
    _name = 'notebook.line.payments'
    _description = 'notebook.line.payments'

    vendor_id = fields.Many2one('res.partner', string='Vendor')
    vendor_payment_id = fields.Many2one('vendor.payment', string='Vendor Payment', readonly=True, copy=False)
    name = fields.Many2one('account.payment', string='Payment', domain=[('partner_type', '=', 'supplier'), ('is_internal_transfer', '=', False)])
    vendor_vat = fields.Char(string='VAT', readonly=True)
    vendor_bank = fields.Char(string='Bank Account', readonly=True)
    total_invoice_amount = fields.Float(string='Total Invoice Amount', readonly=True)
    move_ids = fields.Many2many('account.move', string='Vendor Invoices', 
                                domain=[('move_type', 'in', ('in_invoice', 'in_refund'))], 
                                readonly=True)
