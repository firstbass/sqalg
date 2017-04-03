#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from queries import *
#Returns the inverse operation for a given comparison operation
#Preconditions: Input is an operation string
#Postconditions: the inverse of the input operation string is returned
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

#Transforms a from list into relational algebra
#Preconditions: Input is a the operands to a from list
#Postconditions: Output is a general relational algebra statement
def from_list_to_relalg(from_list):
  #print(28);
  from_arr = from_list.split(',') #separate the input from list by commas
  #print(from_arr);
  #print(from_arr);
  from_list = ''; #NO LONGER NECESSARY
  #go through the different entries in the comma separated list (CSL) and sanitize the RENAMEALL flag into RENAME.
  for i in range(len(from_arr)):
    #print(33);
    if '{' in from_arr[i]: #Due to how we have documented the code, 
      #print(35);
      #print(from_arr[i]);
      #find if RENAMEALL is within the entry we are looking at
      match = re.search('RENAMEALL\_\{[\w\d]+\}\([\w\d]+\)', from_arr[i]);
      #print(match);
      #print(37);
      #find the new name of the table
      rename = from_arr[i][from_arr[i].index('{')+1:from_arr[i].index('}')];
      #find the original name of the table
      table_name = from_arr[i][from_arr[i].index('(')+1:from_arr[i].index(')')]
      #print(rename, table_name);
      #if the original name of the table is the same as  the renamed value, then put the original table value down. 
      if (table_name == rename):
        from_arr[i] = re.sub('RENAMEALL_\{[\w\d]+\}\([\w\d]+\)', table_name, from_arr[i], count = 1)
      #otherwise, denote that the table is renamed.
      else:
        from_arr[i] = re.sub('RENAMEALL_\{[\w\d]+\}\([\w\d]+\)', table_name + ' ' + rename, from_arr[i], count = 1)


  #go through the entries in the from list and denote which ones need to be renamed
  for i in range(len(from_arr)):
    from_arr[i].strip();
    word_arr = re.findall('\w+', from_arr[i]);
    #print(45,word_arr);
    #if there is more than word in this entry, then there must be a renamed value. luckily, the original
    #table name is always the first entry, and the renamed value is always the last entry.
    if len(word_arr) > 1:
      from_arr[i] = 'RENAME_{' + word_arr[-1] + '}(' + word_arr[0] + ')'; 
    else:
      from_arr[i] = word_arr[0];

  #format the cross product
  cross_text = '';
  for i in range(len(from_arr)):
    if i != len(from_arr)-1:
      cross_text += 'CROSS(' + from_arr[i] + ',';
    else:
      cross_text += from_arr[i] + (')' * (i));
  return cross_text;


#Puts a subquery-free query into proper relational algebra
#Preconditions: select_list,from_list,where_list are the entries in a select, where, and from statement, respectively
#Postconditions: the lists as translated into relational algebra is returned.
def relalg(select_list, from_list, where_list):
  return 'PROJECT_{' + select_list + '}(' + 'SELECT_{' + where_list + '}(' + from_list_to_relalg(from_list) + '))';

#print(15);
#print(relalg('*', 'SAILORS AS S', 'S.RATING=5'));
#print(17);

#Split a query into its select, from, and where statements
#Preconditions: Input query is a valid SQL input.
#Postconditions: the split query is returned, the contents of the select_list, from_list, 
#and where_list are returned, and the from_list in relational algebra is returned.
def select_from_where_nosubquery(query):
  query = re.sub('[\n\s]+',' ', query);
  SELECT_FROM_WHERE = '(SELECT|FROM|WHERE)'# ([\W\w]+) FROM ([\W\w]+) WHERE ([\W\w]+)';
  arr = re.split(SELECT_FROM_WHERE, query);


  select_list = arr[arr.index('SELECT') + 1];
  from_list = arr[arr.index('FROM') + 1];
  where_list = arr[arr.index('WHERE') + 1];

  cross_text = from_list_to_relalg(from_list);
  
  #print(cross_text);

  #return 'PROJECT_{' + select_list + '}(SELECT_{' + where_list + '}(' + cross_text + '))';
  return (arr, select_list, where_list, from_list, cross_text);
