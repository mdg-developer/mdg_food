# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class FESC(models.Model):
    _name = "res.fesc"
    _description = "FESC"

    def _default_company(self):
        return self.env.company.id

    name = fields.Char(string='FESC No')
    date = fields.Date(string="Date", default=fields.Date.context_today)
    licence_no = fields.Char(string="License No")
    bank_id = fields.Many2one('account.journal', string="Bank", domain="[('type', 'in', ['bank','cash'])]")
    import_declaration_no = fields.Char(string="Import Declaration Number")
    partner_id = fields.Many2one('res.partner', string='Vendor', domain="[('supplier_rank', '>', 0)]")
    mt_qty = fields.Float(string='MT Qty')
    price = fields.Float(string='Price')
    subtotal = fields.Float(string='Subtotal')
    percent = fields.Float(string='Percent')
    balance = fields.Float(string='Balance')
    purchase_id = fields.Many2one('purchase.order', string='PO Number')
    company_id = fields.Many2one('res.company', string='Company', default=_default_company)

    @api.onchange('mt_qty','price')
    def onchange_mt_qty_price(self):
        if self.mt_qty and self.price:
            self.subtotal = self.mt_qty * self.price

    @api.model
    def create(self, vals):
        fesc_no = self.env['ir.sequence'].next_by_code('res.fesc')
        if fesc_no:
            vals['name'] = fesc_no
        res = super(FESC, self).create(vals)
        return res

