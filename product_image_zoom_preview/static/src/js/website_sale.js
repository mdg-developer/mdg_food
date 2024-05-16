odoo.define('product_image_zoom_preview.website_sale', function(require) {
    "use strict";

    require('website_sale.website_sale');
    var utils = require('web.utils');
    var core = require('web.core');
    var config = require('web.config');

    var _t = core._t;

    $(document).on('mouseover', '.carousel-item.h-100.active .knk_zoom_img', function() {
        $(this).elevateZoom({scrollZoom : true, borderSize : 1, zoomWindowPosition: 1, zoomWindowOffetx: 3,});
    });
    
});