#print(select_from_where_nosubquery(q1));
def find_parentheses(s):
    """ Find and return the location of the matching parentheses pairs in s.

    Given a string, s, return a dictionary of start: end pairs giving the
    indexes of the matching parentheses in s. Suitable exceptions are
    raised if s contains unbalanced parentheses.

    """

    # The indexes of the open parentheses are stored in a stack, implemented
    # as a list

    stack = []
    parentheses_locs = {}
    for i, c in enumerate(s):
        if c == '(':
            stack.append(i)
        elif c == ')':
            try:
                parentheses_locs[stack.pop()] = i
            except IndexError:
                raise IndexError('Too many close parentheses at index {}'
                                                                .format(i))
    if stack:
        raise IndexError('No matching close parenthesis to open parenthesis '
                         'at index {}'.format(stack.pop()))
    return parentheses_locs


def normalize_with_ands(query):
  (oarr, oselect, owhere, ofrom, ocross) = select_from_where_nosubquery(query);
  
  new_where = '';
  new_str = ' '.join(oarr[oarr.index('WHERE')+1:])
  new_str = re.sub('[\n\s]+',' ', new_str)

  parens = find_parentheses(new_str)
  
  ands = re.finditer('\s+AND\s+', new_str)
  actual_ands = [];
  sub_wheres = [];
  for a in ands:
      a_index = a.start();
      is_separator = True
      for op in parens:
          cp = parens[op];
          if a_index > op and a_index < cp:
              is_separator = False;
      if is_separator:
          actual_ands += [a];
  if len(actual_ands) == 0:
      ##print(162);
      return normalize_without_ands(query);
  else:
      for ai in range(len(actual_ands)):
          #print(ai);
          
          if ai == len(actual_ands) - 1:
             sub_wheres += [new_str[actual_ands[ai].end():]];
          if ai == 0:
              sub_wheres += [new_str[:actual_ands[ai].start()]]
          else:
              sub_wheres += [new_str[actual_ands[ai-1].end():actual_ands[ai].start()]]
  
      for where in sub_wheres:
            subwheretext = 'SELECT'  + oselect + ' FROM ' + ofrom + ' WHERE ' + where;
            normalized_subpart = normalize_with_ands(subwheretext);
            if new_where == '':
                new_where = normalized_subpart[normalized_subpart.index('WHERE')+len('WHERE'):]
            else:
                new_where += ' AND ' +normalized_subpart[normalized_subpart.index('WHERE')+len('WHERE'):]
  return 'SELECT ' + oselect + ' FROM ' + ofrom + ' WHERE ' + new_where;

  #print(query_text);
  #return query_text;
  #should we return query_text?




#Normalize subqueries to be in EXISTS or NOT EXISTS form
#Preconditions: Query is proper SQL
#Postconditions: Returns subqueries in the query in the proper form

