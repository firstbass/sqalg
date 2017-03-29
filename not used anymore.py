#!/usr/bin/env python
# -*- coding: utf-8 -*-



import re
import string
from queries import *

#q1 = 'SELECT * FROM SAILORS AS S, RESERVE AS R, DOGS D, OTHER WHERE X > 5'


def comp_op(op):
  if op == '<':
    return '>='
  elif op == '<=':
    return '>'
  elif op == '>':
    return '<='
  elif op == '>=':
    return '<'
  elif op == '=':
    return '<>'
  elif op == '<>':
    return '=';


def select_from_where_nosubquery(query):
  SELECT_FROM_WHERE = '(SELECT|FROM|WHERE)'# ([\W\w]+) FROM ([\W\w]+) WHERE ([\W\w]+)';
  arr = re.split(SELECT_FROM_WHERE, query);


  q1 = re.sub('[\n\s]+', ' ', query);

  select_list = arr[arr.index('SELECT') + 1];
  from_list = arr[arr.index('FROM') + 1];
  where_list = arr[arr.index('WHERE') + 1];

  from_arr = from_list.split(',')
  #print(from_arr);
  from_list = '';
  for i in range(len(from_arr)):
    from_arr[i].strip();
    word_arr = re.findall('\w+', from_arr[i]);
    if len(word_arr) > 1:
      from_arr[i] = 'RENAME_{' + word_arr[-1] + '}(' + word_arr[0] + ')';
    else:
      from_arr[i] = word_arr[0];

  cross_text = '';
  for i in range(len(from_arr)):
    if i != len(from_arr)-1:
      cross_text += 'CROSS(' + from_arr[i] + ',';
    else:
      cross_text += from_arr[i] + (')' * (i));

  #print(cross_text);

  #return 'PROJECT_{' + select_list + '}(SELECT_{' + where_list + '}(' + cross_text + '))';
  return (arr, select_list, where_list, cross_text);
#print(select_from_where_nosubquery(q1));

q2 = '''SELECT movieTitle FROM StarsIn
WHERE starName >= (SELECT name
FROM MovieStar
WHERE birthdate = 1960)'''

def normalize_without_ands(query):
  (oarr, oselect, owhere, ofrom) = select_from_where_nosubquery(query);
  print(oselect, owhere, ofrom)
  if hasSubquery(query):
    nextsub = getNextSubQuery(query)
    (iarr, iselect, iwhere, ifrom) = select_from_where_nosubquery(nextsub);
    print( iselect, iwhere, ifrom);
    #phrase_before_in, iselect, iwhere
    if (iwhere != ''):
      iwhere += ' AND ';
    print(owhere);

    # Accept Not IN
    phrase_before_not_in = '(\w+)\s+NOT IN';
    pb4ni = re.search(phrase_before_not_in, owhere);
    if pb4ni:
      print('found NOT IN');
      iwhere += iselect + ' = ' + owhere[pb4ni.start():pb4ni.end()-len('NOT IN')];
      print(iwhere);
      owhere = re.sub(phrase_before_not_in, 'NOT EXISTS', owhere);
      print(owhere);

    #accept in
    phrase_before_in = '(\w+)\s+IN';
    pb4i = re.search(phrase_before_in, owhere);
    if pb4i:
      print('found IN');
      iwhere += iselect + ' = ' + owhere[pb4i.start():pb4i.end()-3];
      print(iwhere);
      owhere = re.sub(phrase_before_in, 'EXISTS', owhere);
      print(owhere);


    #could be made in REGEX, but not now
    owhere_arr = re.split('\s+', owhere);
    print(owhere_arr);
    if (owhere_arr.count('ALL') != 0):
      all_index = owhere_arr.index('ALL');
      if (all_index != -1):
        print('found ALL');
        print(owhere_arr.index('ALL'));
        op_index = all_index - 1;
        pb4all = owhere_arr[op_index-1];
        iwhere += pb4all + comp_op(owhere_arr[op_index]) + iselect;
        print(iwhere);
        owhere = re.sub('(\w+)\s+[><=]+\s+ALL','NOT EXISTS', owhere)
        print(owhere);

    #could be made in REGEX, but not now
    owhere_arr = re.split('\s+', owhere);
    print(owhere_arr);
    if (owhere_arr.count('ANY') > 0):
      any_index = owhere_arr.index('ANY');
      print(any_index);
      if (any_index != -1):
        print('found ANY');
        print(owhere_arr.index('ANY'));
        op_index = any_index - 1;
        pb4any = owhere_arr[op_index-1];
        iwhere += pb4any + owhere_arr[op_index] + iselect;
        print(iwhere);
        owhere = re.sub('(\w+)\s+[><=]+\s+ANY','EXISTS', owhere)
        print(owhere);

    #could be made in REGEX, but not now
    owhere_arr = re.split('\s+', owhere);
    print(owhere_arr);
    op = '';
    for entry in owhere_arr:
      op_match = re.match('[><=]+', entry);
      if op_match:
        op = entry;
        break;
    if (op != ''):
        print('found operator');
        op_index = owhere_arr.index(op);
        pb4op = owhere_arr[op_index - 1];
        iwhere += pb4op + op + iselect;
        print(iwhere);
        owhere = re.sub('(\w+)\s+[><=]+','EXISTS', owhere)
        print(owhere);

    subquery_text = 'SELECT ' + iselect + ' FROM ' + ifrom + ' WHERE ' + iwhere;
    query_text = 'SELECT'  + oselect + ' FROM ' + ofrom + ' WHERE ' + owhere;

    query_text += subquery_text + ')';

    print(query_text);


