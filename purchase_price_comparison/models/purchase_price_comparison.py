from odoo import models, fields, api, _

class PurchasePriceComparison(models.Model):
    _name = 'purchase.price.comparison'
    _description = 'Purchase Price Comparison'

    name = fields.Char(string='Name', required=True, default='New', readonly=True)
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('evaluate', 'Evaluate'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='State', default='draft', required=True)

    price_line_ids = fields.One2many('purchase.price.line', 'comparison_id', string='Price Lines')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])
            if vals.get('name', _("New")) == _("New"):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'purchase.price.comparison') or _("New")

        return super(PurchasePriceComparison, self).create(vals_list)

    def action_evaluate(self):
        self.write({'state': 'evaluate'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})
