################################
#
#  Build App
#
################################

import os
import logging

from datetime import datetime
from logging.config import dictConfig

from flask import Flask, g, current_app, request, make_response
from flask_restful import abort
from flask_cors import CORS

from app.config import LocalConfig
from app.common.extensions import CustomApi
from app.common.database import Database
from app.common.helpers import default_schema, milli_time

from app.views.home import *
from app.views.api import *


def create_app(production=False):
	config = LocalConfig

	# Create app
	app = Flask(__name__)
	app.config.from_object(config)
	app.config['TEMPLATES_AUTO_RELOAD'] = True
	app.secret_key = app.config['APP_SECRET_KEY']
	app.url_map.strict_slashes = False
	app.jinja_env.cache = {}
	app.jinja_env.auto_reload = True

	# create api
	CORS(app)
	api = CustomApi(app, prefix='/api/v1')

	# Initializing the logger
	dictConfig(app.config['LOGGING'])

# 	register_extensions(app)
	register_hooks(app)
# 	register_endpoints(api)
	register_routes(app)

	return app

def register_hooks(app):
	def db_has_connection():
		return hasattr(g,'db')
	
	def get_db_connection():
		if not db_has_connection():
			try:
				g.db = Database(
					host=current_app.config['MYSQL']['HOST'],
					db=current_app.config['MYSQL']['DB'],
					user=current_app.config['MYSQL']['USER'],
					passwd=current_app.config['MYSQL']['PASS'],
				)
			except Exception as e:
				abort(500,
					status=0,
					message='Failed to connect to CORE Database.',
					errors=dict(
						application='There was a problem connecting to MySQL.',
						validation=None
					), 
					http_status=500
				)
		return g.db
	
	@app.before_request
	def before_request():
		if request.path.startswith('/favicon.ico'):
			response = make_response('', 204)
			response.headers['Content-Length'] = 0
			response.status_code = 204
			return response

		g.start_time = milli_time()

		get_db_connection()

	@app.teardown_request
	def close_db_connection(ex):
		if db_has_connection():
			conn = get_db_connection()
			conn.close()


def register_routes(app):

	#############################################
	#
	#	Dashboard home
	
	# Campaigns
	app.add_url_rule('/', view_func=Home.as_view('home'))
	app.add_url_rule('/api', methods=["GET", "POST"], view_func=Api.as_view('api'))


