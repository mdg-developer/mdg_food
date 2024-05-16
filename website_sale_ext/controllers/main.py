from odoo import http, _
from odoo.addons.website_sale.controllers import main
from odoo.exceptions import UserError
from odoo.http import request
from werkzeug.exceptions import Forbidden
import logging


from werkzeug.urls import url_encode, url_parse
_logger = logging.getLogger(__name__)


class WebsiteSale(main.WebsiteSale):

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if order.partner_id.commercial_partner_id.id == partner_id:
                        mode = ('new', 'shipping')
                        partner_id = -1
                    elif partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode and partner_id != -1:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else:  # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw and request.httprequest.method == "POST":
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                # We need to validate _checkout_form_save return, because when partner_id not in shippings
                # it returns Forbidden() instead the partner_id
                if isinstance(partner_id, Forbidden):
                    return partner_id
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.with_context(not_self_saleperson=True).onchange_partner_id()
                    # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                                         (not order.only_services and (
                                                 mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                    # We need to update the pricelist(by the one selected by the customer), because onchange_partner reset it
                    # We only need to update the pricelist when it is not redirected to /confirm_order
                    if kw.get('callback', '') != '/shop/confirm_order':
                        request.website.sale_get_order(update_pricelist=True)
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                # TDE FIXME: don't ever do this
                # -> TDE: you are the guy that did what we should never do in commit e6f038a
                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')

        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
        }
        render_values.update(self._get_country_related_render_values(kw, render_values))

        render_values.update(self._get_city_related_render_values(kw, render_values))

        render_values.update(self._get_township_related_render_values(kw, render_values))

        return request.render("website_sale.address", render_values)

    def _get_township_related_render_values(self, kw, render_values):
        '''
        This method provides fields related to the country to render the website sale form
        '''
        values = render_values['checkout']
        mode = render_values['mode']
        order = render_values['website_sale_order']

        def_township_id = order.partner_id.township_id
        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_township_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_township_id = request.website.user_id.sudo().country_id

        township = 'township_id' in values and values['township_id'] != '' and request.env['res.township'].browse(int(values['township_id']))
        township = township and township.exists() or def_township_id

        city = 'city_id' in values and values['city_id'] != '' and request.env['res.city'].browse(
            int(values['city_id']))
        city = city and city.exists()

        res = {
            'township': township,
            'townshipes': township.get_website_sale_township(city),
        }
        return res

    def _get_city_related_render_values(self, kw, render_values):
        '''
        This method provides fields related to the country to render the website sale form
        '''
        values = render_values['checkout']
        mode = render_values['mode']
        order = render_values['website_sale_order']

        def_city_id = order.partner_id.city_id
        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_city_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_city_id = request.website.user_id.sudo().city_id

        city = 'city_id' in values and values['city_id'] != '' and request.env['res.city'].browse(int(values['city_id']))
        city = city and city.exists() or def_city_id

        res = {
            'city': city,
            'cities': city.get_website_sale_city(mode=mode[1]),
        }
        return res

    def _get_mandatory_fields_billing(self, country_id=False):
        req = ["name", "email", "street", "country_id"]
        if country_id:
            country = request.env['res.country'].browse(country_id)
            if country.state_required:
                req += ['state_id']
            if country.zip_required:
                req += ['zip']
        return req

    @http.route(['/shop/city_info/<model("res.city"):city>'], type='json', auth="public", methods=['POST'], website=True)
    def city_info(self, city, mode, **kw):
        return dict(
            states=[(st.id, st.name, st.code) for st in city.get_website_sale_township(mode=mode)],
            city=city.name,
        )

    @http.route(['/shop/state_info/<model("res.country.state"):state>'], type='json', auth="public", methods=['POST'], website=True)
    def state_info(self, state, mode, **kw):
        township_ids = ''
        states_ids = [(st.id, st.name, st.code) for st in state.get_website_sale_city(mode=mode)]
        if states_ids:
            township_ids = [(st.id, st.name, st.code) for st in state.get_website_sale_city(mode=mode)[0].get_website_sale_township(mode=mode)]
        return dict(
            cities=states_ids,
            state=state.name,
            township=township_ids,
        )

    @http.route(['/shop/country_infos/<model("res.country"):country>'], type='json', auth="public", methods=['POST'],
                website=True)
    def country_infos(self, country, mode, **kw):
        return dict(
            fields=country.get_address_fields(),
            states=[(st.id, st.name, st.code) for st in country.get_website_sale_states(mode=mode) if st.code != '04'],
            phone_code=country.phone_code,
            zip_required=country.zip_required,
            state_required=country.state_required,
        )

    def values_postprocess(self, order, mode, values, errors, error_msg):
        new_values = {}
        authorized_fields = request.env['ir.model']._get('res.partner')._get_form_writable_fields()
        for k, v in values.items():
            # don't drop empty value, it could be a field to reset
            if k in authorized_fields and v is not None:
                new_values[k] = v
            else:  # DEBUG ONLY
                if k not in ('field_required', 'partner_id', 'callback', 'submitted'): # classic case
                    _logger.debug("website_sale postprocess: %s value has been dropped (empty or not writable)" % k)
                if k in ('city_id', 'township_id'):
                    new_values[k] = v

        if request.website.specific_user_account:
            new_values['website_id'] = request.website.id

        if mode[0] == 'new':
            new_values['company_id'] = request.website.company_id.id
            new_values['team_id'] = request.website.salesteam_id and request.website.salesteam_id.id
            new_values['user_id'] = request.website.salesperson_id.id

        lang = request.lang.code if request.lang.code in request.website.mapped('language_ids.code') else None
        if lang:
            new_values['lang'] = lang
        if mode == ('edit', 'billing') and order.partner_id.type == 'contact':
            new_values['type'] = 'other'
        if mode[1] == 'shipping':
            new_values['parent_id'] = order.partner_id.commercial_partner_id.id
            new_values['type'] = 'delivery'

        return new_values, errors, error_msg

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment_confirmation(self, **post):
        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)

            order_seq_name = request.env['ir.sequence'].next_by_code('sale.order')
            order.write({
                'state': 'sale',
                'name': order_seq_name,
                'reference': order_seq_name,
            })
            order.action_confirm()

            return request.render("website_sale.confirmation", {
                'order': order,
                'order_tracking_info': self.order_2_return_dict(order),
            })
        else:
            return request.redirect('/shop')
