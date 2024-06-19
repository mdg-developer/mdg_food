odoo.define('pos_foc_button.pos_foc_button', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    class FocButton extends PosComponent {
        async onClick() {
            const order = this.env.pos.get_order();
            const selectedOrderline = order.get_selected_orderline();
            if (selectedOrderline) {
                selectedOrderline.set_unit_price(0);
            } else {
                this.showPopup('ErrorPopup', {
                    title: this.env._t('No Product Selected'),
                    body: this.env._t('Please select a product before applying FOC.'),
                });
            }
        }
    }
    FocButton.template = 'FocButton';

    ProductScreen.addControlButton({
        component: FocButton,
        condition: function () {
            return true;
        },
    });

    Registries.Component.add(FocButton);

    return FocButton;
});

