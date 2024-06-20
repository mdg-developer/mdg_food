{
  "name"                 :  "POS FOC Button",
  "summary"              :  """POS FOC Button""",
  "category"             :  "Point of Sale",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "MDG developer",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/odoo-pos-manage-packages-with-pricelist.html",
  "description"          :  """POS FOC Button""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_manage_packages&custom_url=/pos/web/#action=pos.ui",
  "depends"              :  ['point_of_sale'],
  "assets"               :  {
                              'point_of_sale.assets': [
                                "/pos_foc_button/static/src/js/pos_foc_button.js",
                                "/pos_foc_button/static/src/js/clientscreen_button.js",
                              ],
                              'web.assets_qweb': [
                                "/pos_foc_button/static/src/xml/focButton.xml",
                                "/pos_foc_button/static/src/xml/clientscreenButton.xml",
                              ],
                            },
  'qweb': [],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
}
