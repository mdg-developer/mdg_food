# -*- coding: utf-8 -*-
{
  "name"                 :  "POS Session Report",
  "summary"              :  "Custom: This module prints POS Session Summary as well as send Session Summary to the current login user.",
  "category"             :  "Point Of Sale",
  "version"              :  "1.1",
  "author"               :  "Webkul and Nisu Company Limited.",
  "website"              :  "https://nisu.consulting",
  "description"          :  """POS Session Report , POS Session Report Analysis, Session Report in Running Session, Session report as receipt
                              POS Sales Report, User Wise Session Summary, Session Summary in Running Session, Print Session Summary, POS Summary,
                           
                            """,
  "depends"              :  [
                             'point_of_sale',
                             'mail',
                            ],
  "data"                 :  [
                             'views/pos_config.xml',
                             'views/pos_session_report_view.xml',
                             'views/report_session_summary.xml',
                            ],
 "assets": {
        'point_of_sale.assets': [
            '/wk_pos_session_report_analysis/static/src/js/main.js',
            '/wk_pos_session_report_analysis/static/src/js/jquery.datetimepicker.full.js',
            '/wk_pos_session_report_analysis/static/src/css/jquery.datetimepicker.css'
        ],
        'web.assets_qweb': [
            '/wk_pos_session_report_analysis/static/src/xml/pos_session_report.xml',
        ]
  },
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "pre_init_hook"        :  "pre_init_check",
}
