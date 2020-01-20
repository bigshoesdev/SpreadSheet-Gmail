from app.config import LocalConfig
import pymysql
import imaplib
import email
import os
from zipfile import ZipFile 
from xml.dom import minidom

userEmail = 'jianglovelyman0319@gmail.com'
passwd = 'Partner123'

con = pymysql.connect(LocalConfig.MYSQL['HOST'], LocalConfig.MYSQL['USER'],
                      LocalConfig.MYSQL['PASS'], LocalConfig.MYSQL['DB'])

report = {
            'campaign': '', 'campaign_id': 0, 'date_str': '', 'click_through_url': '', 'creative_type': '', 'ad_str': '',
            'ad_id': 0, 'media_cost': 0, 'impressions': 0, 'clicks': 0, 'click_rate': 0, 'total_conversions': 0,
            'cost_per_click': 0, 'effective_cpm': 0, 'activity_per_click': 0, 'activity_per_thousand_impressions': 0,
            'click_through_conversions': 0, 'click_through_revenue': 0, 'revenue_per_click': 0,
            'revenue_per_thousand_impressions': 0, 'total_revenue': 0, 'view_through_conversions': 0,
            'view_through_revenue': 0
        }

report_col_index = {
    'campaign': -1, 'campaign_id': -1, 'date_str': -1, 'click_through_url': -1, 'creative_type': -1, 'ad_str': -1,
    'ad_id': -1, 'media_cost': -1, 'impressions': -1, 'clicks': -1, 'click_rate': -1, 'total_conversions': -1,
    'cost_per_click': -1, 'effective_cpm': -1, 'activity_per_click': -1, 'activity_per_thousand_impressions': -1,
    'click_through_conversions': -1, 'click_through_revenue': -1, 'revenue_per_click': -1,
    'revenue_per_thousand_impressions': -1, 'total_revenue': -1, 'view_through_conversions': -1,
    'view_through_revenue': -1
}

label_string = ['Campaign', 'Campaign ID', 'Date', 'Click-through URL', 'Creative Type', 'Ad',
    'Ad ID', 'Media Cost', 'Impressions', 'Clicks', 'Click Rate', 'Total Conversions',
    'Cost Per Click', 'Effective CPM', 'Activity Per Click', 'Activity Per Thousand Impressions',
    'Click-through Conversions', 'Click-through Revenue', 'Revenue Per Click',
    'Revenue Per Thousand Impressions', 'Total Revenue', 'View-through Conversions',
    'View-through Revenue']

