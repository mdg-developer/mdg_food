odoo.define('pos_member_type.pos_member', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

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

    models.load_fields('res.partner', ['pos_member_type_id','birthday']);

});
