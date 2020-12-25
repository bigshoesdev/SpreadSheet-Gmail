"""
	A very simple wrapper for MySQLdb

	Methods:
		getOne() - get a single row
		getAll() - get all rows
		lastId() - get the last insert id
		lastQuery() - get the last executed query
		insert() - insert a row
		insertBatch() - Batch Insert
		insertOrUpdate() - insert a row or update it if it exists
		update() - update rows
		delete() - delete rows
		query()  - run a raw sql query

	License: GNU GPLv2

	Kailash Nadh, http://nadh.in
	May 2013
"""

import pymysql as MySQLdb
import warnings

from collections import namedtuple
from itertools import repeat

warnings.filterwarnings('error', category=MySQLdb.Warning)

class Database:
	conn = None
	cur = None
	conf = None

	def __init__(self, **kwargs):
		self.conf = kwargs
		self.conf['keep_alive'] = kwargs.get('keep_alive', False)
		self.conf['charset'] = kwargs.get('charset', 'utf8')
		self.conf['host'] = kwargs.get('host', 'localhost')
		self.conf['port'] = kwargs.get('port', 3306)
		self.conf['autocommit'] = kwargs.get('autocommit', False)
		self.conf['ssl'] = kwargs.get('ssl', False)
		self.connect()

	def connect(self):
		"""Connect to the mysql server"""

		try:
			params = dict(
				db=self.conf['db'],
				host=self.conf['host'],
				port=self.conf['port'],
				user=self.conf['user'],
				passwd=self.conf['passwd'],
				charset=self.conf['charset']
			)

			if self.conf['ssl']:
				params.update('ssl', self.conf['ssl'])

			self.conn = MySQLdb.connect(**params)
			#self.cur = self.conn.cursor(MySQLdb.cursors.SSDictCursor)
			self.cur = self.conn.cursor(MySQLdb.cursors.DictCursor)
			self.conn.autocommit(self.conf['autocommit'])
		except:
			print ('MySQL connection failed')
			raise

	def getOne(self, table=None, fields='', where=None, order=None, limit=(1,)):
		"""Get a single result

			table = (str) table_name
			fields = (field1, field2 ...) list of fields to select
			where = ("parameterizedstatement", [parameters])
					eg: ("id=%s and name=%s", [1, "test"])
			order = [field, ASC|DESC]
			limit = [limit1, limit2]
		"""

		cur = self._select(table, fields, where, order, limit)
		result = cur.fetchone()
		result = list(cur)

		if result:
			row = result[0]
		else:
			row = None
			#Row = namedtuple("Row", [f[0] for f in cur.description])
			#row = Row(*result)

		return row

	def getAll(self, table=None, fields=None, where=None, order=None, limit=None):
		"""Get all results

			table = (str) table_name
			fields = (field1, field2 ...) list of fields to select
			where = ("parameterizedstatement", [parameters])
					eg: ("id=%s and name=%s", [1, "test"])
			order = [field, ASC|DESC]
			limit = [limit1, limit2]
		"""

		cur = self._select(table, fields, where, order, limit)

		return list(cur)

	def getCount(self, table=None, fields=['count(*) as count'], where=None, order=None, limit=None):
		"""Get all results

			table = (str) table_name
			fields = (field1, field2 ...) list of fields to select
			where = ("parameterizedstatement", [parameters])
					eg: ("id=%s and name=%s", [1, "test"])
			order = [field, ASC|DESC]
			limit = [limit1, limit2]
		"""
		cur = self._select(table, fields, where, order, limit)
		return list(cur)[0]['count']

	def lastId(self):
		"""Get the last insert id"""
		return self.cur.lastrowid

	def lastQuery(self):
		"""Get the last executed query"""
		try:
			return self.cur.statement
		except AttributeError:
			return self.cur._last_executed

	def insert(self, table, data):
		"""Insert a record"""
		query = self._serialize_insert(data)
		sql = 'INSERT INTO %s (%s) VALUES(%s)' % (table, query[0], query[1])

		return self.query(sql, list(data.values())).rowcount

	def insertIgnore(self, table, data):
		"""Insert a record"""
		query = self._serialize_insert(data)
		sql = 'INSERT IGNORE INTO %s (%s) VALUES(%s)' % (table, query[0], query[1])

		return self.query(sql, list(data.values())).rowcount

	def insertBatch(self, table, data):
		"""Insert multiple record"""
		query = self._serialize_batch_insert(data)
		sql = 'INSERT INTO %s (%s) VALUES %s' % (table, query[0], query[1])
		flattened_values = [v for sublist in data for k,v in sublist.items()]

		return self.query(sql,flattened_values).rowcount

	def insertIgnoreBatch(self, table, data):
		"""Insert multiple record"""
		query = self._serialize_batch_insert(data)

		sql = 'INSERT IGNORE INTO %s (%s) VALUES %s' % (table, query[0], query[1])

		flattened_values = [v for sublist in data for k,v in sublist.items()]

		return self.query(sql,flattened_values).rowcount

	def update(self, table, data, where = None):
		"""Insert a record"""
		# # update rows based on a parametrized condition
		# db.update("books",
		# 	{"discount": 10},
		# 	("id=%s AND year=%s", [id, year])
		# )
		query = self._serialize_update(data)
		sql = 'UPDATE %s SET %s' % (table, query)

		if where and len(where) > 0:
			sql += ' WHERE %s' % where[0]

		return self.query(sql, list(data.values()) + where[1] if where and len(where) > 1 else data.values()).rowcount

	def insertOrUpdate(self, table, data, keys):
		insert_data = data.copy()
		data = {k: data[k] for k in data if k in keys}

		insert = self._serialize_insert(insert_data)
		update = self._serialize_update(data)

		sql = 'INSERT INTO %s (%s) VALUES(%s) ON DUPLICATE KEY UPDATE %s' % (table, insert[0], insert[1], update)

		return self.query(sql, list(insert_data.values()) + list(data.values()) ).rowcount

	def insertOrUpdateBatch(self, table, data, keys):
		"""Insert multiple records, update if exists"""
		insert_data = data.copy()

		query = self._serialize_batch_insert(data)
		update = self._serialize_batch_update(data[0])

		sql = 'INSERT INTO %s (%s) VALUES %s ON DUPLICATE KEY UPDATE %s' % (table, query[0], query[1], update)

		flattened_values = [v for sublist in data for k,v in sublist.items()]

		return self.query(sql, flattened_values).rowcount

	def delete(self, table, where = None):
		"""Delete rows based on a where condition"""
		sql = 'DELETE FROM {}'.format(table)

		if where and len(where) > 0:
			sql += ' WHERE {}'.format(where[0])

		return self.query(sql, where[1] if where and len(where) > 1 else None).rowcount

