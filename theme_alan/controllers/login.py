# -*- coding: utf-8 -*-

import logging

import odoo
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
from odoo.addons.auth_oauth.controllers.main import OAuthLogin
from odoo.addons.web.controllers.main import Home
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home, SIGN_UP_REQUEST_PARAMS
import re

_logger = logging.getLogger(__name__)

# Shared parameters for all login/signup flows

SIGN_UP_REQUEST_PARAMS_CUSTOM = {'db', 'login', 'debug', 'token', 'message', 'error', 'scope', 'mode',
                          'redirect', 'redirect_hostname', 'email', 'name', 'partner_id',
                          'password', 'confirm_password', 'gender', 'dob', 'city', 'country_id', 'lang'}

class AlanAuthSystem(Home):

    @http.route('/alan/login/',type='json', auth="public", website=True)
    def alan_login(self,**kwargs):
        ''' Login Template Getters '''
        context = {}
        providers = OAuthLogin.list_providers(self)
        context.update(super().get_auth_signup_config())
        context.update({'providers':providers})
        signup_enabled = request.env['res.users']._get_signup_invitation_scope() == 'b2c'
        reset_password_enabled = request.env['ir.config_parameter'].sudo().get_param('auth_signup.reset_password') == 'True'
        website_logo = request.website.image_url(request.website,'logo')
        context.update({'signup_enabled':signup_enabled ,"reset_password_enabled":reset_password_enabled,'website_logo':website_logo})
        login_template = request.env['ir.ui.view']._render_template("theme_alan.as_login",context)
        return {'template':login_template}

    @http.route('/alan/login/authenticate', type='json', auth="none")
    def alan_login_authenticate(self, **kwargs):
        ''' Login Authentication '''
        request.params['login_success'] = False
        if not request.uid:
            request.uid = odoo.SUPERUSER_ID
        values = request.params.copy()
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                return request.params
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("We have sent new login password to your Email. Please check and try again!")
                else:
                    values['error'] = e.args[0]
        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')
        return values

    @http.route('/alan/signup/authenticate',type="json",auth="public")
    def alan_signup_authenticate(self,*args, **kw):
        ''' Signup Authentication '''
        qcontext = self.get_auth_signup_qcontext()
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                super(AlanAuthSystem,self).do_signup(qcontext)
                return {'signup_success':True}
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))]):
                    qcontext['error'] = _('Another user is already registered using this email address.')
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _('Could not create a new account.')
        return qcontext

    def get_auth_signup_qcontext(self):
        """ Shared helper returning the rendering context for signup and reset password """
        qcontext = {k: v for (k, v) in request.params.items() if k in SIGN_UP_REQUEST_PARAMS_CUSTOM}
        qcontext.update(self.get_auth_signup_config())
        if not qcontext.get('token') and request.session.get('auth_signup_token'):
            qcontext['token'] = request.session.get('auth_signup_token')
        if qcontext.get('token'):
            try:
                # retrieve the user info (name, login or email) corresponding to a signup token
                token_infos = request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                qcontext['invalid_token'] = True
        return qcontext

    def _prepare_signup_values(self, qcontext):
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password', 'gender', 'dob') }
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('login'):
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]gmail+[.]\w{3,3}$'
            if not (re.fullmatch(regex, values.get('login'))):
                raise UserError(_("Invalid Email; please retype them."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '')
        if lang in supported_lang_codes:
            values['lang'] = lang
        return values

