odoo.define('techno_pos_session_report.session_report', function(require){
    "use strict";

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen')
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class SessionReportButton extends PosComponent {
            constructor() {
                super(...arguments);
                useListener('click', this.onClick);
            }
 
            async onClick(){
                var self = this;
                var pos_session_id = self.env.pos.pos_session.id;
                var action = {
                    'type': 'ir.actions.report',
                    'report_type': 'qweb-pdf',
                    'report_file': 'techno_pos_session_report.report_pos_session_pdf/'+pos_session_id.toString(),
                    'report_name': 'techno_pos_session_report.report_pos_session_pdf/'+pos_session_id.toString(),
                    'data': self.data,
                    'context': {'active_id': [pos_session_id]},
                };
                return this.env.pos.do_action(action);
                
            }
       };

        SessionReportButton.template = 'SessionReportPrintButton'
        ProductScreen.addControlButton({
            component: SessionReportButton,
            condition: function() {
                return this.env.pos.config.iface_session_report;
            },
        });

        Registries.Component.add(SessionReportButton);

        return SessionReportButton;
    
});
