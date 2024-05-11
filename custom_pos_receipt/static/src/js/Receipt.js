odoo.define('custom_pos_receipt.receipt', function(require){
    'use strict';
    var models = require('point_of_sale.models');
    var _super_partner = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes){
            var self = this;
            models.load_fields('res.partner', ['barcode']);
            _super_partner.initialize.apply(this, arguments);
        },
        getValidationDate: function () {
            var order = this.get_order();
            if (order) {
                return this._format_validation_date(order.validation_date);
            }
            return '';
        },
        _format_validation_date: function (date) {
            if (!date) return '';
            return moment(date).format('D-MMM-Y, hh:mm A'); // Adjust the format as needed
        },
    });
});
