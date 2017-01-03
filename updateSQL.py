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

	# SET m_small = 0;
	# outerloop: LOOP
	# 	SET k = m_small;
	# 	innerloop1: LOOP
	# 		SET result1 = NFactorial(N_u) / NFactorial(k) / NFactorial(N_u - k);
 #            SET result1  = 1 * POWER(1 - (u/100), N_u - k) * POWER(u/100, k);

	# 		SET k = k + 1;
	# 		IF k > N_u THEN
	# 			LEAVE innerloop1;
	# 		END IF;
	# 	END LOOP innerloop1;

	# 	SET overallresult = overallresult + result1;

	# 	SET m_small = m_small+1;
	# 	IF m_small > M THEN
	# 		LEAVE outerloop;
	# 	END IF;
	# END LOOP outerloop;
import math
def fact(n):
	if n <= 1:
		return 1
	else:
		return n * fact(n-1)


def AtLeastMLevelUps(M, N_u, N_p, u, p):
	m_small = 0
	overallresult = 0.0

	while True:
		k = m_small
		while True:
			result1 = fact(N_u) / fact(k) / fact(N_u - k)
			try:
				result1 = result1 * math.pow(1 - u/100, N_u - k) * math.pow(u/100, k)
			except ValueError as e:
				print(k, N_u)
				raise e

			k = k+1
			if k > N_u:
				break
		overallresult = overallresult + result1

		m_small = m_small+1
		if m_small > M:
			break
	return overallresult

print(AtLeastMLevelUps(3, 5, 0, 100, 0))


exit()

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
CHAR_T = 'CHAR(1)'
INT_T = 'INTEGER'

