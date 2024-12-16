from odoo import models, fields, api


class IssueDetailReport(models.TransientModel):
    _name = 'issue.detail.report'

    date_from = fields.Date('From Date', default=fields.Datetime.now)
    date_to = fields.Date('To Date', default=fields.Datetime.now)

    def action_export_excel(self):
        return self.env.ref('drum_quantity.report_issue_detail_list_xlsx').report_action(self)

class IssueDetailXlsx(models.AbstractModel):
    _name = 'report.drum_quantity.report_issue_detail_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('Car List Report')
        bold = workbook.add_format({'bold': True})
        title_format = workbook.add_format({'bold':True, 'font_size': 14, 'font_name': 'Pyidaungsu'})
        title_format.set_center_across('center_across')
        title_format.set_text_wrap()
        title_format.set_align('center_across')
        my_format = workbook.add_format({'font_size': 11, 'font_name': 'Pyidaungsu'})
        my_format.set_bold('bold')
        my_format.set_center_across('center_across')
        my_format.set_text_wrap()
        my_format.set_border()
        number_style = workbook.add_format({'bold':False, 'font_size': 11,'font_name': 'Pyidaungsu'})
        number_style.set_align('center')
        number_style.set_border()
        number_style.set_align('center_across')
        cell_format = workbook.add_format({'bold':False, 'font_size': 11,'font_name': 'Pyidaungsu'})
        cell_format.set_align('left')
        cell_format.set_border()
        cell_format.set_text_wrap()

        cell_format1 = workbook.add_format({'bold':True, 'font_size': 11,'font_name': 'Pyidaungsu'})
        cell_format1.set_align('left')
        cell_format1.set_text_wrap()

        table_header = [
            'စဉ်','DO NO.','ကားနံပါတ်','ယာဥ်မောင်းအမည်','ယာဥ်မောင်းမှတ်ပုံတင်အမှတ်','ဖုန်းနံပါတ်','ဆီထုတ်ယူမည့် (ပေပါ)','ဆီချမည့်လိပ်စာ',
            'ကိုယ်စားလှယ်အမည်','တိုင်း/ပြည်နယ်','ကိုယ်စားလှယ် မှတ်ပုံတင်အမှတ်','ဖုန်းနံပါတ်', 'နေရပ်လိပ်စာ', 'မှတ်ချက်'
        ]
        title = "(" +partners.date_from.strftime("%d.%m.%Y")+ ") ရက်နေ့ ( Ecoharmony  Co.,Ltd မှ ROS ဆီကန်တွင် ဆီထုတ်ယူမည့် ကားစာရင်း )"
        sheet.merge_range('A2:N2',title,title_format)
        
        row = 3
        col = 0
        for th in table_header:
            sheet.write(row,col,th,my_format)
            col +=1
        sheet.set_row(row, height=50, options = None) 
        sheet.set_column('A:A',5)
        sheet.set_column('B:B',23)
        sheet.set_column('C:C',15)
        sheet.set_column('D:D',30)
        sheet.set_column('E:E',35)
        sheet.set_column('F:F',30)
        sheet.set_column('G:G',10)
        sheet.set_column('H:H',50)
        sheet.set_column('I:I',30)
        sheet.set_column('J:J',35)
        sheet.set_column('K:K',40)
        sheet.set_column('L:L',23)
        sheet.set_column('M:M',30)
        sheet.set_column('N:N',10)

        query = """SELECT so.name as do_name,
                       so.truck_no as truck_no,
                       rd.name as driver,
                       so.driver_nrc,
                       (case when so.mobile_one is not null and so.mobile_two is not null then so.mobile_one||', '||so.mobile_two
                            when so.mobile_one is not null and so.mobile_two is null then so.mobile_one
                            when so.mobile_one is null and so.mobile_two is not null then so.mobile_two end ) as driver_phone, 
                       sol.drum_qty,
                       so.oil_address,
                       rp.name as rp_name,
                       rp.x_studio_nrc as rp_nrc,
                       (case when rp.phone is not null then rp.phone else rp.mobile end ) as rp_phone,
                       (coalesce(rp.street,'')||' '||coalesce(rp.street2,'')||' '||coalesce(rp.zip,'')||' '||coalesce(rp.city,'')||' '||coalesce(rcs.name,'')
                                    ||' '||coalesce(rc.name,'')) as address,
                       to_char(sp.issue_date,'dd-mm-yyyy') as issue_date,
                       so.remark
                FROM sale_order so
                LEFT JOIN (select sum(drum_qty) as drum_qty,
                                sum(product_uom_qty) as product_uom_qty,
                                order_id
                            from sale_order_line group by order_id) as sol on sol.order_id=so.id
                LEFT JOIN stock_picking sp on sp.sale_id=so.id
                LEFT JOIN res_partner rp on rp.id=so.partner_id
                LEFT JOIN res_country rc on rc.id=rp.country_id
                LEFT JOIN res_country_state rcs on rcs.id=rp.state_id
                LEFT JOIN res_driver rd on rd.id=so.driver_id
                WHERE sp.sale_id is not null and sp.state  not in ('cancel') and sp.company_name='ECOHARMONY COMPANY LIMITED'
            """

        if partners.date_from:
            where_cause = """ AND so.issue_date >= %s"""
            param = [partners.date_from]
        if partners.date_to:
            where_cause += """ AND so.issue_date <= %s"""
            param.append(partners.date_to)

        order = """ 
                ORDER BY so.issue_date,so.id """
        query = query + where_cause + order
        self.env.cr.execute(query, param)
        responses = self.env.cr.fetchall()
        row = 4
        sequence = 1
        total_drum_qty = 0
        for rec in responses:
            sheet.write(row,0,sequence, number_style)
            sheet.write(row,1,rec[0], cell_format)
            sheet.write(row,2,rec[1], cell_format)
            sheet.write(row,3,rec[2], cell_format)
            sheet.write(row,4,rec[3], cell_format)
            sheet.write(row,5,rec[4], cell_format)
            sheet.write(row,6,rec[5], number_style)
            sheet.write(row,7,rec[6], cell_format)
            sheet.write(row,8,rec[7], cell_format)
            sheet.write(row,9,rec[12], cell_format)
            sheet.write(row,10,rec[8], cell_format)
            sheet.write(row,11,rec[9], cell_format)
            sheet.write(row,12,rec[10], cell_format)
            sheet.write(row,13,' ', cell_format)
            total_drum_qty += rec[5]
            sequence += 1
            row += 1

        sheet.write('A'+str(row+1)+':A'+str(row+1),' ',my_format)
        sheet.write('B'+str(row+1)+':B'+str(row+1),'စုစုပေါင်း',my_format)
        sheet.write('C'+str(row+1)+':C'+str(row+1),' ',my_format)
        sheet.write('D'+str(row+1)+':D'+str(row+1),' ',my_format)
        sheet.write('E'+str(row+1)+':E'+str(row+1),' ',my_format)
        sheet.write('F'+str(row+1)+':F'+str(row+1),' ',my_format)
        sheet.write('G'+str(row+1)+':G'+str(row+1),total_drum_qty,my_format)
        sheet.write('H'+str(row+1)+':H'+str(row+1),' ',my_format)
        sheet.write('I'+str(row+1)+':I'+str(row+1),' ',my_format)
        sheet.write('J'+str(row+1)+':J'+str(row+1),' ',my_format)
        sheet.write('K'+str(row+1)+':K'+str(row+1),' ',my_format)
        sheet.write('L'+str(row+1)+':L'+str(row+1),' ',my_format)
        sheet.write('M'+str(row+1)+':M'+str(row+1),' ',my_format)
        sheet.write('N'+str(row+1)+':N'+str(row+1),' ',my_format)