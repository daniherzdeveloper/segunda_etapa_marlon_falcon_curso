from odoo import models, fields, api

class VendorPayment(models.Model):
    _name = 'vendor.payment'
    _description = 'Vendor Payments'

    name = fields.Char('name', default='New', readonly=1)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    total_invoice_amount = fields.Float(string='Total Invoice Amount', compute='_compute_total_invoice_amount', store=True)
    payment_journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True)
    created_by_user_id = fields.Many2one('res.users', string='Created by', default=lambda self: self.env.user, readonly=True)
    description = fields.Text(string='Description')

    notebook_lines_invoice = fields.One2many('notebook.line.invoice', 'vendor_payment_id', string='Notebook Lines Invoice', readonly=True, states={'draft': [('readonly', False)]})
    notebook_lines_payments = fields.One2many('notebook.line.payments', 'vendor_payment_id', string='Notebook Lines Payments', readonly=True)

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('loaded', 'Loaded'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('downloaded', 'Downloaded'),
        ('uploaded', 'Uploaded'),
        ('cancelled', 'Cancelled'),
    ]
    state = fields.Selection(STATE_SELECTION, string='state', default='draft', readonly=True, required=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('vendor.payment') or 'New'
        return super(VendorPayment, self).create(vals)
    
    @api.onchange('payment_journal_id')
    def onchange_payment_journal(self):
        if self.payment_journal_id:
            self.currency_id = self.payment_journal_id.currency_id.id

    @api.depends('notebook_lines_invoice.invoice_amount')
    def _compute_total_invoice_amount(self):
        for payment in self:
            total_amount = 0.0
            for line in payment.notebook_lines_invoice:
                total_amount += line.invoice_amount
            payment.total_invoice_amount = total_amount

    def action_loade_invoice(self):
        self.ensure_one()
        self.state = 'loaded'

    def action_approve_invoice(self):
        # self.ensure_one()
        self.add_notebook_lines_payments()
        self.state = 'approved'
        
    def action_cancel(self):
        self.state = 'cancelled'

    def add_notebook_lines_payments(self):
        payment_lines = []
        for invoice_line in self.notebook_lines_invoice:
            
            if invoice_line.vendor_id and invoice_line.move_id:
                payment_line_vals = {
                    'vendor_id': invoice_line.vendor_id.id,
                    'vendor_vat': invoice_line.vendor_vat,
                    'vendor_bank': invoice_line.vendor_bank,
                    'total_invoice_amount': invoice_line.invoice_amount,
                    'move_id': invoice_line.move_id.id,
                }
                print(payment_line_vals)
                payment_lines.append((0, 0, payment_line_vals))

        self.notebook_lines_payments = payment_lines
        