odoo.define('wk_pos_session_report_analysis.pos_session_report_analysis',function(require){
    "use strict"
    var chrome = require('point_of_sale.chrome');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var _t = core._t;
	var popup_widget = require('point_of_sale.popups');


    var SessionTicketScreenWidget = screens.ScreenWidget.extend({
        template: 'SessionTicketScreenWidget',
        show: function() {
            var self = this;
            self._super();
            $('.button.back.wk_reprint_back').on("click", function() {
                self.gui.show_screen('products');
            });
            $('.button.print').click(function() {
                var test = self.chrome.screens.receipt;
                setTimeout(function() {
                    self.chrome.screens.receipt.lock_screen(false);
                }, 1000);
                if (!test['_locked']) {
                    self.chrome.screens.receipt.print_web();
                    self.chrome.screens.receipt.lock_screen(true);
                }
            });
        }
    });
    gui.define_screen({ name: 'print_session_ticket', widget: SessionTicketScreenWidget });

    var SessionReportPopup = popup_widget.extend({
		template: 'SessionReportPopup',
        show: function(){
			var self=this;
			this._super();
            $( "#session_from_date" ).datetimepicker({
                showButtonPanel: true,
                dateFormat: "yy-mm-dd",
                changeMonth: true,
                changeYear: true,
                yearRange: "c-100:c+10",
                dayNamesMin : [ "S", "M", "T", "W", "T", "F", "S" ],
                buttonImageOnly: true,
                buttonImage: "/wk_pos_session_report_analysis/static/description/date.png",
                buttonText: "Pick Date",
                showOn: "button",
            });  
            $( "#session_to_date" ).datetimepicker({
                showButtonPanel: true,
                dateFormat: "yy-mm-dd",
                changeMonth: true,
                changeYear: true,
                yearRange: "c-100:c+10",
                dayNamesMin : [ "S", "M", "T", "W", "T", "F", "S" ],
                buttonImageOnly: true,
                buttonImage: "/wk_pos_session_report_analysis/static/description/date.png",
                buttonText: "Pick Date",
                showOn: "button",
            });  
            $( "#datepicker-div" ).datetimepicker({
                dateFormat: "dd/mm/yy",
                yearRange: "c-100:c+10",
                dayNamesMin : [ "S", "M", "T", "W", "T", "F", "S" ],
            });

            $("#running_session_summary").change(function() {
                var checked = $('#running_session_summary').is(":checked");
                if (checked) {
                   $("#datepicker-container").hide();
                }
                else{
                   $("#datepicker-container").show();
                   
                }
             });

            $('.print_summary').on('click', function(){
                self.print_session_summary();
            })
        },
        print_session_summary: function(){
            var self = this;
            if($('#running_session_summary').is(":checked")){
                if(self.pos.config.wk_report_print_type != 'pdf'){                    
                    if(self.pos.config.wk_report_print_type != 'posbox'){
                       rpc.query({
                            model:'pos.session',
                            method:'get_session_report_data',
                            args: [{ 'session_id': self.pos.pos_session.id }]
                       })
                       .then(function(result){
                            if(result){
                                var company = {
                                    email: self.pos.company.email,
                                    website: self.pos.company.website,
                                    company_registry: self.pos.company.company_registry,
                                    contact_address: self.pos.company.partner_id[1],
                                    vat: self.pos.company.vat,
                                    phone: self.pos.company.phone,
                                    name: self.pos.company.name,
                                    logo:  self.pos.company_logo_base64,
                                }

                                result['company'] = company;
                                result['widget'] = self;

                                $('.pos-receipt-container').html(QWeb.render('wkPosSummaryTicket', {
                                    widget: self,
                                    receipt: self.pos.config,
                                    result: result,
                                }));
                                self.gui.show_screen("print_session_ticket");
                            }
                       });
                    }  
                    else{
                        rpc.query({
                            model:'pos.session',
                            method:'get_session_report_data',
                            args: [{ 'session_id': self.pos.pos_session.id }]
                        })
                        .then(function(result){
                            if(result){
                                var company = {
                                    email: self.pos.company.email,
                                    website: self.pos.company.website,
                                    company_registry: self.pos.company.company_registry,
                                    contact_address: self.pos.company.partner_id[1],
                                    vat: self.pos.company.vat,
                                    phone: self.pos.company.phone,
                                    name: self.pos.company.name,
                                    logo:  self.pos.company_logo_base64,
                                }
                                result['company'] = company;
                                result['widget'] = self;
                                var receipt = QWeb.render('SessionXmlReceipt', result);
                                self.pos.proxy.print_receipt(receipt);
                                self.click_cancel();
                            }
                        });
                    }
                }
                else{
                    setTimeout(function(){
                        self.chrome.do_action('wk_pos_session_report_analysis.action_wk_report_pos_session_summary',{additional_context:{
                            active_ids:[self.pos.pos_session.id],
                        }})
                        .catch(function(err){
                            self.gui.show_popup('error',{
                                'title': _t('The report could not be printed'),
                                'body': _t('Check your internet connection and try again.'),
                            });
                        });
                    },500)
                    self.click_cancel();
                }
            }
            else{
                if($('#session_from_date').val() ==''){
                    $('#session_from_date').removeClass('text_shake');
                    $('#session_from_date').focus();
                    $('#session_from_date').addClass('text_shake');
                    return;
                }
                else if ($('#session_to_date').val() ==''){
                    $('#session_to_date').removeClass('text_shake');
                    $('#session_to_date').focus();
                    $('#session_to_date').addClass('text_shake');
                    return;
                }
                else{
                    let f_date = $('#session_from_date').val()
                    f_date = new Date(f_date);
                    f_date = f_date.getTime() + (f_date.getTimezoneOffset() * 60000);
                    f_date = moment(f_date).format('YYYY-MM-DD HH:mm:ss')

                    let to_date = $('#session_to_date').val()                    
                    to_date = new Date(to_date);
                    to_date = to_date.getTime() + (to_date.getTimezoneOffset() * 60000);
                    to_date = moment(to_date).format('YYYY-MM-DD HH:mm:ss')

                    if(self.pos.config.wk_report_print_type != 'pdf'){
                        if(self.pos.config.wk_report_print_type != 'posbox'){
                            rpc.query({
                                model:'wk.pos.details.wizard',
                                method:'get_report_data',
                                args: [{'config_id':self.pos.config.id, 'start_date': f_date , 'end_date':to_date}]
                           })
                           .then(function(result){                            
                                if(result){
                                    var company = {
                                        email: self.pos.company.email,
                                        website: self.pos.company.website,
                                        company_registry: self.pos.company.company_registry,
                                        contact_address: self.pos.company.partner_id[1],
                                        vat: self.pos.company.vat,
                                        phone: self.pos.company.phone,
                                        name: self.pos.company.name,
                                        logo:  self.pos.company_logo_base64,
                                    }
    
                                    result['from_date'] = $('#session_from_date').val();
                                    result['to_date'] = $('#session_to_date').val()
                                    result['company'] = company;
                                    result['widget'] = self;    
                                    $('.pos-receipt-container').html(QWeb.render('wkPosSummaryTicket', {
                                        widget: self,
                                        receipt: self.pos.config,
                                        result: result,
                                    }));
                                    self.gui.show_screen("print_session_ticket");
                                }
                           });
                        }
                        else{
                            rpc.query({
                                model:'wk.pos.details.wizard',
                                method:'get_report_data',
                                args: [{'config_id':self.pos.config.id, 'start_date': f_date , 'end_date':to_date}]
                            })
                            .then(function(result){
                                if(result){
                                    var company = {
                                        email: self.pos.company.email,
                                        website: self.pos.company.website,
                                        company_registry: self.pos.company.company_registry,
                                        contact_address: self.pos.company.partner_id[1],
                                        vat: self.pos.company.vat,
                                        phone: self.pos.company.phone,
                                        name: self.pos.company.name,
                                        logo:  self.pos.company_logo_base64,
                                    }
                                    result['from_date'] = $('#session_from_date').val();
                                    result['to_date'] = $('#session_to_date').val()
                                    result['company'] = company;
                                    result['widget'] = self;
                                    var receipt = QWeb.render('SessionXmlReceipt', result);
                                    self.pos.proxy.print_receipt(receipt);
                                }
                                self.click_cancel();
                            });
                        }
                    }
                    else{
                        rpc.query({
                            model:'wk.pos.details.wizard',
                            method:'create',
                            args: [{'config_id':self.pos.config.id, 'start_date':f_date , 'end_date':to_date}]
                        })
                        .then(function(result){
                            self.chrome.do_action('wk_pos_session_report_analysis.action_wk_report_pos_session_summary_by_date',{additional_context:{
                                active_ids:[result],
                            }})
                            .catch(function(err){
                                self.gui.show_popup('error',{
                                    'title': _t('The report could not be printed'),
                                    'body': _t('Check your internet connection and try again.'),
                                });
                            });
                            self.click_cancel();
                        });
                    }
                }
            }
        },
	});
	gui.define_popup({ name: 'session_report', widget: SessionReportPopup });

    var SessionReportButtonWidget = screens.ActionButtonWidget.extend({
        template: 'SessionReportButtonWidget',
        button_click: function() {
            var self = this;
            var session_id = self.pos.pos_session.id;
            console.log('SessionReportButtonWidget button click customer',self.pos.get_order().get_client());
            self.pos.chrome.gui.show_popup('session_report')
           
        },
    });
    
    screens.define_action_button({
        'name': 'Session Summary',
        'widget': SessionReportButtonWidget,
        'condition': function() {
                return true
        },
    });
});