def read_gmail(user_email, password):
    try:
        imp_session = imaplib.IMAP4_SSL('imap.gmail.com')
        success, account_details = imp_session.login(user_email, password)

        if success != 'OK':
            print('Not able to sign in with your credential')
            raise

        imp_session.select('Inbox')
        success, data = imp_session.search(None, 'UnSeen')

        if success != 'OK':
            print('Error searching message in inbox')
            raise

        for msgId in data[0].split():
            success, message_parts = imp_session.fetch(msgId, '(RFC822)')
            if success != 'OK':
                print('Error fetching mail id = ' + msgId)
                continue

            email_body = message_parts[0][1]
            mail = email.message_from_string(email_body.decode("utf-8"))

            for part in mail.walk():
                if part.get_content_maintype() == 'multipart':
                    continue

                if part.get('Content-Disposition') is None:
                    continue

                file_name = part.get_filename()

                if file_name.endswith('xlsx'):
                  if bool(file_name):
                    if 'attachments' not in os.listdir("."):
                        os.mkdir('attachments')
                    file_path = os.path.join(".", 'attachments', file_name)
                    if not os.path.isfile(file_path):
                        fp = open(file_path, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()
                        read_xls(file_path)
        imp_session.close()
        imp_session.logout()
    except Exception as e:
        print(e)


def read_xls(file_path):
    with ZipFile(file_path, 'r') as zip: 
        worksheet_paths = []

        # Reading the Content Types in xlsx
        content_type_doc = minidom.parseString(zip.read("[Content_Types].xml"))
        for override_element in content_type_doc.getElementsByTagName("Override"):
            if override_element.getAttribute("ContentType") == 'application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml' :
                worksheet_paths.append(override_element.getAttribute('PartName'))

        def read_value(ele):
            t_data = ele.getElementsByTagName("t")

            if(t_data):
                pass
            else:
                t_data = ele.getElementsByTagName("v")

            if(t_data):
                if(t_data[0].firstChild):
                    t_data_str = t_data[0].firstChild.nodeValue
                    return t_data_str
                else:
                    return ''
            else:
                return ''

        # Reading Worksheet from the xlsx
        start_read = False
        for worksheet_path in worksheet_paths:
            worksheet_doc = minidom.parseString(zip.read(worksheet_path[1:]))
            for sheet_data in worksheet_doc.getElementsByTagName("sheetData"):
                for row_data in sheet_data.getElementsByTagName("row"):
                    col_datas = row_data.getElementsByTagName("c")

                    t_data = col_datas[0].getElementsByTagName("t")
                    t_data_str = read_value(col_datas[0])
                    print(t_data_str)
                    if(t_data_str == 'Grand Total:'):
                            start_read = False

                    if(start_read):

                        for key in report.keys():
                            if(report_col_index[key] >= 0 ):
                                t_data_str = read_value(col_datas[report_col_index[key]])
                                report[key] = t_data_str
                                print(report[key])

                        # print(report)

                        insert_data(report)

                    if(t_data_str == 'Campaign'):
                        start_read = True
                        col_datas = row_data.getElementsByTagName("c")

                        label_keys = list(report.keys())

                        for i in range(len(col_datas)):
                            t_data_str = read_value(col_datas[i])
                            for j in range(len(label_string)):
                                if(label_string[j] == t_data_str):
                                    report_col_index[label_keys[j]] = i
                                    break
                        # print(report_col_index)                        

def insert_data(report):
    with con:
        cur = con.cursor()
        query = "INSERT INTO campaign_has_reports (campaign, campaign_id, date_str, click_through_url, " \
                "creative_type, ad_str, ad_id, media_cost, impressions, clicks, click_rate, total_conversions," \
                "cost_per_click, effective_cpm, activity_per_click, activity_per_thousand_impressions, click_through_conversions, " \
                "click_through_revenue, revenue_per_click, revenue_per_thousand_impressions, " \
                "total_revenue, view_through_conversions, view_through_revenue) " \
                "VALUES('{}', {}, '{}', '{}', '{}', '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})"

        str = query.format(report['campaign'], report['campaign_id'], report['date_str'], report['click_through_url'],
                         report['creative_type'], report['ad_str'], report['ad_id'], report['media_cost'],
                         report['impressions'],
                         report['clicks'], report['click_rate'], report['total_conversions'], report['cost_per_click'],
                         report['effective_cpm'], report['activity_per_click'],
                         report['activity_per_thousand_impressions'],
                         report['click_through_conversions'], report['click_through_revenue'],
                         report['revenue_per_click'],
                         report['revenue_per_thousand_impressions'], report['total_revenue'],
                         report['view_through_conversions'],
                         report['view_through_revenue'])

        cur.execute(
            query.format(report['campaign'], report['campaign_id'], report['date_str'], report['click_through_url'],
                         report['creative_type'], report['ad_str'], report['ad_id'], report['media_cost'],
                         report['impressions'],
                         report['clicks'], report['click_rate'], report['total_conversions'], report['cost_per_click'],
                         report['effective_cpm'], report['activity_per_click'],
                         report['activity_per_thousand_impressions'],
                         report['click_through_conversions'], report['click_through_revenue'],
                         report['revenue_per_click'],
                         report['revenue_per_thousand_impressions'], report['total_revenue'],
                         report['view_through_conversions'],
                         report['view_through_revenue']))

# read_gmail(userEmail, passwd)
read_xls("./attachments/1.xlsx")