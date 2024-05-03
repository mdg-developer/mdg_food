odoo.define('custom_pos_receipt.receipt', function(require){
    'use strict';
    var models = require('point_of_sale.models');
    var _super_partner = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes){
            var self = this;
            models.load_fields('res.partner', ['barcode']);
            _super_partner.initialize.apply(this, arguments);
        }
    });
});
