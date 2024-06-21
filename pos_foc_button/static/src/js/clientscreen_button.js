odoo.define('CustomerFacingDisplayOrder', function (require) {
    var CustomerFacingDisplayWidget = require('CustomerFacingDisplayOrder.CustomerFacingDisplayWidget');

    CustomerFacingDisplayWidget.include({
        update_customer_display: function() {
            var currentOrder = this.pos.get_order();
            if (currentOrder && currentOrder.get_client()) {
                this.$('.customer-info').html(QWeb.render('CustomCustomerInfo', {
                    widget: this,
                    order: currentOrder,
                }));
            } else {
                this.$('.customer-info').html('');
            }
        },
    });

    return CustomerFacingDisplayWidget;
});
