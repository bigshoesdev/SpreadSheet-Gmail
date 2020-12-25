import os
import logging
import json
from datetime import datetime, timedelta
from app.common.helpers import JsonDateTimeEncoder


################################
################################
#
#  All Servers
#
################################
################################

class BaseConfig(object):
	
	################################
	#
	#	Application Config
	#
	################################
	
	# Set App name
	APP_NAME = 'dashboard_app'
	
	# Set IP Host
	APP_HOST = '127.0.0.1'
	
	# Set IP Host Port
	APP_PORT = 5030
	
	# Current directory
	BASE_DIR = os.path.dirname(os.getcwd())

	# Set app dir
	APP_DIR = '{}/code/app'.format(BASE_DIR)
	
	# Set data dir
	APP_DATA_DIR = '{}/data'.format(BASE_DIR)
	
	# Set data dir
	APP_LOG_DIR = '{}/logs'.format(BASE_DIR)

	# JSON Encoding override to fix datetime
	RESTFUL_JSON = {'cls': JsonDateTimeEncoder}
	BUNDLE_ERRORS = True
	
	################################
	#	Authentication
	################################
	
	JWT_BLACKLIST_ENABLED = True
	JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
	JWT_COOKIE_CSRF_PROTECT = True
	JWT_CLAIMS_IN_REFRESH_TOKEN = True
	BCRYPT_LOG_ROUNDS = 14

	################################
	#	Google ReCaptcha V3 Keys
	################################
	
	RECAPTCHA_V3_SITE_KEY = ''
	RECAPTCHA_V3_SECRET_KEY = ''
	
	################################
	#	Api Keys
	################################
	
	# IPs that are allowed access
	API_ACCESS_IPS = ['0.0.0.0', '127.0.0.1']

	DEBUG_TB_INTERCEPT_REDIRECTS = False
	SECRET_KEY = 'custom_key'
	EMAIL_TOKEN_SECRET_KEY = 'custom_key'
	EMAIL_TOKEN_SALT = 'custom_key'

################################
################################
#
#  Local Dev Server
#
################################
################################

class LocalConfig(BaseConfig):

	################################
	#	Mysql
	################################

	MYSQL = {
		'HOST': '127.0.0.1',
		'DB': 'dashboard_app_db',
		'USER': 'root',
		'PASS': 'scb123',
	}

	################################
	#	Development & Debugging
	################################
	
	# Set debug status
	IS_DEV = True
	DEBUG = True
	APP_DEBUG_FLASK = DEBUG
	PROPAGATE_EXCEPTIONS = False
	LOG_LEVEL = logging.DEBUG
	
	# Set ssl context for local testing
	APP_SSL_CONTEXT = None #'adhoc'
	
	# Compress json
	JSONIFY_PRETTYPRINT_REGULAR = True
	
	################################
	#	Authentication
	################################
	
	JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
	JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=365)
	
	JWT_SECRET_KEY = 'custom_key'
	JWT_RESET_SECRET_KEY = 'custom_key'
	JWT_ALGORITHM = 'HS256'

	APP_SECRET_KEY = 'custom_key'
	APP_API_KEYS = {
		'custom_key': 'App',
	}

	################################
	#	Logger
	################################
	
	LOGGING = {
		'version': 1,
		'disable_existing_loggers': False,
		'root': {
			'level': LOG_LEVEL,
			'handlers': ['console', 'file'],
		},
		'handlers': {
			'console': {
				'class': 'logging.StreamHandler',
				'level': LOG_LEVEL,
				'formatter': 'detailed',
				'stream': 'ext://sys.stdout',
			},
			'file': {
				'class': 'logging.handlers.RotatingFileHandler',
				'level': LOG_LEVEL,
				'formatter': 'detailed',
				'filename': '{}/{}.log'.format(BaseConfig.APP_LOG_DIR, BaseConfig.APP_NAME),
				'mode': 'a',
				'maxBytes': 10485760,
				'backupCount': 5,
			}
		},
		'formatters': {
			'detailed': {
				'format': ('%(asctime)s %(name)-17s line:%(lineno)-4d '
				'%(levelname)-8s %(message)s')
			}
		},
	}

