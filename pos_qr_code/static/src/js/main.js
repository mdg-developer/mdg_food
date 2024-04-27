odoo.define('pos_qr_code.date_format', function(require) {
'use strict';

const {Order} = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');


const PosDateFormatExt = (Order) => class PosDateFormatExt extends Order {
                                                             initialize_validation_date() {
                                                                      this.validation_date = new Date();
                                                                      this.formatted_validation_date = moment(this.validation_date).format('DD MMMM YYYY , hh:mm A');
                                                                        }}
Registries.Model.extend(Order, PosDateFormatExt);
});