SQL_FILES = [
	{
		'tableName': 'Classes',
		'sourceFile': os.path.join('FE14', 'classes.csv'),
		'schema': {
			'types': OrderedDict([
				('ClassName', (STRING_T, 'NOT NULL') ),
				('isHoshidan', (BOOLEAN_T, 'NOT NULL') ),
				('isNohrian', (BOOLEAN_T, 'NOT NULL') ),
				('isPromoted', (BOOLEAN_T, 'NOT NULL') ),
				('isSpecial', (BOOLEAN_T, 'NOT NULL') ),
				('canBeMale', (BOOLEAN_T, 'NOT NULL') ),
				('canBeFemale', (BOOLEAN_T, 'NOT NULL') ),
				('Description', (LONG_STRING_T, 'NOT NULL') )
				]),
			'primaryKey': 'ClassName',
			'foreignKey': {}
		},
		'triggers': []
	},
	{
		'tableName': 'Characters',
		'sourceFile': os.path.join('FE14', 'characters.csv'),
		'schema': {
			'types': OrderedDict([
				# a dict mapping from CharId -> (data type, constraint string)
				('CharId', (STRING_T, 'NOT NULL')),
				('EnglishName', (STRING_T, 'NOT NULL')),
				('isMale', (BOOLEAN_T, 'NOT NULL')),
				('isFemale', (BOOLEAN_T, 'NOT NULL')),
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
			'foreignKey': {
				'ClassName': ('Classes', 'ClassName')
			}
		},
		'triggers': [
			'''CREATE TRIGGER Characters_oneGender
				BEFORE INSERT ON Characters FOR EACH ROW
				IF NOT (NEW.isMale XOR NEW.isFemale)
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Every character must have a single gender.';
				END IF;'''# only one gender at a time
		]
	},
	{
		'tableName': 'WeaponTypes',
		'sourceFile': os.path.join('FE14', 'weapontypes.csv'),
		'schema': {
			'types': OrderedDict([
				('WeaponType', (STRING_T, 'NOT NULL')),
				('NohrName', (STRING_T, 'NOT NULL')),
				('HoshidoName', (STRING_T, 'NOT NULL'))
				]),
			'primaryKey': 'WeaponType',
			'foreignKey': {}
		},
		'triggers': []
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
		},
		'triggers': []
	},
	{
		'tableName': 'Reclasses',
		'sourceFile': os.path.join('FE14', 'reclasses.csv'),
		'schema': {
			'types': OrderedDict([
				('CharId', (STRING_T, 'NOT NULL')),
				('BaseClassName', (STRING_T, 'NOT NULL'))
				]),
			'primaryKey': 'CharId,BaseClassName', # neither name nor class alone is unique
			'foreignKey': {
				'CharId': ('Characters', 'CharId'),
				'BaseClassName': ('Classes',  'ClassName')
			}
		},
		'triggers': [
			'''CREATE TRIGGER Reclasses_Baseclass
				BEFORE INSERT ON Reclasses FOR EACH ROW
				IF (SELECT NOT EXISTS(SELECT * FROM Classes C WHERE NOT C.isPromoted AND C.ClassName = NEW.BaseClassName))
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Characters can only reclass to a base class.';
				END IF;'''# reclasses must be to a base class
		]
	},
	{
		'tableName': 'ClassPromotions',
		'sourceFile': os.path.join('FE14', 'classpromotions.csv'),
		'schema': {
			'types': OrderedDict([
				('PromotedClass', (STRING_T, 'NOT NULL')),
				('BaseClass', (STRING_T, 'NOT NULL'))
				]),
			'primaryKey': 'PromotedClass,BaseClass', # neither promoted nor base classes alone are unique
			'foreignKey': {
				'PromotedClass': ('Classes',  'ClassName'),
				'BaseClass': ('Classes',  'ClassName')
			}
		},
		'triggers': [
			'''CREATE TRIGGER ClassPromotions_Baseclass
				BEFORE INSERT ON ClassPromotions FOR EACH ROW
				IF (SELECT NOT EXISTS(SELECT * FROM Classes C WHERE NOT C.isPromoted AND C.ClassName = NEW.BaseClass))
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Characters can only promote from a base class.';
				ELSEIF (SELECT NOT EXISTS(SELECT * FROM Classes C WHERE C.isPromoted AND C.ClassName = NEW.PromotedClass))
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Characters can only promote to a promoted class.';
				END IF;''',
		]
	},
	{
		'tableName': 'ClassStats',
		'sourceFile': os.path.join('FE14', 'classstats.csv'),
		'schema': {
			'types': OrderedDict([
				('ClassName', (STRING_T, 'NOT NULL')),
				('BaseHP', (INT_T, 'NOT NULL')),
				('BaseStr', (INT_T, 'NOT NULL')),
				('BaseMag', (INT_T, 'NOT NULL')),
				('BaseSkl', (INT_T, 'NOT NULL')),
				('BaseSpd', (INT_T, 'NOT NULL')),
				('BaseLck', (INT_T, 'NOT NULL')),
				('BaseDef', (INT_T, 'NOT NULL')),
				('BaseRes', (INT_T, 'NOT NULL')),
				('BaseMov', (INT_T, 'NOT NULL')),
				('HitBoost', (INT_T, 'NOT NULL')),
				('AvoBoost', (INT_T, 'NOT NULL')),
				('CrtBoost', (INT_T, 'NOT NULL')),
				('CEvBoost', (INT_T, 'NOT NULL')),
				('GrowthHP', (INT_T, 'NOT NULL')),
				('GrowthStr', (INT_T, 'NOT NULL')),
				('GrowthMag', (INT_T, 'NOT NULL')),
				('GrowthSkl', (INT_T, 'NOT NULL')),
				('GrowthSpd', (INT_T, 'NOT NULL')),
				('GrowthLck', (INT_T, 'NOT NULL')),
				('GrowthDef', (INT_T, 'NOT NULL')),
				('GrowthRes', (INT_T, 'NOT NULL')),
				('MaxHP', (INT_T, 'NOT NULL')),
				('MaxStr', (INT_T, 'NOT NULL')),
				('MaxMag', (INT_T, 'NOT NULL')),
				('MaxSkl', (INT_T, 'NOT NULL')),
				('MaxSpd', (INT_T, 'NOT NULL')),
				('MaxLck', (INT_T, 'NOT NULL')),
				('MaxDef', (INT_T, 'NOT NULL')),
				('MaxRes', (INT_T, 'NOT NULL'))
				]),
			'primaryKey': 'ClassName',
			'foreignKey': {
				'ClassName': ('Classes',  'ClassName')
			}
		},
		'triggers': []
	},
	{
		'tableName': 'ClassWeapons',
		'sourceFile': os.path.join('FE14', 'classweapons.csv'),
		'schema': {
			'types': OrderedDict([
				('ClassName', (STRING_T, 'NOT NULL')),
				('WeaponType', (STRING_T, 'NOT NULL')),
				('MaxWeaponRank', (CHAR_T, 'NOT NULL'))
				]),
			'primaryKey': 'ClassName,WeaponType',
			'foreignKey': {
				'ClassName': ('Classes',  'ClassName'),
				'WeaponType': ('WeaponTypes',  'WeaponType')
			}
		},
		'triggers': []
	},
	{
		'tableName': 'CharacterStats',
		'sourceFile': os.path.join('FE14', 'characterstats.csv'),
		'schema': {
			'types': OrderedDict([
				('CharId', (STRING_T, 'NOT NULL')),
				('GrowthHP', (INT_T, 'NOT NULL')),
				('GrowthStr', (INT_T, 'NOT NULL')),
				('GrowthMag', (INT_T, 'NOT NULL')),
				('GrowthSkl', (INT_T, 'NOT NULL')),
				('GrowthSpd', (INT_T, 'NOT NULL')),
				('GrowthLck', (INT_T, 'NOT NULL')),
				('GrowthDef', (INT_T, 'NOT NULL')),
				('GrowthRes', (INT_T, 'NOT NULL')),
				('ModifierMaxStr', (INT_T, 'NOT NULL')),
				('ModifierMaxMag', (INT_T, 'NOT NULL')),
				('ModifierMaxSkl', (INT_T, 'NOT NULL')),
				('ModifierMaxSpd', (INT_T, 'NOT NULL')),
				('ModifierMaxLck', (INT_T, 'NOT NULL')),
				('ModifierMaxDef', (INT_T, 'NOT NULL')),
				('ModifierMaxRes', (INT_T, 'NOT NULL'))
				]),
			'primaryKey': 'CharId',
			'foreignKey': {
				'CharId': ('Characters',  'CharId')
			}
		},
		'triggers': [
			'''CREATE TRIGGER CharacterStats_NoChildren
				BEFORE INSERT ON CharacterStats FOR EACH ROW
				IF (SELECT EXISTS(SELECT * FROM Characters C WHERE C.isChild AND C.CharId = NEW.CharId))
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'CharacterStats can only hold non-child characters.';
				END IF;''',
		]
	},
	{
		'tableName': 'ChildrenStats',
		'sourceFile': os.path.join('FE14', 'childrenstats.csv'),
		'schema': {
			'types': OrderedDict([
				('CharId', (STRING_T, 'NOT NULL')),
				('GrowthHP', (INT_T, 'NOT NULL')),
				('GrowthStr', (INT_T, 'NOT NULL')),
				('GrowthMag', (INT_T, 'NOT NULL')),
				('GrowthSkl', (INT_T, 'NOT NULL')),
				('GrowthSpd', (INT_T, 'NOT NULL')),
				('GrowthLck', (INT_T, 'NOT NULL')),
				('GrowthDef', (INT_T, 'NOT NULL')),
				('GrowthRes', (INT_T, 'NOT NULL'))
				]),
			'primaryKey': 'CharId',
			'foreignKey': {
				'CharId': ('Characters',  'CharId')
			}
		},
		'triggers': [
			'''CREATE TRIGGER ChildrenStats_OnlyChildren
				BEFORE INSERT ON ChildrenStats FOR EACH ROW
				IF (SELECT NOT EXISTS(SELECT * FROM Characters C WHERE C.isChild AND C.CharId = NEW.CharId))
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ChildrenStats can only hold child characters.';
				END IF;''',
		]
	},
	{
		'tableName': 'CharacterBaseStats',
		'sourceFile': os.path.join('FE14', 'characterbasestats.csv'),
		'schema': {
			'types': OrderedDict([
				('CharId', (STRING_T, 'NOT NULL')),
				('inBirthright', (BOOLEAN_T, 'NOT NULL')),
				('inConquest', (BOOLEAN_T, 'NOT NULL')),
				('inRevelation', (BOOLEAN_T, 'NOT NULL')),
				('Chapter', (STRING_T, 'NOT NULL')),
				('Class', (STRING_T, 'NOT NULL')),
				('BaseLevel', (INT_T, 'NOT NULL')),
				('BaseHP', (INT_T, 'NOT NULL')),
				('BaseStr', (INT_T, 'NOT NULL')),
				('BaseMag', (INT_T, 'NOT NULL')),
				('BaseSkl', (INT_T, 'NOT NULL')),
				('BaseSpd', (INT_T, 'NOT NULL')),
				('BaseLck', (INT_T, 'NOT NULL')),
				('BaseDef', (INT_T, 'NOT NULL')),
				('BaseRes', (INT_T, 'NOT NULL'))
				]),
			'primaryKey': 'CharId,inBirthright,inConquest,inRevelation,Chapter',
			'foreignKey': {
				'CharId': ('Characters',  'CharId'),
				'Class': ('Classes',  'ClassName')
			}
		},
		'triggers': [
			'''CREATE TRIGGER CharacterBaseStats_NoChildren
				BEFORE INSERT ON CharacterBaseStats FOR EACH ROW
				IF (SELECT EXISTS(SELECT * FROM Characters C WHERE C.isChild AND C.CharId = NEW.CharId))
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'CharacterBaseStats can only hold non-child characters.';
				END IF;''',
		]
	},
	{
		'tableName': 'ChildrenBaseStats',
		'sourceFile': os.path.join('FE14', 'childrenbasestats.csv'),
		'schema': {
			'types': OrderedDict([
				('CharId', (STRING_T, 'NOT NULL')),
				('Chapter', (STRING_T, 'NOT NULL')),
				('Class', (STRING_T, 'NOT NULL')),
				('BaseLevel', (INT_T, 'NOT NULL')),
				('BaseHP', (INT_T, 'NOT NULL')),
				('BaseStr', (INT_T, 'NOT NULL')),
				('BaseMag', (INT_T, 'NOT NULL')),
				('BaseSkl', (INT_T, 'NOT NULL')),
				('BaseSpd', (INT_T, 'NOT NULL')),
				('BaseLck', (INT_T, 'NOT NULL')),
				('BaseDef', (INT_T, 'NOT NULL')),
				('BaseRes', (INT_T, 'NOT NULL'))
				]),
			'primaryKey': 'CharId',
			'foreignKey': {
				'CharId': ('Characters',  'CharId'),
				'Class': ('Classes',  'ClassName')
			}
		},
		'triggers': [
			'''CREATE TRIGGER ChildrenBaseStats_OnlyChildren
				BEFORE INSERT ON ChildrenBaseStats FOR EACH ROW
				IF (SELECT NOT EXISTS(SELECT * FROM Characters C WHERE C.isChild AND C.CharId = NEW.CharId))
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ChildrenBaseStats can only hold child characters.';
				END IF;''',
		]
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
		# create the table
		sql = schema_to_SQL_query(tableData['tableName'], tableData['schema'])
		print(sql); cur.execute(sql)

		# run any triggers
		for trigger in tableData['triggers']:
			sql = trigger
			print(sql); cur.execute(sql)

		# insert values
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
					# escape strings
					if tableData['schema']['types'][jtem][0] in [STRING_T, LONG_STRING_T, CHAR_T]:
						sql.append('\'')
					sql.append(row[jtem].replace('\'', '\'\'') if row[jtem] != '' else 'null')
					if tableData['schema']['types'][jtem][0] in [STRING_T, LONG_STRING_T, CHAR_T]:
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