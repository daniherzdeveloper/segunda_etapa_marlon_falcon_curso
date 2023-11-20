# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang, get_lang
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)


class Purchase3rdParty(models.Model):
    _name = 'purchase.3rd.party'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Purchase 3rd Party'
    _order = 'id desc'

    name = fields.Char("Code", required=True, default=_('New'), copy=False)
    partner_id = fields.Many2one('res.partner', string='Supplier', required=True)
    company_partner_id = fields.Many2one('res.partner', string='Company 3ro', required=True)
    date_order = fields.Date(string='Order Date', required=True, default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('to-pay', 'To Pay'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    state_stock = fields.Selection([
        ('no', 'No'),
        ('partial', 'Partial'),
        ('yes', 'Yes'),
    ], string='Received',
    compute='_compute_state_stock',
    readonly=True, copy=False, index=True, tracking=3, default='no')

    line_ids = fields.One2many('purchase.3rd.party.line',
               'purchase_3rd_party_id', string='Lines')


    line_stock_ids = fields.One2many('purchase.3rd.party.stock.line',
                'purchase_3rd_party_id', string='Lines Stock')



    amount_net = fields.Monetary(string='Total Neto', store=True, readonly=True, compute='_amount_all', tracking=4)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', tracking=4)
    tax_amount = fields.Monetary(string='Tax', store=True, readonly=True, compute='_amount_all', tracking=4)

    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id.id)
    user_id = fields.Many2one('res.users', string='User', index=True, tracking=3, default=lambda self: self.env.user)
    description = fields.Text(string='Description')

    report_footer = fields.Char(string='Report Footer', compute='_compute_report_footer', store=True)

    @api.depends('company_partner_id.email', 'company_partner_id.phone')
    def _compute_report_footer(self):
        for record in self:
            email = record.company_partner_id.email or ''
            phone = record.company_partner_id.phone or ''
            record.report_footer = f'{phone} | {email}'

    def _compute_state_stock(self):
        state = 'no'
        len_lines = len(self.line_ids)
        count = 0
        for line in self.line_ids:
            if line.product_qty > line.received_qty:
                state = 'partial'
                break

            if line.product_qty == line.received_qty:
                count += 1

        if count == len_lines:
            state = 'yes'

        self.state_stock = state


    @api.depends('line_ids.price_subtotal')
    def _amount_all(self):
        for order in self:
            amount_total = 0.0
            amount_net = 0.0
            tax_amount = 0.0

            for line in order.line_ids:
                line_amount_net = line.price_subtotal

                line_tax_amount = line_amount_net * line.tax_ids[0].amount / 100 if line.tax_ids else 0.0

                amount_net += line_amount_net
                tax_amount += line_tax_amount

                line_amount_total = line_amount_net + line_tax_amount
                amount_total += line_amount_total

            order.update({
                'amount_net': amount_net,
                'tax_amount': tax_amount,
                'amount_total': amount_total,
            })


    ref = fields.Char(string='Reference')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('purchase.3rd.party') or _('New')
        return super().create(vals)


    def exe_done(self):
        self.state = 'done'


    def exe_to_pay(self):
        self.state = 'to-pay'


    def exe_pay(self):
        self.state = 'paid'

    def exe_cancel(self):
        self.state = 'cancel'


    def exe_draft(self):
        self.state = 'draft'


    def exe_received_all(self):
        self.line_stock_ids.unlink()
        for line in self.line_ids:
            self.line_stock_ids.create({
                'name': line.name.id,
                'product_qty': line.product_qty,
                'user_id': self.env.user.id,
                'date': self.date_order,
                'purchase_3rd_party_id': self.id,
            })

class Purchase3rdPartyStockLine(models.Model):
    _name = 'purchase.3rd.party.stock.line'
    _description = 'Purchase 3rd Party Stock Line'

    name = fields.Many2one('product.product', string='Product', required=True)
    product_qty = fields.Float(string='Quantity Order', digits='Product Unit of Measure', required=True, default=1.0)
    user_id = fields.Many2one('res.users', string='User', index=True, tracking=3, default=lambda self: self.env.user)
    note = fields.Text(string='Note')
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)

    purchase_3rd_party_id = fields.Many2one(
        'purchase.3rd.party', 'Purchase 3rd Party', ondelete='cascade')


class Purchase3rdPartyLine(models.Model):
    _name = 'purchase.3rd.party.line'
    _description = 'Purchase 3rd Party Line'

    name = fields.Many2one('product.product', string='Product', required=True)
    product_qty = fields.Float(string='Quantity Order', digits='Product Unit of Measure', required=True, default=1.0)
    received_qty = fields.Float(string='Quantity Received',
                     compute='_compute_received_qty',
    digits='Product Unit of Measure', required=True, default=0.0)
    tax_ids = fields.Many2many('account.tax', string='Taxes', help="Taxes that apply on the base amount")
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_amount', store=True)
    purchase_3rd_party_id = fields.Many2one(
        'purchase.3rd.party', 'Purchase 3rd Party', ondelete='cascade')

    # received_qty
    @api.depends('purchase_3rd_party_id')
    def _compute_received_qty(self):
        for line in self:
            line.received_qty = 0.0
            for line_stock in line.purchase_3rd_party_id.line_stock_ids:
                if line.name.id == line_stock.name.id:
                    line.received_qty += line_stock.product_qty


    @api.onchange('name')
    def _onchange_uom(self):
        for line in self:
            line.product_uom = line.name.uom_id.id
            line.tax_ids = line.name.supplier_taxes_id.ids


    @api.depends('product_qty', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.price_subtotal = line.product_qty * line.price_unit