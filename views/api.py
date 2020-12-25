from app.common.helpers import *

from flask import render_template, g
from flask.views import MethodView
from flask import request
from decimal import Decimal
from flask import jsonify

class DecimalEncoder(json.JSONEncoder):
    def _iterencode(self, o, markers=None):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        return super(DecimalEncoder, self)._iterencode(o, markers)

# report_column = [
#             'campaign', 'campaign_id', 'date_str', 'click_through_url', 'creative_type', 'ad_str',
#             'ad_id', 'media_cost', 'impressions', 'clicks', 'click_rate', 'total_conversions',
#             'cost_per_click', 'effective_cpm', 'activity_per_click', 'activity_per_thousand_impressions',
#             'click_through_conversions', 'click_through_revenue', 'revenue_per_click',
#             'revenue_per_thousand_impressions', 'total_revenue', 'view_through_conversions',
#             'view_through_revenue'
#         ]

report_column = ['impressions', 'total_revenue']

class Api(MethodView):
    def post(self):
        params = request.get_json()
        print(params)

        data1 = params['data1']
        data2 = params['data2']
        report_index = int(params['category']) - 1
        report_current_column = report_column[report_index]

        report_data1 = g.db.query(
            """ SELECT	
                    *
                FROM campaign_has_reports 
                WHERE date_str >= %s AND date_str <= %s
                LIMIT 100 """, (data1['start_date'], data1['end_date']))

        x_data1 = []
        y_data1 = []

        result = {}

        for report1 in list(report_data1):
            x_data1.append(report1['date_str'])
            y_data1.append(float(report1[report_current_column]))
            print(report1[report_current_column])

        result['x_data1'] = x_data1
        result['y_data1'] = y_data1
        
        report_data2 = g.db.query(
            """ SELECT  
                    *
                FROM campaign_has_reports 
                WHERE date_str >= %s AND date_str <= %s
                LIMIT 100 """, (data2['start_date'], data2['end_date']))

        x_data2 = []
        y_data2 = []

        for report2 in list(report_data2):
            x_data2.append(report2['date_str'])
            y_data2.append(float(report2[report_current_column]))

        result['x_data2'] = x_data2
        result['y_data2'] = y_data2

        return jsonify(result)