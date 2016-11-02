# encoding: utf-8
import pymysql as mdb
import os.path
import csv
from collections import OrderedDict

"""
	NOTE: there is no protection against SQL injection; the intended use of this function is that
	everything that goes into this function is from this file. Besides, this is intended to be 
	a purely local database. Besides, it's a database of Fire Emblem Data. Is it so big a deal if
	someone thinks that Elise has a base HP of, say, 25 instead of 19?

	You have to create a password.txt in this same folder, where the first line includes your username
	to the database, and the second line includes your password (If you have a weird username or
	password, e.g. with newlines or something, you may need to do weirder things here)
"""

DATABASE_NAME = 'FireEmblemData'

# read password file
with open('password.txt', 'r') as f:
	USERNAME = f.readline()
	PASSWORD = f.readline()
	if len(USERNAME) > 0 and USERNAME[-1] == '\n':
		USERNAME = USERNAME[:-1]
	if len(PASSWORD) > 0 and PASSWORD[-1] == '\n':
		PASSWORD = PASSWORD[:-1]
		
STRING_T = 'VARCHAR(64)' # for names
LONG_STRING_T = 'VARCHAR(1024)' # for descriptions
BOOLEAN_T = 'BOOLEAN'
INT_T = 'INTEGER'

SQL_FILES = [
	{
		'tableName': 'Characters',
		'sourceFile': os.path.join('FE14', 'characters.csv'),
		'schema': {
			'types': OrderedDict([
				# a dict mapping from CharId -> (data type, constraint string)
				('CharId', (STRING_T, 'NOT NULL')),
				('EnglishName', (STRING_T, 'NOT NULL')),
				('Birthright', (BOOLEAN_T, 'NOT NULL')),
				('Conquest', (BOOLEAN_T, 'NOT NULL')),
				('Revelation', (BOOLEAN_T, 'NOT NULL')),
				('IsChild', (BOOLEAN_T, 'NOT NULL')),
				('ClassName', (STRING_T, 'NOT NULL')),
				('BirthdayDay', (INT_T, '')),
				('BirthdayMonth', (INT_T, '')),
				('Description', (LONG_STRING_T, 'NOT NULL'))
				]),
			'primaryKey': 'CharId',
			'foreignKey': {}
		}
	},
	{
		'tableName': 'PersonalSkills',
		'sourceFile': os.path.join('FE14', 'personalskill.csv'),
		'schema': {
			'types': OrderedDict([
				('CharId', (STRING_T, 'NOT NULL')),
				('PersonalSkill', (STRING_T, 'NOT NULL')),
				('Description', (LONG_STRING_T, 'NOT NULL'))
				]),
			'primaryKey': 'CharId', # male and female avatars share a PersonalSkill, so that can't be the key
			'foreignKey': {
				'CharId': ('Characters', 'CharId')
			}
		}
	}
]

def schema_to_SQL_query(tablename, schema):
	"""take in an OrderedDict schema and returns a MYSQL query string that creates such a table
	"""
	if ' ' in tablename:
		raise ValueError('tablename cannot have a space in it')

	toReturnList = ['CREATE TABLE ', tablename, ' (']

	for item in schema['types']:
		toReturnList.append(item)
		toReturnList.append(' ')
		toReturnList.append(schema['types'][item][0])
		toReturnList.append(' ')
		toReturnList.append(schema['types'][item][1])
		toReturnList.append(', \n    ')

	toReturnList.append('PRIMARY KEY (') # remove the last comma-space and replace it what we need next
	toReturnList.append(schema['primaryKey'])
	toReturnList.append(')')
	toReturnList.append(', \n    ')

	for item in schema['foreignKey']:
		toReturnList.append('FOREIGN KEY (')
		toReturnList.append(item)
		toReturnList.append(') REFERENCES ')
		toReturnList.append(schema['foreignKey'][item][0])
		toReturnList.append('(')
		toReturnList.append(schema['foreignKey'][item][1])
		toReturnList.append(')')
		toReturnList.append(', \n    ')

	toReturnList[-1] = ')' 

	return ''.join(toReturnList)

try:
	print('starting')
	sql = '(no sql query made yet)'
	con = mdb.connect('localhost', USERNAME, PASSWORD, charset='utf8mb4');
	cur=con.cursor(mdb.cursors.DictCursor)

	# clear all data from the old database
	sql = 'DROP DATABASE IF EXISTS %s' % DATABASE_NAME
	cur.execute(sql)
	sql = 'CREATE DATABASE %s CHARACTER SET UTF8mb4 COLLATE utf8mb4_bin' % DATABASE_NAME
	cur.execute(sql)
	sql = 'USE %s' % (DATABASE_NAME)
	cur.execute(sql)
	print('successfully dropped and recreated the database')

	for tableData in SQL_FILES:
		sql = schema_to_SQL_query(tableData['tableName'], tableData['schema'])
		print(sql); cur.execute(sql)

		baseSql = ['INSERT INTO ', tableData['tableName'], ' (']
		for jtem in tableData['schema']['types']:
			baseSql.append(jtem)
			baseSql.append(', ')
		baseSql[-1] = ') VALUES ('#delete the final comma-space and replace it with what's necessary
		baseSql = ''.join(baseSql)

		with open(tableData['sourceFile'], 'r', encoding='utf-8') as f:
			reader = csv.DictReader(f)
			for row in reader:
				sql = [baseSql]
				for jtem in tableData['schema']['types']:
					if tableData['schema']['types'][jtem][0] == STRING_T or tableData['schema']['types'][jtem][0] == LONG_STRING_T:
						sql.append('\'')
					sql.append(row[jtem].replace('\'', '\'\'') if row[jtem] != '' else 'null')
					if tableData['schema']['types'][jtem][0] == STRING_T or tableData['schema']['types'][jtem][0] == LONG_STRING_T:
						sql.append('\'')
					sql.append(', ')
				sql[-1] = ')'#delete the final comma-space and replace it with what's necessary
				sql = ''.join(sql)

				cur.execute(sql)
except Exception as e:
	print("\n\nERROR!")
	print("The last SQL command attempted was: %s" % sql)
	print(e)
finally:
	if con:
		try:
			con.commit()
		except Exception as e:
			print(e)
			pass
		con.close()

print('finished')