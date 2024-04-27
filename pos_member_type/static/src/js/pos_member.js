odoo.define('pos_member_type.pos_member', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');

    models.load_models([
        {
            model: 'pos.member.type',
            fields: ['name', 'loyalty_points'],
            domain: null,
            loaded: function (self, member_types) {
                self.member_types = member_types;
                self.member_type_by_id = {};
                member_types.forEach(function (member_type) {
                    self.member_type_by_id[member_type.id] = member_type;
                });
            },
        },
    ]);

    models.load_fields('res.partner', ['pos_member_type_id']);

    var _super_orderline_set_product = models.Orderline.prototype.set_product;
    models.Orderline = models.Orderline.extend({
        set_product: function (product, options) {
            _super_orderline_set_product.call(this, product, options);
            var client = this.pos.get_client();
            if (client && client.pos_member_type_id) {
                var member_type = this.pos.member_type_by_id[client.pos_member_type_id[0]];
                if (member_type) {
                    this.reward = this.pos.loyalty.get_reward_by_product(this.product);
                    this.loyalty_points = this.get_price() * member_type.loyalty_points;
                }
            }
        },
    });
});
