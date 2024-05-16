odoo.define('theme_alan.category_slider', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var fewSeconds = 8;

    $(document).on("click",".multi-cat", function() {
    	var cr = $(this).closest('.as_cat_product_slider ');
    	var custom = $(this).attr('cat-multi-id');
        ajax.jsonRpc('/get/get_cat_brand_slider_content', 'call', {
            'cat_ids': cr.attr('data-cat-ids'),
            'snippet_type': cr.attr('data-snippet-type'),
            'mainUI': cr.attr('data-mainUI'),
            'tabOption': cr.attr('data-tabOption'),
            'styleUI': cr.attr('data-styleUI'),
            'dataCount': cr.attr('data-dataCount'),
            'recordLink': cr.attr('data-recordLink'),
            'autoSlider': cr.attr('data-autoSlider'),
            'sTimer': cr.attr('data-sTimer'),
            'cart': cr.attr('data-cart'),
            'quickView': cr.attr('data-quickView'),
            'compare': cr.attr('data-compare'),
            'wishList': cr.attr('data-wishList'),
            'prodLabel': cr.attr('data-prodLabel'),
            'rating': cr.attr('data-rating'),
            'infinity': cr.attr('data-infinity'),
            'sliderType': cr.attr('data-slider'),
            'filter_data': custom,
        }).then(function(data) {
            cr.removeClass("as-dynamic-loading").empty().append(data.slider);
            var count = data.dataCount;
            var ui = data.mainUI;
            var stimer = data.sTimer;
            var sliderData = { spaceBetween: 15, slidesPerView: 2,
                navigation: {
                  nextEl: ".swiper-button-next",
                  prevEl: ".swiper-button-prev",
                },
                breakpoints: {
                    640: {
                      slidesPerView: 2,
                    },
                    768: {
                      slidesPerView: 3,
                    },
                    1024: {
                      slidesPerView: 4,
                    },
                    1200: {
                      slidesPerView: data.dataCount,
                    },
                },
            }
            switch (data.sliderType) {
                case 1:
                    sliderData['pagination'] = {}
                    break;
                case 2:
                    sliderData['pagination'] = {el: ".swiper-pagination", clickable: true}
                    break;
                case 3:
                    sliderData['pagination'] = {el: ".swiper-pagination", dynamicBullets: true}
                    break;
                case 4:
                    sliderData['pagination'] = {el: ".swiper-pagination", type: "progressbar"}
                    break;
                case 5:
                    sliderData['pagination'] = {el: ".swiper-pagination", type: "fraction"}
                    break;
                case 6:
                    sliderData['pagination'] = {el: ".swiper-pagination", clickable: true,
                                                renderBullet: function (index, className) {
                                                    return '<span class="' + className + '">' + (index + 1) + "</span>";
                                                }}
                    break;
                case 7:
                    sliderData['scrollbar'] = {el: ".swiper-scrollbar", hide: true}
                    break;
            }
            if (data.autoSlider) {
                sliderData.autoplay = {
                  delay: stimer,
                  disableOnInteraction: false,
                }
            }
            if (data.infinity) {
                sliderData['loop'] = true
            }
        });
    });

});