###############################################
#CURRENTLY DOES NOT RETURN A VALUE
###############################################
def normalize_without_ands(query):
  (oarr, oselect, owhere, ofrom, ocross) = select_from_where_nosubquery(query);
  subquery_text='';
  #print(oselect, owhere, ofrom, ocross)
  #make sure we are working from the query above the outermost query, and solve inward-out
  if hasSubquery(query):
    nextsub = getNextSubQuery(query)
    nextsub = normalize_with_ands(nextsub);
    (iarr, iselect, iwhere, ifrom,icross) = select_from_where_nosubquery(nextsub);
    #print( iselect, iwhere, ifrom);
    #phrase_before_in, iselect, iwhere
    if (iwhere != ''):
      iwhere=iwhere[:-1];
      iwhere += ' AND ';
    #print(owhere);

    # Accept Not IN
    phrase_before_not_in = '([\d\.\w]+)\s+NOT IN';
    pb4ni = re.search(phrase_before_not_in, owhere);
    if pb4ni: #adjust query to be in NOT EXISTS form
      #print('found NOT IN');
      iwhere += iselect + ' = ' + owhere[pb4ni.start():pb4ni.end()-len('NOT IN')];#add the condition to inner where
      #print(iwhere);
      owhere = re.sub(phrase_before_not_in, 'NOT EXISTS', owhere); # replaces NOT IN with NOT exists
      #print(owhere);

    #accept in
    phrase_before_in = '([\d\.\w]+)\s+IN';
    pb4i = re.search(phrase_before_in, owhere);
    if pb4i: #adjust query to be in EXISTS form
      #print('found IN');
      iwhere += iselect + ' = ' + owhere[pb4i.start():pb4i.end()-3]; #add the condition to  inner where
      #print(iwhere);
      owhere = re.sub(phrase_before_in, 'EXISTS', owhere); #replace the IN statement with EXISTS 
      #print(owhere);

    #accept ALL
    owhere_arr = re.split('\s+', owhere);
    #print(owhere_arr);
    #may need to do this in REGEX to avoid issues
    if (owhere_arr.count('ALL') != 0):
      all_index = owhere_arr.index('ALL');
      if (all_index != -1): #found ALL
        #print('found ALL');
        #print(owhere_arr.index('ALL'));
        op_index = all_index - 1;
        pb4all = owhere_arr[op_index-1];
        iwhere += pb4all + comp_op(owhere_arr[op_index]) + iselect; #invert the logic and add it to inner where
        #print(iwhere);
        owhere = re.sub('([\d\.\w]+)\s+[><=]+\s+ALL','NOT EXISTS', owhere) #change statement to NOT EXISTS
        #print(owhere);

    #accept ANY
    owhere_arr = re.split('\s+', owhere);
    #print(owhere_arr);
    #may need to do this with REGEX to avoid issues
    if (owhere_arr.count('ANY') > 0):
      any_index = owhere_arr.index('ANY');
      #print(any_index);
      if (any_index != -1): #found ANY
        #print('found ANY');
        #print(owhere_arr.index('ANY'));
        op_index = any_index - 1; #figure out where operator is
        pb4any = owhere_arr[op_index-1];
        iwhere += pb4any + owhere_arr[op_index] + iselect; #add statement to inner where
        #print(iwhere);
        owhere = re.sub('(\w+)\s+[><=]+\s+ANY','EXISTS', owhere) #change statement to EXISTS
        #print(owhere);

    #accept comparison operator
    owhere_arr = re.split('\s+', owhere);
    #print(owhere_arr);
    op = '';
    for entry in owhere_arr:
      op_match = re.match('[><=]+', entry);
      if op_match: #operator has been found
        op = entry;
        break;
    if (op != ''):
        #print('found operator');
        op_index = owhere_arr.index(op);
        pb4op = owhere_arr[op_index - 1];
        iwhere += pb4op + op + iselect;#insert conidition with operator into inner select
        #print(iwhere);
        owhere = re.sub('([\d\.\w]+)\s+[><=]+','EXISTS', owhere) #change statement to EXISTS
        #print(owhere);

    subquery_text = 'SELECT ' + iselect + ' FROM ' + ifrom + ' WHERE ' + iwhere;
  query_text = 'SELECT'  + oselect + ' FROM ' + ofrom + ' WHERE ' + owhere;
  if subquery_text != '':
    query_text += subquery_text + ')';

    #print(query_text);
  return query_text;
    #should we return query_text?

#Get a list of what all functions were renamed, for context relations
#Preconditions: from_list is a proper from_list, Q_arr is a query
#Postconditions: a map of renamed tables to their original names is returned
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


