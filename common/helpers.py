import json
import pytz
import requests

from datetime import datetime, timezone
from time import time
from flask import current_app, make_response, g
from flask_restful import Resource

milli_time = lambda: int(round(time() * 1000))

#######################################
#	Date & Time Formatting
#######################################

def current_date(format='%Y-%m-%d %H:%M:%S'):
	now = datetime.now()
	if format:
		return now.strftime(format)
	return now

def current_date_utc(format='%Y-%m-%d %H:%M:%S'):
	now = datetime.now(timezone.utc)
	if format:
		return now.strftime(format)
	return now

def current_timestamp(convert_to_int=True, in_milliseconds=False):
	now = current_date(False)
	ts = now.timestamp()
	if convert_to_int:
		if in_milliseconds:
			return int(round(ts * 1000.0))
		return int(ts)
	return ts

def format_timestamp(date, in_milliseconds=False):
	ts = date.timestamp()
	if in_milliseconds:
		return int(round(ts * 1000.0))
	return int(ts)

def format_date(date):
	return date.strftime('%Y-%m-%d %H:%M:%S')

def timestamp_to_date(timestamp):
	return datetime.fromtimestamp(timestamp)
	#return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def convert_utc_to_pst_date(utc_date):
	old_timezone = pytz.timezone('UTC')
	new_timezone = pytz.timezone('US/Pacific')
	return old_timezone.localize(utc_date).astimezone(new_timezone)

#######################################
#	Json & Encoding
#######################################

def json_encode(data, separators=(',',':'), indent=None, sort_keys=True):
	return json.dumps(data, separators=(',',':'), indent=indent, sort_keys=sort_keys)

def json_decode(data):
	return json.loads(data)

class JsonDateTimeEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, datetime):
			return o.isoformat()
		return json.JSONEncoder.default(self, o)

#######################################
#	Response Handling
#######################################

def default_schema(data=None, message=None, http_status=200, headers=None):
	"""
	Argument data refers to data or errors, the latter in case of the
	http_status being 4xx or 5xx.
	"""
	if http_status < 400:
		response = {
			'status': 1,
			'http_status': http_status,
			'data': data,
			'message': message
		}, http_status, headers
	else:
		response = {
			'status': 0,
			'http_status': http_status,
			'errors': data,
			'message': message
		}, http_status, headers
	
	if current_app.config['APP_DEBUG_FLASK']:
		response[0]['time'] = milli_time() - g.start_time
		
	return response

# class NoContent(Resource):
# 	def get(self):
# 		resp = make_response('', 204)
# 		resp.headers['Content-Length'] = 0
# 		return resp


