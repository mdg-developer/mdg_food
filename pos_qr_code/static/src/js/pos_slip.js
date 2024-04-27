odoo.define('pos_qr_code.default_code', function(require) {
    'use strict';

const {Orderline} = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');
var PosDB = require('point_of_sale.DB');
var config = require('web.config');
var core = require('web.core');
var field_utils = require('web.field_utils');
var time = require('web.time');
var utils = require('web.utils');
var { Gui } = require('point_of_sale.Gui');
const { batched, uuidv4 } = require("point_of_sale.utils");
const { escape } = require("@web/core/utils/strings");

var QWeb = core.qweb;
var _t = core._t;
var round_di = utils.round_decimals;
var round_pr = utils.round_precision;
const Markup = utils.Markup
const { markRaw, reactive } = owl;

const PosExt = (Orderline) => class PosExt extends Orderline {
                                                        export_for_printing(){
                                                                return {
                                                                    id: this.id,
                                                                    quantity:           this.get_quantity(),
                                                                    unit_name:          this.get_unit().name,
                                                                    is_in_unit:         this.get_unit().id == this.pos.uom_unit_id,
                                                                    price:              this.get_unit_display_price(),
                                                                    discount:           this.get_discount(),
                                                                    product_name:       this.get_product().display_name,
                                                                    product_name_wrapped: this.generate_wrapped_product_name(),
                                                                    price_lst:          this.get_lst_price(),
                                                                    fixed_lst_price:    this.get_fixed_lst_price(),
                                                                    price_manually_set: this.price_manually_set,
                                                                    display_discount_policy:    this.display_discount_policy(),
                                                                    price_display_one:  this.get_display_price_one(),
                                                                    price_display :     this.get_display_price(),
                                                                    price_with_tax :    this.get_price_with_tax(),
                                                                    price_without_tax:  this.get_price_without_tax(),
                                                                    price_with_tax_before_discount:  this.get_price_with_tax_before_discount(),
                                                                    tax:                this.get_tax(),
                                                                    product_description:      this.get_product().description,
                                                                    product_description_sale: this.get_product().description_sale,
                                                                    pack_lot_lines:      this.get_lot_lines(),
                                                                    customer_note:      this.get_customer_note(),
                                                                    default_code:       this.get_product().default_code
        }}}
    Registries.Model.extend(Orderline, PosExt);
   });


