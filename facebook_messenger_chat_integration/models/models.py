# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RecCompany(models.Model):
    _inherit = "res.company"

    fb_page_id = fields.Char("Facebook Business Page ID")
    fb_theme_color = fields.Char("Chat Widget Color")
    fb_logged_in_greeting = fields.Char("Logged In Greeting Message")
    fb_logged_out_greeting = fields.Char("Logged Out Greeting Message")