def fix_all_correlated_subquery(query, schema, parent_rename_map = { }):
  keywords = ['ABSOLUTE','EXEC','OVERLAPS','ACTION','EXECUTE','PAD','ADA','EXISTS','PARTIAL','ADD','EXTERNAL','PASCAL','ALL','EXTRACT','POSITION','ALLOCATE','FALSE','PRECISION','ALTER','FETCH','PREPARE','AND','FIRST','PRESERVE','ANY','FLOAT','PRIMARY','ARE','FOR','PRIOR','AS','FOREIGN','PRIVILEGES','ASC','FORTRAN','PROCEDURE','ASSERTION','FOUND','PUBLIC','AT','FROM','READ','AUTHORIZATION','FULL','REAL','AVG','GET','REFERENCES','BEGIN','GLOBAL','RELATIVE','BETWEEN','GO','RESTRICT','BIT','GOTO','REVOKE','BIT_LENGTH','GRANT','RIGHT','BOTH','GROUP','ROLLBACK','BY','HAVING','ROWS','CASCADE','HOUR','SCHEMA','CASCADED','IDENTITY','SCROLL','CASE','IMMEDIATE','SECOND','CAST','IN','SECTION','CATALOG','INCLUDE','SELECT','CHAR','INDEX','SESSION','CHAR_LENGTH','INDICATOR','SESSION_USER','CHARACTER','INITIALLY','SET','CHARACTER_LENGTH','INNER','SIZE','CHECK','INPUT','SMALLINT','CLOSE','INSENSITIVE','SOME','COALESCE','INSERT','SPACE','COLLATE','INT','SQL','COLLATION','INTEGER','SQLCA','COLUMN','INTERSECT','SQLCODE','COMMIT','INTERVAL','SQLERROR','CONNECT','INTO','SQLSTATE','CONNECTION','IS','SQLWARNING','CONSTRAINT','ISOLATION','SUBSTRING','CONSTRAINTS','JOIN','SUM','CONTINUE','KEY','SYSTEM_USER','CONVERT','LANGUAGE','TABLE','CORRESPONDING','LAST','TEMPORARY','COUNT','LEADING','THEN','CREATE','LEFT','TIME','CROSS','LEVEL','TIMESTAMP','CURRENT','LIKE','TIMEZONE_HOUR','CURRENT_DATE','LOCAL','TIMEZONE_MINUTE','CURRENT_TIME','LOWER','TO','CURRENT_TIMESTAMP','MATCH','TRAILING','CURRENT_USER','MAX','TRANSACTION','CURSOR','MIN','TRANSLATE','DATE','MINUTE','TRANSLATION','DAY','MODULE','TRIM','DEALLOCATE','MONTH','TRUE','DEC','NAMES','UNION','DECIMAL','NATIONAL','UNIQUE','DECLARE','NATURAL','UNKNOWN','DEFAULT','NCHAR','UPDATE','DEFERRABLE','NEXT','UPPER','DEFERRED','NO','USAGE','DELETE','NONE','USER','DESC','NOT','USING','DESCRIBE','NULL','VALUE','DESCRIPTOR','NULLIF','VALUES','DIAGNOSTICS','NUMERIC','VARCHAR','DISCONNECT','OCTET_LENGTH','VARYING','DISTINCT','OF','VIEW','DOMAIN','ON','WHEN','DOUBLE','ONLY','WHENEVER','DROP','OPEN','WHERE','ELSE','OPTION','WITH','END','OR','WORK','END-EXEC','ORDER','WRITE','ESCAPE','OUTER','YEAR','EXCEPT','OUTPUT','ZONE','EXCEPTION']
  #Get to innermost subquery
  subquery = '';
  #print('175', query);
  #top-level query
  (oarr, oselect, owhere, ofrom, ocross) = select_from_where_nosubquery(query);
  (oarr, oselect, owhere, ofrom, ocross) = select_from_where_nosubquery(query);

  new_where = '';
  new_str = ' '.join(oarr[oarr.index('WHERE')+1:])
  new_str = re.sub('[\n\s]+',' ', new_str)

  parens = find_parentheses(new_str)

  ands = re.finditer('\s+AND\s+', new_str)
  actual_ands = [];
  sub_wheres = [];
  for a in ands:
    a_index = a.start();
    is_separator = True
    for op in parens:
        cp = parens[op];
        if a_index > op and a_index < cp:
            is_separator = False;
    if is_separator:
        actual_ands += [a];
  if len(actual_ands) == 0:
    print(162);
    return fix_correlated_subquery(query, schema);
  else:
    for ai in range(len(actual_ands)):
        print(ai);
        
        if ai == len(actual_ands) - 1:
            sub_wheres += [new_str[actual_ands[ai].end():]];
        if ai == 0:
            sub_wheres += [new_str[:actual_ands[ai].start()]]
        else:
            sub_wheres += [new_str[actual_ands[ai-1].end():actual_ands[ai].start()]]

    for where in sub_wheres:
        subwheretext = 'SELECT ' + oselect + ' FROM ' + ofrom + ' WHERE ' + where;
        fixed_part = fix_all_correlated_subquery(subwheretext, schema);
        if new_where == '':
            new_where = fixed_part[fixed_part.index('WHERE')+len('WHERE'):]
        else:
            new_where += ' AND ' + fixed_part[fixed_part.index('WHERE')+len('WHERE'):]
  print('new_where', new_where);
  return 'SELECT ' + oselect + ' FROM ' + ofrom + ' WHERE ' + new_where;

  
  '''
  if hasSubquery(query):
    subquery = getNextSubQuery(query);
    (iarr, iselect, iwhere, ifrom, icross) = select_from_where_nosubquery(subquery);
    #print(parent_rename_map);
    updated_rename_map = parent_rename_map.copy();
    rnm = getRenameMap(ofrom, oarr);
    updated_rename_map.update(rnm);#make sure we understand all currently available context relations
    #print(updated_rename_map, 183, query);
    #print('unfixed subquery: ' + subquery)
    subquery = fix_correlated_subquery(subquery, updated_rename_map); #send the list of context relations to the child
    #print('fixed subquery: ' + subquery)
    #in the where make sure everything belongs to the from
  wherarr=re.findall('[\w\d]*\.*[\w\d]+', owhere);
  
  rename_map = getRenameMap(ofrom, oarr);
  #print(wherarr);
  for entry in wherarr: #go through and  find context relation
    #print(wherarr);
    if entry != 'EXISTS': #EXISTS is definitely not a context relation
      #print('entry start');
      #print(entry);
      #stolen from validAttributes Function
      if re.match('[\w\d]+\.[\w\d]+', entry): #if there is a ., we have to check if the phrase before the . is in our rename table 
        #print(entry, parent_rename_map, rename_map);
        attr = entry[entry.index('.') + 1:] 
        table = entry[0:entry.index('.')]
        #print('a: ',attr, table, table in rename_map.keys() or table in parent_rename_map.keys())
        if not (table in rename_map.keys()):
          #ifrom = 'CROSS(RENAME_{' + table + '}(' + rename_map[table] + '),' + ifrom + ')';
          #print('do nothing');
        #else:
          ofrom = 'RENAMEALL_{' + table + '}(' + parent_rename_map[table] + '),' + ofrom; #label the query as RENAMEALL, to denote a context relation
          #print(subquery);
        
      else: #the query is simply a single word, we must check if the attribute works in the proper spot
        flag = False;
        #print(rename_map);
        for table in rename_map.values():
          if entry in schema[table].keys():
            #we got one that's good - the attribute is in a directly related table
            flag = True;
            break#RA

        if not flag: #it's not in immediately available tables - we know it's a context relation then
          for table in parent_rename_map.values():
            if entry in schema[table]:
              #found it
              ofrom = 'CROSS(RENAMEALL_{' + table + '}(' + parent_rename_map[table] + '),' + ofrom + ')';
      #print('entry end');
  query = 'SELECT ' + oselect + ' FROM ' + ofrom + ' WHERE ' + owhere + subquery;
  if subquery != '':
      query += ')';
  print(419,query);
  return query;
#NOT FINISHED, NAIVE AND DOES NOT APPLY ANY LOGICAL CORRECTIONS
'''


