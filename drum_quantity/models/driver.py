# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class Driver(models.Model):
    _name = "res.driver"
    _description = "Driver"

    def _default_company_name(self):
        return self.env.company.name        

    company_name = fields.Char(string='Company Name', default=_default_company_name)
    name = fields.Char(string="Name")
    nrc_no = fields.Char(string="NRC No")
    phone_one = fields.Char(string="Phone 1")
    phone_two = fields.Char(string="Phone 2")


