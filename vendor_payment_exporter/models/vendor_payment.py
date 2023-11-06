from odoo import models, fields, api

class VendorPayment(models.Model):
    _name = 'vendor.payment'
    _description = 'Vendor Payments'

    name = fields.Char('name', default='New', readonly=1)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    amount = fields.Float(string='Amount', required=True)
    payment_journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True)
    created_by_user_id = fields.Many2one('res.users', string='Created by', default=lambda self: self.env.user, readonly=True)
    description = fields.Text(string='Description')

    notebook_lines = fields.One2many('notebook.line', 'vendor_payment_id', string='Notebook Lines')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('vendor.payment') or 'New'
        return super(VendorPayment, self).create(vals)
    
    @api.onchange('payment_journal_id')
    def onchange_payment_journal(self):
        if self.payment_journal_id:
            self.currency_id = self.payment_journal_id.currency_id.id