#Fix context relations in correlated subqueries
#Preconditions: Query is a valid SQL query, Parent_rename_map is the table of all renamed values
#Postconditions: the query with solved context relations is returned
def fix_correlated_subquery(query, schema, parent_rename_map = { }):
  keywords = ['ABSOLUTE','EXEC','OVERLAPS','ACTION','EXECUTE','PAD','ADA','EXISTS','PARTIAL','ADD','EXTERNAL','PASCAL','ALL','EXTRACT','POSITION','ALLOCATE','FALSE','PRECISION','ALTER','FETCH','PREPARE','AND','FIRST','PRESERVE','ANY','FLOAT','PRIMARY','ARE','FOR','PRIOR','AS','FOREIGN','PRIVILEGES','ASC','FORTRAN','PROCEDURE','ASSERTION','FOUND','PUBLIC','AT','FROM','READ','AUTHORIZATION','FULL','REAL','AVG','GET','REFERENCES','BEGIN','GLOBAL','RELATIVE','BETWEEN','GO','RESTRICT','BIT','GOTO','REVOKE','BIT_LENGTH','GRANT','RIGHT','BOTH','GROUP','ROLLBACK','BY','HAVING','ROWS','CASCADE','HOUR','SCHEMA','CASCADED','IDENTITY','SCROLL','CASE','IMMEDIATE','SECOND','CAST','IN','SECTION','CATALOG','INCLUDE','SELECT','CHAR','INDEX','SESSION','CHAR_LENGTH','INDICATOR','SESSION_USER','CHARACTER','INITIALLY','SET','CHARACTER_LENGTH','INNER','SIZE','CHECK','INPUT','SMALLINT','CLOSE','INSENSITIVE','SOME','COALESCE','INSERT','SPACE','COLLATE','INT','SQL','COLLATION','INTEGER','SQLCA','COLUMN','INTERSECT','SQLCODE','COMMIT','INTERVAL','SQLERROR','CONNECT','INTO','SQLSTATE','CONNECTION','IS','SQLWARNING','CONSTRAINT','ISOLATION','SUBSTRING','CONSTRAINTS','JOIN','SUM','CONTINUE','KEY','SYSTEM_USER','CONVERT','LANGUAGE','TABLE','CORRESPONDING','LAST','TEMPORARY','COUNT','LEADING','THEN','CREATE','LEFT','TIME','CROSS','LEVEL','TIMESTAMP','CURRENT','LIKE','TIMEZONE_HOUR','CURRENT_DATE','LOCAL','TIMEZONE_MINUTE','CURRENT_TIME','LOWER','TO','CURRENT_TIMESTAMP','MATCH','TRAILING','CURRENT_USER','MAX','TRANSACTION','CURSOR','MIN','TRANSLATE','DATE','MINUTE','TRANSLATION','DAY','MODULE','TRIM','DEALLOCATE','MONTH','TRUE','DEC','NAMES','UNION','DECIMAL','NATIONAL','UNIQUE','DECLARE','NATURAL','UNKNOWN','DEFAULT','NCHAR','UPDATE','DEFERRABLE','NEXT','UPPER','DEFERRED','NO','USAGE','DELETE','NONE','USER','DESC','NOT','USING','DESCRIBE','NULL','VALUE','DESCRIPTOR','NULLIF','VALUES','DIAGNOSTICS','NUMERIC','VARCHAR','DISCONNECT','OCTET_LENGTH','VARYING','DISTINCT','OF','VIEW','DOMAIN','ON','WHEN','DOUBLE','ONLY','WHENEVER','DROP','OPEN','WHERE','ELSE','OPTION','WITH','END','OR','WORK','END-EXEC','ORDER','WRITE','ESCAPE','OUTER','YEAR','EXCEPT','OUTPUT','ZONE','EXCEPTION']
  #Get to innermost subquery
  subquery = '';
  #print('175', query);
  (oarr, oselect, owhere, ofrom, ocross) = select_from_where_nosubquery(query);
  if hasSubquery(query):
    subquery = getNextSubQuery(query);
    (iarr, iselect, iwhere, ifrom, icross) = select_from_where_nosubquery(subquery);
    print(430,parent_rename_map);
    updated_rename_map = parent_rename_map.copy();
    rnm = getRenameMap(ofrom, oarr);
    updated_rename_map.update(rnm);#make sure we understand all currently available context relations
    #print(updated_rename_map, 183, query);
    #print('unfixed subquery: ' + subquery)
    subquery = fix_correlated_subquery(subquery, schema, updated_rename_map); #send the list of context relations to the child
    #print('fixed subquery: ' + subquery)
    #in the where make sure everything belongs to the from
  wherarr=re.findall('[\w\d]*\.*[\w\d]+', owhere);

  rename_map = getRenameMap(ofrom, oarr);
  print(442, rename_map);
  #print(wherarr);
  for entry in wherarr: #go through and  find context relation
    #print(wherarr);
    if entry != 'EXISTS': #EXISTS is definitely not a context relation
      #print('entry start');
      #print(entry);
      #stolen from validAttributes Function
      if re.match('[\w\d]+\.[\w\d]+', entry): #if there is a ., we have to check if the phrase before the . is in our rename table 
        #print(entry, parent_rename_map, rename_map);
        attr = entry[entry.index('.') + 1:] 
        table = entry[0:entry.index('.')]
        #print('a: ',attr, table, table in rename_map.keys() or table in parent_rename_map.keys())
        if not (table in rename_map.keys()):
          #ifrom = 'CROSS(RENAME_{' + table + '}(' + rename_map[table] + '),' + ifrom + ')';
          #print('do nothing');
        #else:
          print(458, parent_rename_map);
          print(460, table);
          ofrom = 'RENAMEALL_{' + table + '}(' + parent_rename_map[table] + '),' + ofrom; #label the query as RENAMEALL, to denote a context relation
          #print(subquery);
        
      else: #the query is simply a single word, we must check if the attribute works in the proper spot
        flag = False;
        #print(rename_map);
        for table in rename_map.values():
          if entry in schema[table].keys():
            #we got one that's good - the attribute is in a directly related table
            flag = True;
            break#RA

        if not flag: #it's not in immediately available tables - we know it's a context relation then
          for table in parent_rename_map.values():
            if entry in schema[table]:
              #found it
              ofrom = 'CROSS(RENAMEALL_{' + table + '}(' + parent_rename_map[table] + '),' + ofrom + ')';
      #print('entry end');
  query = 'SELECT ' + oselect + ' FROM ' + ofrom + ' WHERE ' + owhere + subquery;
  if subquery != '':
      query += ')';
  print(419,query);
  return query;
