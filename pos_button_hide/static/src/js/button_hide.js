odoo.define('pos_button_hide.ProductInfoButtonExt', function(require) {
    'use strict';

    const ProductInfoButton = require('point_of_sale.ProductInfoButton');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    ProductScreen.addControlButton({
        component: ProductInfoButton,
        condition: function() {
            var res;
            if(this.env.pos.config.hide_info_button)
                res = false;
            else
                res = true;
            return res;
        },
        position: ['replace', 'ProductInfoButton'],
    });

});
