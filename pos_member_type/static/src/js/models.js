/* global waitForWebfonts */
odoo.define('pos_member_type.models', function (require) {
"use strict";

const { PosGlobalState, PosDB } = require('point_of_sale.models');
    const Registries = require("point_of_sale.Registries");
    var utils = require('web.utils');
    var { Gui } = require('point_of_sale.Gui');
    var round_di = utils.round_decimals;
const PosGlobalStateExt = (PosGlobalState) => class PosGlobalStateExt extends PosGlobalState {
    async load_server_data(){
        const loadedData = await this.env.services.rpc({
            model: 'pos.session',
            method: 'load_pos_data',
            args: [[odoo.pos_session_id]],
        });
        await this._processData(loadedData);
        await this._get_pos_member_type_data(loadedData);
        return this.after_load_server_data();
    }
    async _get_pos_member_type_data(loadedData){
        this.pos_member_type = loadedData['pos.member.type'];
    }
//    async _processData(loadedData) {
//        this.version = loadedData['version'];
//        this.company = loadedData['res.company'];
//        this.dp = loadedData['decimal.precision'];
//        this.units = loadedData['uom.uom'];
//        this.units_by_id = loadedData['units_by_id'];
//        this.states = loadedData['res.country.state'];
//        this.countries = loadedData['res.country'];
//        this.langs = loadedData['res.lang'];
//        this.taxes = loadedData['account.tax'];
//        this.taxes_by_id = loadedData['taxes_by_id'];
//        this.pos_session = loadedData['pos.session'];
//        this._loadPosSession();
//        this.config = loadedData['pos.config'];
//        this._loadPoSConfig();
//        this.bills = loadedData['pos.bill'];
//        this.partners = loadedData['res.partner'];
//        this.addPartners(this.partners);
//        this.picking_type = loadedData['stock.picking.type'];
//        this.user = loadedData['res.users'];
//        this.pricelists = loadedData['product.pricelist'];
//        this.default_pricelist = loadedData['default_pricelist'];
//        this.currency = loadedData['res.currency'];
//        this.db.add_categories(loadedData['pos.category']);
//        this._loadProductProduct(loadedData['product.product']);
//        this.db.add_packagings(loadedData['product.packaging']);
//        this.attributes_by_ptal_id = loadedData['attributes_by_ptal_id'];
//        this.cash_rounding = loadedData['account.cash.rounding'];
//        this.payment_methods = loadedData['pos.payment.method'];
//        this._loadPosPaymentMethod();
//        this.fiscal_positions = loadedData['account.fiscal.position'];
//        this.base_url = loadedData['base_url'];
//        await this._loadFonts();
//        await this._loadPictures();
//    }
}

Registries.Model.extend(PosGlobalState, PosGlobalStateExt);
});
