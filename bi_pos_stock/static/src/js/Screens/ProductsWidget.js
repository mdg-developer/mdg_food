// BiProductScreen js
odoo.define('bi_pos_stock.ProductsWidget', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ProductsWidget = require('point_of_sale.ProductsWidget');
	var models = require('point_of_sale.models');
	var utils = require('web.utils');
	var round_pr = utils.round_precision;

	let prd_list_count = 0;

	const BiProductsWidget = (ProductsWidget) =>
		class extends ProductsWidget {
			constructor() {
				super(...arguments);
			}

			mounted() {
				super.mounted();
				this.env.pos.on('change:is_sync', this.render, this);
				let self = this;
				self.env.services.bus_service.updateOption('pos.sync.stock',self.env.session.uid);
				self.env.services.bus_service.onNotification(self,self._onProductNotification);
				self.env.services.bus_service.startPolling();
				self.env.services.bus_service._startElection();
			}

			_onProductNotification(notifications){
				let self = this;
				_.each(notifications,function(not){
					let prod_data = JSON.parse(not.type.prod_data);
					let prod_id = JSON.parse(not.type.id);
					let product = self.env.pos.db.get_product_by_id(prod_id);
					product.pos = self.env.pos;
					if(self.env.pos.db.product_by_id[product.id]){
						$.each(prod_data, function( key, val ){
							if(key == 'qty_available'){
								product['qty_available'] = val;
								product['bi_on_hand'] = val;
							}
							else if(key == 'virtual_available'){
								product['virtual_available'] = val;
							}
							else if(key == 'incoming_qty'){
								product['incoming_qty'] = val;
							}
							else if(key == 'outgoing_qty'){
								product['outgoing_qty'] = val;
							}
							else if (key == 'quant_text') {
								let data = JSON.parse(val)
								$.each(data, function( i, j ){
									product['quant_text'] = val;
								})
							}
						})
						self.env.pos.db.product_by_id[product.id] = new models.Product({}, product);
					}
					self.env.pos.set("is_sync",false);
					
				})
				let call = self.productsToDisplay;
				this.env.pos.set("is_sync",true);
			}

			willUnmount() {
				super.willUnmount();
				this.env.pos.off('change:is_sync', null, this);
			}

			_switchCategory(event) {
				this.env.pos.set("is_sync",true);
				super._switchCategory(event);
			}

			get is_sync() {
				return this.env.pos.get('is_sync');
			}

			get productsToDisplay() {
				let self = this;
				let prods = super.productsToDisplay;
				let location = self.env.pos.locations;
				if (self.env.pos.config.show_stock_location == 'specific'){
					if (self.env.pos.config.pos_stock_type == 'onhand'){
						$.each(prods, function( i, prd ){
							prd['bi_on_hand'] = 0;
							let loc_onhand = JSON.parse(prd.quant_text);
							$.each(loc_onhand, function( k, v ){
								if(location.id == k){
									prd['bi_on_hand'] = v[0];
								}
							})
						});
						self.env.pos.set("is_sync",false);
					}
					if (self.env.pos.config.pos_stock_type == 'available'){
						$.each(prods, function( i, prd ){
							let loc_available = JSON.parse(prd.quant_text);
							prd['bi_available'] = 0;
							let total = 0;
							let out = 0;
							let inc = 0;
							$.each(loc_available, function( k, v ){
								if(location.id == k){
									total += v[0];
									if(v[1]){
										out += v[1];
									}
									if(v[2]){
										inc += v[2];
									}
									let final_data = (total + inc)
									prd['bi_available'] = final_data;
									prd['virtual_available'] = final_data;
								}
							})
						});
						self.env.pos.set("is_sync",false);
					}
				}
				else{
					$.each(prods, function( i, prd ){
						prd['bi_on_hand'] = (prd.qty_available - prd.outgoing_qty);
						prd['bi_available'] = (prd.virtual_available);
					});
				}
				return prods
			}
		};

	Registries.Component.extend(ProductsWidget, BiProductsWidget);

	return ProductsWidget;

});