#NOT FINISHED, NAIVE AND DOES NOT APPLY ANY LOGICAL CORRECTIONS

def decorrelate_disconjuctive(query):
  ORcond = [];
  ANDcond = '';
  query=re.sub(';','',query);
  (oarr, oselect, owhere, ofrom,ocross) = select_from_where_nosubquery(query);
  conditions = re.split('[\s]+(AND|OR)[\s]+', owhere);
  for entry in range(len(conditions)):
    if(entry==0):
      ANDcond += conditions[entry];
    elif(conditions[entry]=='OR'):
      ORcond.append(conditions[entry+1]);
      entry += 1;
    elif(conditions[entry]=='AND'):
      ANDcond += ' AND ' + conditions[entry+1];
      entry += 1;
  #  ORcond = re.split('[\s]+OR[\s]+',conditions[entry]);
  ##print('ORcond: ', ORcond, 'ANDwOR: ', conditions);
  query='SELECT ' + oselect + ' FROM ' + ofrom + ' WHERE ' + ANDcond;
  ##print(query)
  for entry in range(len(ORcond)):
    query += '\n UNION ' + ' SELECT ' + oselect + ' FROM ' + ofrom + ' WHERE ' + ORcond[entry];
  query +=';';
  ##print(query);
  return query;
#Transform a conjunctive query to relational algebra
#Precondition: Query already has context relations take into account
#Postcondition: query in its relational algebra form
def decorrelate_conjunctive(query,schema):
  # already added context relations to the from list
  subquery = '';
  subquery_free_part = '';
  exists = [];
  notexists = [];

  to_union = [];
  rel_alg = '';
  #print(query);
  #print('175', query);
  (oarr, oselect, owhere, ofrom,ocross) = select_from_where_nosubquery(query);
  #
  #print(237,ofrom);
  if hasSubquery(query): #make sure we're working from innermost query
    subquery = getNextSubQuery(query);
    (iarr, iselect, iwhere, ifrom, icross) = select_from_where_nosubquery(subquery);

  owhere_arr = re.split('[\s]+AND[\s]+', owhere);
  #print(owhere_arr)
  for entry in owhere_arr: # go through and decorrelate each EXISTS/NOT EXISTS query
    if 'EXISTS' not in entry:
      #print('subquery free part is', entry);
      if subquery_free_part == '':
        subquery_free_part = entry #no need to add more tables to from list
      else:
        subquery_free_part += ' AND ' + entry;
    elif 'NOT EXISTS' in entry:
      #print 'exists found';
      #print('subquery: ', subquery);
      #print(ifrom);

      context_relations = re.findall('RENAMEALL_\{[\w\d]+\}\([\w\d]+\)', ifrom);
      attrs = '';
      for rel in context_relations:
        table_name = rel[rel.index('(')+1:rel.index(')')];
        rename = rel[rel.index('{') + 1:rel.index('}')];
        attrs += getParameters(schema, table_name, rename)
        #anti join
        natty_join = 'MINUS(' + from_list_to_relalg(ofrom) + ',NATURALJOIN(' + from_list_to_relalg(ofrom) + ',' + 'PROJECT_{' + str(attrs) + '}(SELECT_{' + iwhere + '}('  + from_list_to_relalg(ifrom) + '))';
        #print(rel_alg);
        notexists += [natty_join];

    elif 'EXISTS' in entry:
      #print 'exists found';
      #print('subquery: ', subquery);
      #print(ifrom);

      context_relations = re.findall('RENAMEALL_\{[\w\d]+\}\([\w\d]+\)', ifrom);
      attrs = '';
      for rel in context_relations:
        table_name = rel[rel.index('(')+1:rel.index(')')];
        rename = rel[rel.index('{') + 1:rel.index('}')];
        attrs += getParameters(schema, table_name, rename)

        print(568,from_list_to_relalg(ofrom))
        print(569,from_list_to_relalg(ifrom))
        natty_join = 'NATURALJOIN(' + from_list_to_relalg(ofrom) + ',' + 'PROJECT_{' + str(attrs) + '}(SELECT_{' + iwhere + '}('  + from_list_to_relalg(ifrom) + ')))';
        exists += [natty_join];
    

  for join in (exists + notexists):
    to_union += ['PROJECT_{' + oselect + '}(' + 'SELECT_{' + subquery_free_part + '}(' + join + '))'];

  if len(to_union) == 0:
    return relalg(oselect, ofrom, owhere);
    return to_union[0];
  else:
    rel_alg = to_union[0];
    for i in range(1, len(to_union)):
      rel_alg = 'UNION(' + to_union[i] + ',' + rel_alg + ')';
    return rel_alg;
        #print(rel_alg);
                      #(ofrom list) natural join proj')ect(context_relations on inner query)select(where_list)(on (cross product of inner-from)
    # if the entry does not contain EXISTS or NOT EXISTS
    #remove select list from subquery
  #translate the subquery free part
  #translate the exists
  #translate the not exists
  #apply the projection of the sle
  #'\w+[\w\d]*'


  ###print('subquery: ', subquery);
  ###print('subquery_free_part: ', subquery_free_part);
  ###print('relalg:', rel_alg); 
  #return rel_alg;
