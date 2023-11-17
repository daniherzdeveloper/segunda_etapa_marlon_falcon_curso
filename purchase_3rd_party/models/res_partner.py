# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_3rd_party = fields.Boolean('Is 3rd Party', default=False)