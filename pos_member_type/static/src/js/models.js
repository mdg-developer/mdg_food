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

}
Registries.Component.add(PosGlobalStateExt)
});