def getRenameMap(from_list, q_arr):
  from_list = q_arr[q_arr.index('FROM') + 1];
  from_arr = from_list.split(',');
  from_list = '';
  rename_map = {};
  for i in range(len(from_arr)):
    from_arr[i].strip();
    word_arr = re.findall('\w+', from_arr[i]);
    from_arr[i] = word_arr[0];
    rename_map[word_arr[-1]] = word_arr[0];
  return rename_map;



def fix_correlated_subquery(query, parent_rename_map = { }):
  keywords = ['ABSOLUTE','EXEC','OVERLAPS','ACTION','EXECUTE','PAD','ADA','EXISTS','PARTIAL','ADD','EXTERNAL','PASCAL','ALL','EXTRACT','POSITION','ALLOCATE','FALSE','PRECISION','ALTER','FETCH','PREPARE','AND','FIRST','PRESERVE','ANY','FLOAT','PRIMARY','ARE','FOR','PRIOR','AS','FOREIGN','PRIVILEGES','ASC','FORTRAN','PROCEDURE','ASSERTION','FOUND','PUBLIC','AT','FROM','READ','AUTHORIZATION','FULL','REAL','AVG','GET','REFERENCES','BEGIN','GLOBAL','RELATIVE','BETWEEN','GO','RESTRICT','BIT','GOTO','REVOKE','BIT_LENGTH','GRANT','RIGHT','BOTH','GROUP','ROLLBACK','BY','HAVING','ROWS','CASCADE','HOUR','SCHEMA','CASCADED','IDENTITY','SCROLL','CASE','IMMEDIATE','SECOND','CAST','IN','SECTION','CATALOG','INCLUDE','SELECT','CHAR','INDEX','SESSION','CHAR_LENGTH','INDICATOR','SESSION_USER','CHARACTER','INITIALLY','SET','CHARACTER_LENGTH','INNER','SIZE','CHECK','INPUT','SMALLINT','CLOSE','INSENSITIVE','SOME','COALESCE','INSERT','SPACE','COLLATE','INT','SQL','COLLATION','INTEGER','SQLCA','COLUMN','INTERSECT','SQLCODE','COMMIT','INTERVAL','SQLERROR','CONNECT','INTO','SQLSTATE','CONNECTION','IS','SQLWARNING','CONSTRAINT','ISOLATION','SUBSTRING','CONSTRAINTS','JOIN','SUM','CONTINUE','KEY','SYSTEM_USER','CONVERT','LANGUAGE','TABLE','CORRESPONDING','LAST','TEMPORARY','COUNT','LEADING','THEN','CREATE','LEFT','TIME','CROSS','LEVEL','TIMESTAMP','CURRENT','LIKE','TIMEZONE_HOUR','CURRENT_DATE','LOCAL','TIMEZONE_MINUTE','CURRENT_TIME','LOWER','TO','CURRENT_TIMESTAMP','MATCH','TRAILING','CURRENT_USER','MAX','TRANSACTION','CURSOR','MIN','TRANSLATE','DATE','MINUTE','TRANSLATION','DAY','MODULE','TRIM','DEALLOCATE','MONTH','TRUE','DEC','NAMES','UNION','DECIMAL','NATIONAL','UNIQUE','DECLARE','NATURAL','UNKNOWN','DEFAULT','NCHAR','UPDATE','DEFERRABLE','NEXT','UPPER','DEFERRED','NO','USAGE','DELETE','NONE','USER','DESC','NOT','USING','DESCRIBE','NULL','VALUE','DESCRIPTOR','NULLIF','VALUES','DIAGNOSTICS','NUMERIC','VARCHAR','DISCONNECT','OCTET_LENGTH','VARYING','DISTINCT','OF','VIEW','DOMAIN','ON','WHEN','DOUBLE','ONLY','WHENEVER','DROP','OPEN','WHERE','ELSE','OPTION','WITH','END','OR','WORK','END-EXEC','ORDER','WRITE','ESCAPE','OUTER','YEAR','EXCEPT','OUTPUT','ZONE','EXCEPTION']
  #Get to innermost subquery
  print('175', query);
  if hasSubquery(query):
    subquery = getNextSubQuery(query);
    (oarr, oselect, owhere, ofrom) = select_from_where_nosubquery(query);
    (iarr, iselect, iwhere, ifrom) = select_from_where_nosubquery(subquery);
    #print(parent_rename_map);
    updated_rename_map = parent_rename_map.copy();

    rnm = getRenameMap(ofrom, oarr);
    updated_rename_map.update(rnm);
    #print(updated_rename_map, 183, query);
    print('unfixed subquery: ' + subquery)
    subquery = fix_correlated_subquery(subquery, updated_rename_map);
    print('fixed subquery: ' + subquery)
    #in the where make sure everything belongs to the from
    wherarr=re.findall('[\w\d]*\.*[\w\d]+', iwhere);
    
    rename_map = getRenameMap(ifrom, iarr);

    for entry in wherarr:
      #print('entry:' +entry);
      #stolen from validAttributes Function
      if re.match('[\w\d]+\.[\w\d]+', entry):
        #print('asdf');
        attr = entry[entry.index('.') + 1:]
        table = entry[0:entry.index('.')]
        #print('a: ',attr, table, table in rename_map.keys() or table in parent_rename_map.keys())
        if table in rename_map.keys():
          #ifrom = 'CROSS(RENAME_{' + table + '}(' + rename_map[table] + '),' + ifrom + ')';
          print('do nothing');
        else:
          ifrom = 'CROSS(RENAME_{' + table + '}(' + parent_rename_map[table] + '),' + ifrom + ')';
        #print(subquery);
        
      else:
        flag = False;
        for table in rename_map:
          if entry in schema[table]:
            #we got one that's good
            flag = True;
            break#RA

        if not flag:
          for table in parent_rename_map:
            if entry in schema[table]:
              #found it
              ifrom = 'CROSS(RENAME_{' + table + '}(' + parent_rename_map[table] + '),' + ifrom + ')';

    subquery = 'SELECT ' + iselect + ' FROM ' + ifrom + ' WHERE ' + iwhere;
    query = 'SELECT ' + oselect + ' FROM ' + ofrom + ' WHERE ' + owhere;
    print (query);
    #print(wherarr);
    #print('renameMap:');
    #print(rename_map);

  #'\w+[\w\d]*'
  return query;

fix_correlated_subquery(q2);