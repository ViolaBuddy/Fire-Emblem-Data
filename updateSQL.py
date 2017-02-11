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
CHAR_T = 'CHAR(1)'
INT_T = 'INTEGER'

SQL_FILES_FE14 = [
	{
		'tableName': 'FE14_Classes',
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
		'tableName': 'FE14_Characters',
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
				'ClassName': ('FE14_Classes', 'ClassName')
			}
		},
		'triggers': [
			'''CREATE TRIGGER FE14_Characters_oneGender
				BEFORE INSERT ON FE14_Characters FOR EACH ROW
				IF NOT (NEW.isMale XOR NEW.isFemale)
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'FE14_Every character must have a single gender.';
				END IF;'''# only one gender at a time
		]
	},
	{
		'tableName': 'FE14_WeaponTypes',
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
		'tableName': 'FE14_PersonalSkills',
		'sourceFile': os.path.join('FE14', 'personalskill.csv'),
		'schema': {
			'types': OrderedDict([
				('CharId', (STRING_T, 'NOT NULL')),
				('PersonalSkill', (STRING_T, 'NOT NULL')),
				('Description', (LONG_STRING_T, 'NOT NULL'))
				]),
			'primaryKey': 'CharId', # male and female avatars share a PersonalSkill, so that can't be the key
			'foreignKey': {
				'CharId': ('FE14_Characters', 'CharId')
			}
		},
		'triggers': []
	},
	{
		'tableName': 'FE14_Reclasses',
		'sourceFile': os.path.join('FE14', 'reclasses.csv'),
		'schema': {
			'types': OrderedDict([
				('CharId', (STRING_T, 'NOT NULL')),
				('BaseClassName', (STRING_T, 'NOT NULL'))
				]),
			'primaryKey': 'CharId,BaseClassName', # neither name nor class alone is unique
			'foreignKey': {
				'CharId': ('FE14_Characters', 'CharId'),
				'BaseClassName': ('FE14_Classes',  'ClassName')
			}
		},
		'triggers': [
			'''CREATE TRIGGER FE14_Reclasses_Baseclass
				BEFORE INSERT ON FE14_Reclasses FOR EACH ROW
				IF (SELECT NOT EXISTS(SELECT * FROM FE14_Classes C WHERE NOT C.isPromoted AND C.ClassName = NEW.BaseClassName))
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'FE14_Characters can only reclass to a base class.';
				END IF;'''# reclasses must be to a base class
		]
	},
	{
		'tableName': 'FE14_ClassPromotions',
		'sourceFile': os.path.join('FE14', 'classpromotions.csv'),
		'schema': {
			'types': OrderedDict([
				('PromotedClass', (STRING_T, 'NOT NULL')),
				('BaseClass', (STRING_T, 'NOT NULL'))
				]),
			'primaryKey': 'PromotedClass,BaseClass', # neither promoted nor base classes alone are unique
			'foreignKey': {
				'PromotedClass': ('FE14_Classes',  'ClassName'),
				'BaseClass': ('FE14_Classes',  'ClassName')
			}
		},
		'triggers': [
			'''CREATE TRIGGER FE14_ClassPromotions_Baseclass
				BEFORE INSERT ON FE14_ClassPromotions FOR EACH ROW
				IF (SELECT NOT EXISTS(SELECT * FROM FE14_Classes C WHERE NOT C.isPromoted AND C.ClassName = NEW.BaseClass))
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'FE14_Characters can only promote from a base class.';
				ELSEIF (SELECT NOT EXISTS(SELECT * FROM FE14_Classes C WHERE C.isPromoted AND C.ClassName = NEW.PromotedClass))
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'FE14_Characters can only promote to a promoted class.';
				END IF;''',
		]
	},
	{
		'tableName': 'FE14_ClassStats',
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
				'ClassName': ('FE14_Classes',  'ClassName')
			}
		},
		'triggers': []
	},
	{
		'tableName': 'FE14_ClassWeapons',
		'sourceFile': os.path.join('FE14', 'classweapons.csv'),
		'schema': {
			'types': OrderedDict([
				('ClassName', (STRING_T, 'NOT NULL')),
				('WeaponType', (STRING_T, 'NOT NULL')),
				('MaxWeaponRank', (CHAR_T, 'NOT NULL'))
				]),
			'primaryKey': 'ClassName,WeaponType',
			'foreignKey': {
				'ClassName': ('FE14_Classes',  'ClassName'),
				'WeaponType': ('FE14_WeaponTypes',  'WeaponType')
			}
		},
		'triggers': []
	},
	{
		'tableName': 'FE14_CharacterStats',
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
				'CharId': ('FE14_Characters',  'CharId')
			}
		},
		'triggers': [
			'''CREATE TRIGGER FE14_CharacterStats_NoChildren
				BEFORE INSERT ON FE14_CharacterStats FOR EACH ROW
				IF (SELECT EXISTS(SELECT * FROM FE14_Characters C WHERE C.isChild AND C.CharId = NEW.CharId))
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'FE14_CharacterStats can only hold non-child characters.';
				END IF;''',
		]
	},
	{
		'tableName': 'FE14_ChildrenStats',
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
				'CharId': ('FE14_Characters',  'CharId')
			}
		},
		'triggers': [
			'''CREATE TRIGGER FE14_ChildrenStats_OnlyChildren
				BEFORE INSERT ON FE14_ChildrenStats FOR EACH ROW
				IF (SELECT NOT EXISTS(SELECT * FROM FE14_Characters C WHERE C.isChild AND C.CharId = NEW.CharId))
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'FE14_ChildrenStats can only hold child characters.';
				END IF;''',
		]
	},
	{
		'tableName': 'FE14_CharacterBaseStats',
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
				'CharId': ('FE14_Characters',  'CharId'),
				'Class': ('FE14_Classes',  'ClassName')
			}
		},
		'triggers': [
			'''CREATE TRIGGER FE14_CharacterBaseStats_NoChildren
				BEFORE INSERT ON FE14_CharacterBaseStats FOR EACH ROW
				IF (SELECT EXISTS(SELECT * FROM FE14_Characters C WHERE C.isChild AND C.CharId = NEW.CharId))
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'FE14_CharacterBaseStats can only hold non-child characters.';
				END IF;''',
		]
	},
	{
		'tableName': 'FE14_ChildrenBaseStats',
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
				'CharId': ('FE14_Characters',  'CharId'),
				'Class': ('FE14_Classes',  'ClassName')
			}
		},
		'triggers': [
			'''CREATE TRIGGER FE14_ChildrenBaseStats_OnlyChildren
				BEFORE INSERT ON FE14_ChildrenBaseStats FOR EACH ROW
				IF (SELECT NOT EXISTS(SELECT * FROM FE14_Characters C WHERE C.isChild AND C.CharId = NEW.CharId))
				THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'FE14_ChildrenBaseStats can only hold child characters.';
				END IF;''',
		]
	},
]
SQL_FILES_HEROES = [
	{
		'tableName': 'Heroes_Votes',
		'sourceFile': os.path.join('Heroes', 'HeroesVotes.csv'),
		'schema': {
			'types': OrderedDict([
				('Ranking', (INT_T, 'NOT NULL') ),
				('CharId', (STRING_T, 'NOT NULL') ),
				('Game', (STRING_T, 'NOT NULL') ),
				('Votes', (INT_T, 'NOT NULL') ),
				]),
			'primaryKey': 'CharId,Game',
			'foreignKey': {}
		},
		'triggers': []
	},
	{
		'tableName': 'Heroes_Gender',
		'sourceFile': os.path.join('Heroes', 'HeroesGender.csv'),
		'schema': {
			'types': OrderedDict([
				('CharId', (STRING_T, 'NOT NULL') ),
				('Game', (STRING_T, 'NOT NULL') ),
				('isMale', (BOOLEAN_T, 'NOT NULL') ),
				('isFemale', (BOOLEAN_T, 'NOT NULL') ),
				]),
			'primaryKey': 'CharId,Game',
			'foreignKey': {
				'CharId,Game': ('Heroes_Votes', 'CharId,Game')
			}
		},
		'triggers': []
	},
]

SQL_FILES = SQL_FILES_HEROES

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
	print(repr(e))
	print(e)
	print(type(e))
finally:
	if con:
		try:
			con.commit()
		except Exception as e:
			print(e)
			pass
		con.close()

print('finished')