q3 =''' SELECT    SNAME
FROM       SAILORS 
WHERE    SAILORS.SID NOT IN (SELECT  RESERVES.SID
                          FROM     RESERVES 
                          WHERE RESERVES.SID=10) OR
         SAILORS.SID IN (SELECT RESRVES.SID
                         FROM RESERVES
                         WHERE RESERVES.SID<>10 AND RESERVES.BID=5);
'''


q4='''SELECT SNAME
FROM SAILORS, RESERVES
WHERE SAILORS.SID = 5 
      OR(RESERVES.SID = 10 AND RESERVES.BID=5)
      AND RESERVES.SID=SAILORS.SID;'''

q5 =''' SELECT    SNAME
FROM       SAILORS, BOATS
WHERE    SAILORS.SID NOT IN (SELECT  RESERVES.SID
                          FROM     RESERVES 
                          WHERE RESERVES.SID=10) AND BOATS.BID NOT IN (SELECT RESERVES.BID FROM RESERVES WHERE RESERVES.BID < 5)'''


q76 = '''SELECT SNAME FROM SAILORS, RESERVES 
         WHERE NOT EXISTS (SELECT RESERVES.SID FROM RESERVES WHERE SAILORS.SID=RESERVES.SID)'''

#test='';
#while(test!=)
#print '---------';
#decorrelate_disconjuctive(q3)
#normalize_without_ands(q4);
#print(fix_correlated_subquery(q2));
#print(decorrelate_conjunctive(fix_correlated_subquery(normalize_without_ands(q3))));
#print(normalize_without_ands(q3));
#RENAMEALL = A Table that needs all of its attributes to be projected
#print(fix_all_correlated_subquery(normalize_with_ands(q5)));
#print('--');
#print(decorrelate_conjunctive(fix_correlated_subquery(normalize_without_ands(q5))))