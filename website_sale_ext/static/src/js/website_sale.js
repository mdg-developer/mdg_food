odoo.define('website_sale_ext.checkout', function(require) {
    'use strict';

    var core = require('web.core');
    var config = require('web.config');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.CheckoutPage = publicWidget.Widget.extend({
        selector: '.oe_website_sale',
        events: {
            'change select[name="city_id"]': '_onChangeCity',
            'change select[name="state_id"]': '_onChangeState',
        },

        _onChangeCity: function(env) {
            if (!this.$('.checkout_autoformat').length) {
                return;
            }
            this._changeCity();
        },
        _changeCity: function () {
            if (!$("#city_id").val()) {
                return;
            }
            this._rpc({
                route: "/shop/city_info/" + $("#city_id").val(),
                params: {
                    mode: $("#city_id").attr('mode'),
                },
            }).then(function (data) {
                $("input[name='city']").val(data.city);
                var selectTownship = $("select[name='township_id']");
                // dont reload state at first loading (done in qweb)
                selectTownship.html('');
                _.each(data.states, function (x) {
                    var opt = $('<option>').text(x[1])
                        .attr('value', x[0])
                        .attr('data-code', x[2]);
                    selectTownship.append(opt);
                });
                selectTownship.parent('div').show();

            });
        },

        _onChangeState: function () {
            if (!$("#state_id").val()) {
                return;
            }
            this._rpc({
                route: "/shop/state_info/" + $("#state_id").val(),
                params: {
                    mode: $("#state_id").attr('mode'),
                },
            }).then(function (data) {
                $("input[name='state_id']").val(data.state);
                var selectCity = $("select[name='city_id']");
                // dont reload state at first loading (done in qweb)
                selectCity.html('');
                _.each(data.cities, function (x) {
                    var opt = $('<option>').text(x[1])
                        .attr('value', x[0])
                        .attr('data-code', x[2]);
                    selectCity.append(opt);
                });
                $("input[name='city']").val(data.cities[0]);
                var selectTownship = $("select[name='township_id']");
                // dont reload state at first loading (done in qweb)
                selectTownship.html('');
                _.each(data.township, function (x) {
                    var opt = $('<option>').text(x[1])
                        .attr('value', x[0])
                        .attr('data-code', x[2]);
                    selectTownship.append(opt);
                });
                selectTownship.parent('div').show();
                selectCity.parent('div').show();
            });
        },
    });
});

