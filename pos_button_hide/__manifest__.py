{
  "name"                 :  "POS Hide Info Button",
  "summary"              :  """POS Hide Info Button""",
  "category"             :  "Point of Sale",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "7th computing developer",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/odoo-pos-manage-packages-with-pricelist.html",
  "description"          :  """POS Hide Info Button""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_manage_packages&custom_url=/pos/web/#action=pos.ui",
  "depends"              :  ['point_of_sale'],
  "data"                 :  ['views/res_config_view.xml',],
  "assets"               :  {
                              'point_of_sale.assets': [
                                "/pos_button_hide/static/src/js/button_hide.js",
                              ],
                              'web.assets_qweb': [
                                'pos_button_hide/static/src/xml/button_hide.xml',
                              ],
                            },

  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  79,
  "currency"             :  "USD",
}