# 	def delete_query(self, sql, params = None):
# 		"""Run a raw query"""
#
# 		# check if connection is alive. if not, reconnect
# 		try:
# 			self.cur.execute(sql, params)
# 			self.commit()
#
# 		except MySQLdb.OperationalError as e:
# 			# mysql timed out. reconnect and retry once
# 			if e[0] == 2006:
# 				self.connect()
# 				self.cur.execute(sql, params)
# 			else:
# 				raise
# 		except Warning as a_warning:
# 			pass
# 		except:
# 			#print("Query failed")
# 			raise
#
# 		return self.cur

	def query(self, sql, params = None):
		"""Run a raw query"""
		#print(sql)
		#print(params)
		# check if connection is alive. if not, reconnect
		try:
			print(sql)
			self.cur.execute(sql, params)
		except MySQLdb.OperationalError as e:
# 			print(sql, params)
# 			print(e)
# 			print()
			# mysql timed out. reconnect and retry once
			if e[0] == 2006:
				self.connect()
				self.cur.execute(sql, params)
			else:
				raise
		except Warning as a_warning:
			pass
		except:
			#print("Query failed")
			raise

		return self.cur

	def commit(self):
		"""Commit a transaction (transactional engines like InnoDB require this)"""
		return self.conn.commit()

	def rollback(self):
		"""Rollback a transaction (transactional engines like InnoDB require this)"""
		return self.conn.rollback()

	def is_open(self):
		"""Check if the connection is open"""
		return self.conn.open

	def close(self):
		"""Kill the connection"""
		self.cur.close()
		self.conn.close()

	def _serialize_insert(self, data):
		"""Format insert dict values into strings"""
		keys = ','.join(list(data.keys()))
		vals = ','.join(['%s' for k in data])

		return [keys, vals]

	def _serialize_batch_insert(self, data):
		"""Format insert dict values into strings"""
		keys = ','.join(list(data[0].keys()))
		v = '(%s)' % ','.join(tuple('%s'.rstrip(',') for v in range(len(data[0]))))
		l = ','.join(list(repeat(v,len(data))))
		return [keys, l]

	def _serialize_update(self, data):
		"""Format update dict values into string"""
		return '=%s,'.join(list(data.keys())) + '=%s'

	def _serialize_batch_update(self, data):
		"""Format update dict values into string"""
		return ','.join(['{}=VALUES({})'.format(k,k) for k in data.keys()])

	def _select(self, table=None, fields=(), where=None, order=None, limit=None):
		"""Run a select query"""

		sql = 'SELECT %s FROM `%s`' % (','.join(fields), table)

		# where conditions
		if where and len(where) > 0:
			sql += ' WHERE %s' % where[0]

		# order
		if order:
			sql += ' ORDER BY %s' % order[0]

			if len(order) > 1:
				sql+= ' %s' % order[1]

		# limit
		if limit:
			sql += ' LIMIT %s' % limit[0]

			if len(limit) > 1:
				sql+= ' OFFSET %s' % limit[1]

		return self.query(sql, where[1] if where and len(where) > 1 else None)

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.close()