# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.urls import url_decode, url_encode, url_parse

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.fields import Command
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.website.controllers import main
from odoo.addons.website.controllers.form import WebsiteForm
from odoo.osv import expression
from odoo.tools.json import scriptsafe as json_scriptsafe
_logger = logging.getLogger(__name__)


# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class ResTownship(models.Model):
    _inherit = 'res.township'

    def get_website_sale_township(self, city):
        if city:
            return self.sudo().search([('city_id', '=', city.id)])
        else:
            return self.sudo().search([])


class ResTownship(models.Model):
    _inherit = 'res.city'

    def get_website_sale_city(self, mode='billing'):
        return self.sudo().search([])

    def get_website_sale_township(self, mode='billing'):
        return self.env['res.township'].sudo().search([('city_id', '=', self.id)])


class CountryState(models.Model):
    _inherit = 'res.country.state'

    def get_website_sale_state(self, mode='billing'):
        return self.sudo().search([])

    def get_website_sale_city(self, mode='billing'):
        return self.env['res.city'].sudo().search([('state_id', '=', self.id)])


class Partner(models.Model):
    _inherit = 'res.partner'

    township_id = fields.Many2one('res.township', string='Townshop')
    city_id = fields.Many2one('res.city', string='City')
