from app.common.helpers import *

from flask import render_template, g
from flask.views import MethodView
import json

# label_string = ['Campaign', 'Campaign ID', 'Date', 'Click-through URL', 'Creative Type', 'Ad',
#     'Ad ID', 'Media Cost', 'Impressions', 'Clicks', 'Click Rate', 'Total Conversions',
#     'Cost Per Click', 'Effective CPM', 'Activity Per Click', 'Activity Per Thousand Impressions',
#     'Click-through Conversions', 'Click-through Revenue', 'Revenue Per Click',
#     'Revenue Per Thousand Impressions', 'Total Revenue', 'View-through Conversions',
#     'View-through Revenue']

label_string = ['Impressions', 'Total Revenue']

class Home(MethodView):
    def get(self):
        return render_template('index.html', label_string=label_string)
