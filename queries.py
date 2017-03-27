#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

'''
    This file will give functions that allow for checking the ownership of
    attributes and tables, and rewriting SQL queries with proper relations
'''

def getSchema(s):
  schema = {};
  precedent = 'Schemas of the underlying relations;\n'
  #additionally precedent is 1)
  start = s.find(precedent) + len(precedent)
  
  succedent = '2)'
  end = s.find(succedent)

  s = s[start:end].strip();
  s = s.split('\n')

  for line in s:
    match = re.search('\w\.\s*',line)
    line = line[match.end():]
    line = re.sub('(\w*)','schema[\'\\1\']=', line, count=1);
    line = line.replace('(', '{');
    line = line.replace(')', '}')

    line = re.sub('(\w*):(\w*)', '\'\\1\':\'\\2\'',line);
    
    exec(line);
  return schema;

schema = getSchema('''Test Data:  
1)  Schemas of the underlying relations;
a.  Sailors(sid:integer, sname:string, rating:integer, age:real)
b.  Boats(bid:integer, bname:string, color:string)
c.  Reserves(sid:integer, bid:integer, day:date) 

2)  SQL queries
a.  SELECT      S.sname
FROM        Sailors AS S,  Reserves AS R
WHERE     S.sid=R.sid AND R.bid=103

b.  SELECT      S.sname
FROM        Sailors AS S,  Reserves AS R, Boats AS B
WHERE     S.sid=R.sid AND R.bid=B.bid AND B.color=’red’
''')

def validAttribute(schema, table, attr):
  return attr in schema[table];

def fixQuery(query, schema):
  

  query = re.sub('\s+', ' ', query).upper();
  print(query);
  keywords = ['=','<>','+','*','/','ABSOLUTE','EXEC','OVERLAPS','ACTION','EXECUTE','PAD','ADA','EXISTS','PARTIAL','ADD','EXTERNAL','PASCAL','ALL','EXTRACT','POSITION','ALLOCATE','FALSE','PRECISION','ALTER','FETCH','PREPARE','AND','FIRST','PRESERVE','ANY','FLOAT','PRIMARY','ARE','FOR','PRIOR','AS','FOREIGN','PRIVILEGES','ASC','FORTRAN','PROCEDURE','ASSERTION','FOUND','PUBLIC','AT','FROM','READ','AUTHORIZATION','FULL','REAL','AVG','GET','REFERENCES','BEGIN','GLOBAL','RELATIVE','BETWEEN','GO','RESTRICT','BIT','GOTO','REVOKE','BIT_LENGTH','GRANT','RIGHT','BOTH','GROUP','ROLLBACK','BY','HAVING','ROWS','CASCADE','HOUR','SCHEMA','CASCADED','IDENTITY','SCROLL','CASE','IMMEDIATE','SECOND','CAST','IN','SECTION','CATALOG','INCLUDE','SELECT','CHAR','INDEX','SESSION','CHAR_LENGTH','INDICATOR','SESSION_USER','CHARACTER','INITIALLY','SET','CHARACTER_LENGTH','INNER','SIZE','CHECK','INPUT','SMALLINT','CLOSE','INSENSITIVE','SOME','COALESCE','INSERT','SPACE','COLLATE','INT','SQL','COLLATION','INTEGER','SQLCA','COLUMN','INTERSECT','SQLCODE','COMMIT','INTERVAL','SQLERROR','CONNECT','INTO','SQLSTATE','CONNECTION','IS','SQLWARNING','CONSTRAINT','ISOLATION','SUBSTRING','CONSTRAINTS','JOIN','SUM','CONTINUE','KEY','SYSTEM_USER','CONVERT','LANGUAGE','TABLE','CORRESPONDING','LAST','TEMPORARY','COUNT','LEADING','THEN','CREATE','LEFT','TIME','CROSS','LEVEL','TIMESTAMP','CURRENT','LIKE','TIMEZONE_HOUR','CURRENT_DATE','LOCAL','TIMEZONE_MINUTE','CURRENT_TIME','LOWER','TO','CURRENT_TIMESTAMP','MATCH','TRAILING','CURRENT_USER','MAX','TRANSACTION','CURSOR','MIN','TRANSLATE','DATE','MINUTE','TRANSLATION','DAY','MODULE','TRIM','DEALLOCATE','MONTH','TRUE','DEC','NAMES','UNION','DECIMAL','NATIONAL','UNIQUE','DECLARE','NATURAL','UNKNOWN','DEFAULT','NCHAR','UPDATE','DEFERRABLE','NEXT','UPPER','DEFERRED','NO','USAGE','DELETE','NONE','USER','DESC','NOT','USING','DESCRIBE','NULL','VALUE','DESCRIPTOR','NULLIF','VALUES','DIAGNOSTICS','NUMERIC','VARCHAR','DISCONNECT','OCTET_LENGTH','VARYING','DISTINCT','OF','VIEW','DOMAIN','ON','WHEN','DOUBLE','ONLY','WHENEVER','DROP','OPEN','WHERE','ELSE','OPTION','WITH','END','OR','WORK','END-EXEC','ORDER','WRITE','ESCAPE','OUTER','YEAR','EXCEPT','OUTPUT','ZONE','EXCEPTION']
  query_arr = query.split(' ');
  selects = [];
  for select in re.finditer('SELECT', query):
    selects += [select.start()];

  selects.reverse();
  for i in range(len(selects)):
    print(query[selects[i]:]);







  print(selects);



fixQuery('''
SELECT S.sname
FROM Sailors AS S
WHERE S.age > (SELECT MAX(S2.age)
               FROM Sailors S2
               WHERE S2.rating = 10
                 AND S.age > 5);
  ''', schema)