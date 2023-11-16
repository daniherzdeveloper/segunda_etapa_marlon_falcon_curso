from odoo import models, fields, api

class PurchasePriceLine(models.Model):
    _name = 'purchase.price.line'
    _description = 'Purchase Price Line'

    name = fields.Many2one('purchase.order', string='Purchase Order', required=True)
    # price = fields.Float(string='Price', required=True)
    # quantity = fields.Float(string='Quantity', required=True)
    # subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    comparison_id = fields.Many2one('purchase.price.comparison', string='Price Comparison')

    @api.depends('price', 'quantity')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.price * line.quantity
