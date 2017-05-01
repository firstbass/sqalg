#!/usr/bin/env python
# -*- coding: utf-8 -*-
from functs import *
import re
from queries import *

################################################################################

def comp_op(op):
  ''' Returns the opposite operation given a comparison operation
  Preconditions:  input is an operation string (example: '>=')
  Postconditions: opposite operation string is returned '''

  switch_dict = {'<'  : '>=',
                 '>=' : '<' ,
                 '>'  : '<=',
                 '<=' : '>' ,
                 '='  : '<>',
                 '<>' : '=' ,
                };

  return switch_dict[op];

################################################################################

def from_list_to_relalg(from_list):
  ''' Transforms a from-list into a relational algebra
  Preconditions:  input is some sort of from-list from a query/modified-query
  Postconditions: returns general relational algebra crossing all tables '''

  # regular expression for RENAMEALL_{...}(...) with no captures
  RENAMEALL_REGEX = 'RENAMEALL\_\{[\w\d]+\}\([\w\d]+\)';

  # separate the from-list by commas
  from_arr = from_list.split(',');

  # clear the from-list
  from_list = '';

  # iterate through all comma separated values
  # and sanitize RENAMEALL into RENAME
  for i in range(len(from_arr)):

    # check for any instances of 'RENAME_{' or 'RENAMEALL_{'
    if '{' in from_arr[i]:
      
      # find if RENAMEALL_{..}(..) is in the current entry
      match = re.search(RENAMEALL_REGEX, from_arr[i]);
      
      # find the renamed name of the table
      open_curly = from_arr[i].index('{');
      close_curly = from_arr[i].index('}');
      rename = from_arr[i][open_curly + 1 : close_curly];
      
      # find the original name of the table
      open_paren = from_arr[i].index('(');
      close_paren = from_arr[i].index(')');
      table_name = from_arr[i][open_paren + 1 : close_paren];

      # replace 'RENAMEALL_{A}(A)' with 'A' initially
      replacement_string = table_name;
      if (table_name != rename):
        # replace 'RENAMEALL_{B}{A}' with 'A B'
        replacement_string += ' ' + rename;

      # execute replacement
      from_arr[i] = re.sub(RENAMEALL_REGEX, replacement_string, from_arr[i], count = 1)

  # iterate through all comma separated values
  # sanitize the table renames if invalid
  for i in range(len(from_arr)):

    # remove any whitespace at front/end of string
    from_arr[i].strip();
    
    # get all individual words and put them in an array
    word_arr = re.findall('[\w\d]+', from_arr[i]);
    print('__45',word_arr);
    
    # >1 word ==> must be a renamed value
    if len(word_arr) > 1:
      # 'A as B' or 'A B' ==> 'RENAME_{B}(A)' 
      from_arr[i] = 'RENAME_{' + word_arr[-1] + '}(' + word_arr[0] + ')'; 
    
    # <=1 word ==> only a singular table
    else:
      # 'A' ==> 'A'
      from_arr[i] = word_arr[0];

  # write the cross product text
  cross_text = '';

  # iterate through all sanitized values
  for i in range(len(from_arr)):

    # if not the last value
    if i != len(from_arr) - 1:

      # cross the table with the next value
      cross_text += 'CROSS(' + from_arr[i] + ',';
    
    # if last value
    else:

      # complete the final cross with the last table and correct # of parens
      cross_text += from_arr[i] + (')' * (i));

  # return the cross product text
  return cross_text;

################################################################################

def relalg(select_list, from_list, where_list):
  """ Puts a subquery-free query into proper relational algebra.
  Preconditions:  select_list, from_list, where_list are entries in a standard
                  select-from-where statement
  Postconditions: the lists translated into proper relational algebra """

  relalg_str =  'PROJECT_{' + select_list + '}(';
  relalg_str += 'SELECT_{'  + where_list  + '}(';
  relalg_str += from_list_to_relalg(from_list) + '))';

  return relalg_str;

################################################################################

def select_from_where_nosubquery(query):
  """ Split a query into its select, from, and where statements
  Preconditions:  Input query is a valid SQL input
  Postconditions: The split query is returned, the contents of the select_list,
                  from_list, and where_list are returned; and the from_list in
                  relational algebra is returned. """

  query = simplify_whitespace(query);

  # split at each query changing word [SELECT, ..., FROM, ...] 
  SELECT_FROM_WHERE = '(SELECT|FROM|WHERE|GROUP BY|HAVING)'
  arr = re.split(SELECT_FROM_WHERE, query);

  # the mandatory select-list is the entry after 'SELECT'
  select_list = arr[arr.index('SELECT') + 1];

  # the mandatory from-list is the entry after 'FROM'
  from_list = arr[arr.index('FROM') + 1];

  # if there exists a 'WHERE', get it; otherwise set the where-list to 1=1
  if re.search('WHERE', query) == None:
    where_list = '1 = 1';
  else:
    where_list = arr[arr.index('WHERE') + 1];

  # find the cross product of the from_list (this is very naiive as there may 
  # be context relations)
  cross_text = from_list_to_relalg(from_list);

  return (arr, select_list, where_list, from_list, cross_text);

################################################################################

def normalize_with_ands(query):
  ''' Description.
  Preconditions:  none.
  Postconditions: none. '''

  # obtain parameters pertaining to the outer query
  (oarr, oselect, owhere, ofrom, ocross) = select_from_where_nosubquery(query);
  
  # new_where will replace the where-list
  new_where = '';

  # new_str is ANYTHING following the first instance of 'WHERE'
  # (this includes subqueries and conditions)
  new_str = ' '.join(oarr[oarr.index('WHERE')+1:])

  # clean it up a bit
  new_str = simplify_whitespace(new_str);

  # create a dictionary matching any parentheses
  parens = find_parentheses(new_str)
  
  # locate all instances of 'AND' keyword
  ands = re.finditer('\s+AND\s+', new_str)

  actual_ands = [];
  sub_wheres = [];

  # for every instance of 'AND'
  for a in ands:
      # determine if the given AND is in the top query (i.e. a separator)
      a_index = a.start();
      is_separator = True
      # that is, AND is not between any full set of parentheses (i.e. a subquery)
      for op in parens:
          cp = parens[op];
          if a_index > op and a_index < cp:
              is_separator = False;

      # if AND is in the top query, add it to the list of actual_ands
      if is_separator:
          actual_ands += [a];

  # if there are no ANDs, then we can deal with this in the normal way
  if len(actual_ands) == 0:
      return normalize_without_ands(query);

  # if there are ANDS, then we must take extra care
  else:

      # for each top-level AND, split the where-list at each AND and execute
      # individual queries 
      for ai in range(len(actual_ands)):
          
          # if the AND is the last in the top-level, obtain contents following AND         
          if ai == len(actual_ands) - 1:
              sub_wheres += [new_str[actual_ands[ai].end():]];
          
          # always obtain the contents preceding the AND (special case for ai=0)
          if ai == 0:
              sub_wheres += [new_str[ : actual_ands[ai].start()]]
          else:
              sub_wheres += [new_str[actual_ands[ai-1].end() : actual_ands[ai].start()]]
    
      # for each entry between ANDs
      for where in sub_wheres:
          # create a pseudo SELECT .. FROM .. WHERE .. query Q`
          subwheretext = 'SELECT'  + oselect + ' FROM ' + ofrom + ' WHERE ' + where;
          # recursively call this function and normalize Q`
          normalized_subpart = normalize_with_ands(subwheretext);

          # if this is the first newly normalized sub-where, do not add an AND
          if new_where == '':
              new_where = normalized_subpart[normalized_subpart.index('WHERE') + len('WHERE'):]
          else:
              # make sure that an AND is between the sub-wheres that exist already
              new_where += ' AND ' + normalized_subpart[normalized_subpart.index('WHERE') + len('WHERE'):]
  return 'SELECT ' + oselect + ' FROM ' + ofrom + ' WHERE ' + new_where;

################################################################################

def normalize_without_ands(query):
  ''' Recursively normalize subqueries to be in EXISTS or NOT EXISTS form
  Preconditions:  Query is proper SQL
  Postconditions: Returns subqueries in the query in the proper form '''

  print('NORMALIZING THE QUERY [' + query + ']');

  # get information about the 'outer query'
  (oarr, oselect, owhere, ofrom, ocross) = select_from_where_nosubquery(query);

  subquery_text='';

  #make sure we are working from the query above the outermost query, and solve inward-out
  if hasSubquery(query):
    
    # get the next subquery
    nextsub = getNextSubQuery(query)

    # normalize with ands (we don't know what its structure is)
    nextsub = normalize_with_ands(nextsub);

    # get information about the 'inner query'
    (iarr, iselect, iwhere, ifrom,icross) = select_from_where_nosubquery(nextsub);
    
    # if there is already an inner where clause, append AND
    if iwhere != '':
      iwhere = iwhere[ : -1];
      iwhere += ' AND ';

    ## MODIFICATION BLOCK FOR "NOT IN" ##
    phrase_before_not_in = '([\d\.\w]+)\s+NOT IN';
    pb4ni = re.search(phrase_before_not_in, owhere);

    # if there is a NOT IN keyword, with a phrase preceding it
    # then we want to adjust the query to be in NOT EXISTS form
    if pb4ni:

      # add the condition to inner where-list
      iwhere += iselect + ' = ' + owhere[pb4ni.start():pb4ni.end()-len('NOT IN')];
      
      # remove the phrase from the outer where-list and replace NOT IN with NOT EXISTS
      owhere = re.sub(phrase_before_not_in, 'NOT EXISTS', owhere); 


    ## MODIFICATION BLOCK FOR "IN" ##
    phrase_before_in = '([\d\.\w]+)\s+IN';
    pb4i = re.search(phrase_before_in, owhere);
    
    # if there is an IN keyword, with a phrase preceding it
    # then we want to adjust the query to be in EXISTS form
    if pb4i:

      # add the condition to the inner where-list
      iwhere += iselect + ' = ' + owhere[pb4i.start():pb4i.end()-3];
      
      # remove the phrase from the outer where-list and replace IN with EXISTS
      owhere = re.sub(phrase_before_in, 'EXISTS', owhere);


    ## MODIFICATION BLOCK FOR "ALL" ##

    # split the outer where-list by whitespace (into words)
    owhere_arr = re.split('\s+', owhere);
    
    #may need to do this in REGEX to avoid issues
    
    # if there is at least an ALL keyword in the outer-where list
    if owhere_arr.count('ALL') > 0:

      # get the index of the first instance
      all_index = owhere_arr.index('ALL');

      # this I think is a bit overkill
      if all_index != -1:

        # op_index is the index in the owhere table of the operator
        op_index = all_index - 1;

        # pb4all is the index in the owhere table of the phrase before ALL
        pb4all = owhere_arr[op_index-1];

        # add the phrase with inverted operation to the inner where-list
        iwhere += pb4all + comp_op(owhere_arr[op_index]) + iselect;
        
        # remove the phrase and operation, and replace ALL with NOT EXISTS
        # in the outer where-list
        owhere = re.sub('([\d\.\w]+)\s+[><=]+\s+ALL','NOT EXISTS', owhere)
        #print(owhere);


    ## MODIFICATION BLOCK FOR "ANY" ##

    # split the outer where-list by whitespace (into words)
    owhere_arr = re.split('\s+', owhere);

    #may need to do this with REGEX to avoid issues
    
    # if there is at least an ANY keyword in the outer-where list
    if (owhere_arr.count('ANY') > 0):

      # get the index of the first instance
      any_index = owhere_arr.index('ANY');

      # this I think is a bit overkill
      if (any_index != -1):

        # op_index is the index in the owhere table of the operator
        op_index = any_index - 1;
        
        # pb4any is the index in the owhere table of the phrase before ANY
        pb4any = owhere_arr[op_index-1];

        # add the phrase with operation to the inner where-list
        iwhere += pb4any + owhere_arr[op_index] + iselect;

        # remove the phrase and operation and change ANY to EXISTS
        owhere = re.sub('(\w+)\s+[><=]+\s+ANY','EXISTS', owhere);

    ## MODIFICATION BLOCK FOR COMPARISONS ##

    # split the outer where-list by whitespace (into words)
    owhere_arr = re.split('\s+', owhere);
    op = '';

    # for each word, check if it is an operation
    for entry in owhere_arr:
      op_match = re.match('[><=]+', entry);

      # if so, mark it and continue
      if op_match:
        op = entry;
        break;

    # if there was an operation
    if op != '':

        # op_index is the index in the owhere table of the operator
        op_index = owhere_arr.index(op);

        # pb4op is the index in the owhere table of the phrase before the operator
        pb4op = owhere_arr[op_index - 1];

        # add the phrase with operation to the inner where-list
        iwhere += pb4op + op + iselect;

        # remove the phrase and operation and add EXISTS
        owhere = re.sub('([\d\.\w]+)\s+[><=]+','EXISTS', owhere);

    # once all substitutions have been completed, reform the subquery
    subquery_text = 'SELECT ' + iselect + ' FROM ' + ifrom + ' WHERE ' + iwhere;

  # once all substitutions have (or haven't) been completed, reform the outer query
  query_text = 'SELECT'  + oselect + ' FROM ' + ofrom + ' WHERE ' + owhere;

  # if the subquery existed then push it to the end of the outer query
  if subquery_text != '':
    query_text += subquery_text + ')';

  # return the updated query
  return query_text;

################################################################################

def getRenameMap(from_list, q_arr):
  ''' Get a list of what all functions were renamed, for context relations
      returns dictionary {renamedTable:actualTable}
  Preconditions:  from_list is a proper from_list, Q_arr is a query
  Postconditions: a map of renamed tables to their original names is returned '''

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

################################################################################

def fix_all_correlated_subquery(query, schema, parent_rename_map = { }):
  ''' Description.
  Preconditions:  none.
  Postconditions: none. '''

  subquery = '';
  new_where = '';
  
  # obtain information about the query
  (oarr, oselect, owhere, ofrom, ocross) = select_from_where_nosubquery(query);

  # get anything after the first WHERE in the query and join with spaces
  new_str = ' '.join(oarr[oarr.index('WHERE')+1:])
  new_str = simplify_whitespace(new_str);

  # get dictionary of parenthesis pairs in new_str
  parens = find_parentheses(new_str)

  # get list of all ANDs 
  ands = re.finditer('\s+AND\s+', new_str)
  actual_ands = [];
  sub_wheres = [];

  # for each AND, determine whether it is acting on the top-level query
  # or on a subquery. If it is a top-level query add its information to
  # actual_ands
  for a in ands:
    a_index = a.start();
    is_separator = True
    for op in parens:
        cp = parens[op];
        if a_index > op and a_index < cp:
            is_separator = False;
    if is_separator:
        actual_ands += [a];

  # if there are no top-level ANDs, then we move on to fixing the query
  # as if it has no ANDs
  if len(actual_ands) == 0:
    return fix_correlated_subquery(query, schema);

  # otherwise, we need to create new temporary queries using the paradigm:
  #   SELECT A FROM B WHERE C AND D; ==> SELECT A FROM B WHERE C
  #                                  ==> SELECT A FROM B WHERE D
  # (C, D are examples of "subwheres")
  else:
    # for each top-level AND found
    for ai in range(len(actual_ands)):
        
        # if it is the last AND, get the subwhere after it
        if ai == len(actual_ands) - 1:
            sub_wheres += [new_str[actual_ands[ai].end():]];

        # always get the subwhere before the AND
        if ai == 0:
            sub_wheres += [new_str[:actual_ands[ai].start()]]
        else:
            sub_wheres += [new_str[actual_ands[ai-1].end():actual_ands[ai].start()]]

    # for each subwhere,
    for where in sub_wheres:

        # create a new temporary query that uses the same select-list, from-list
        # but changes the WHERE statement to be the subwhere
        subwheretext = 'SELECT ' + oselect + ' FROM ' + ofrom + ' WHERE ' + where;
        
        # recursively fix correlated subqueries within the temporary query
        fixed_part = fix_all_correlated_subquery(subwheretext, schema);

        # AND together each fixed part of each temporary query
        if new_where == '':
            new_where = fixed_part[fixed_part.index('WHERE')+len('WHERE'):]
        else:
            new_where += ' AND ' + fixed_part[fixed_part.index('WHERE')+len('WHERE'):]
    
  # return the fixed query
  return 'SELECT ' + oselect + ' FROM ' + ofrom + ' WHERE ' + new_where;

################################################################################

def fix_correlated_subquery(query, schema, parent_rename_map = { }):
  ''' Fix context relations in queries with a single correlated subqueries
  Preconditions:  Query is a valid SQL query, Parent_rename_map is the 
                  table of all renamed values in the query's parent query
  Postconditions: the query with solved context relations is returned '''

  # SOME LOGICAL PROBLEMS INCLUDED, TEST THIS MORE

  #Get to innermost subquery
  subquery = '';

  # obtain information about the query (outer query)
  (oarr, oselect, owhere, ofrom, ocross) = select_from_where_nosubquery(query);

  # if the outer query has a subquery, make sure it has been fixed first
  if hasSubquery(query):

    # store the subquery (inner query) and get information about it
    subquery = getNextSubQuery(query);
    (iarr, iselect, iwhere, ifrom, icross) = select_from_where_nosubquery(subquery);
    

    # parent_rename_map has rename values for the parent of the outer query
    # we create an updated version such that it is accurate for the parent of
    # the inner query (i.e. the outer query)
    updated_rename_map = parent_rename_map.copy();

    # get renamed values for the outer query and push them to the map
    rnm = getRenameMap(ofrom, oarr);
    updated_rename_map.update(rnm);

    # recursively call the current function on the inner query because we now
    # have the list of context relations relevant to it
    subquery = fix_correlated_subquery(subquery, schema, updated_rename_map);
    
  
  # find all words in the outer query where-list
  wherarr=re.findall('[\w\d]*\.*[\w\d]+', owhere);

  # redo the map?
  rename_map = getRenameMap(ofrom, oarr);
  print(442, rename_map);
  
  # for each word in the outer query
  for entry in wherarr: 
    
    # if the word is not a keyword (EXISTS is not a context relation)
    if entry != 'EXISTS':

      # if the word is an attribute directly associated with a table (A.B)
      if re.match('[\w\d]+\.[\w\d]+', entry):

        # verify that the table name is a valid table name
        attr = entry[entry.index('.') + 1 :] 
        table = entry[0 : entry.index('.')]

        # if the table name is not a valid renamed table
        if not (table in rename_map.keys()):
          #ifrom = 'CROSS(RENAME_{' + table + '}(' + rename_map[table] + '),' + ifrom + ')';
        #else:
          print(458, parent_rename_map);
          print(460, table);

          #label the table as RENAMEALL, to denote a context relation
          ofrom = 'RENAMEALL_{' + table + '}(' + parent_rename_map[table] + '),' + ofrom;
        
      # if the word is a single word, we must check if the attribute works
      else:

        # look through each currently available table (using local from-list) 
        # and see if the word is a valid attribute for that table. 
        # If so, set flag=true, else flag=false
        flag = False;
        for table in rename_map.values():
          if entry in schema[table].keys():
            flag = True;
            break # RA

        # if there is no valid attribute currently available, then there is
        # a context relation that we must employ and specify (for our sake)
        if not flag:
          for table in parent_rename_map.values():
            if entry in schema[table]:

              # there is a valid context relation for this attribute
              # we denote it with a RENAMEALL and cross it with the rest of the
              # from-list
              ofrom = 'CROSS(RENAMEALL_{' + table + '}(' + parent_rename_map[table] + '),' + ofrom + ')';

  # update the query
  query = 'SELECT ' + oselect + ' FROM ' + ofrom + ' WHERE ' + owhere + subquery;
  
  # if there was a subquery, make sure to get the ending parenthesis
  if subquery != '':
      query += ')';

  return query;
#NOT FINISHED, NAIVE AND DOES NOT APPLY ANY LOGICAL CORRECTIONS

################################################################################

def decorrelate_conjunctive(query,schema):
  ''' Transform a conjunctive query to relational algebra
  Preconditions:  Query already has context relations take into account
  Postconditions: query in its relational algebra form '''

  # already added context relations to the from-list
  subquery = '';
  subquery_free_part = '';
  exists = [];
  notexists = [];

  to_union = [];
  rel_alg = '';

  # obtain information about the top-level query
  (oarr, oselect, owhere, ofrom,ocross) = select_from_where_nosubquery(query);

  # if there is a subquery
  if hasSubquery(query):

    # get the subquery and obtain information about it
    subquery = getNextSubQuery(query);
    (iarr, iselect, iwhere, ifrom, icross) = select_from_where_nosubquery(subquery);

  # split the where-list at ANDs into subwheres
  owhere_arr = re.split('\s+AND\s+', owhere);

  # for each subwhere in the where-list
  # go through and decorrelate each EXISTS/NOT EXISTS query
  for entry in owhere_arr: 
    
    # if the subwhere is not an EXISTS/NOT EXISTS statement, then it is a
    # subquery-free-part and there is no need to add more tables to the from-list
    # simply add it to the subquery free part if it already exists
    if 'EXISTS' not in entry:
      if subquery_free_part == '':
        subquery_free_part = entry
      else:
        subquery_free_part += ' AND ' + entry;


    # if the subwhere is a NOT EXISTS statement, then we need to do some special
    # relational algebra
    elif 'NOT EXISTS' in entry:

      # find all context relations (using RENAMEALL)
      context_relations = re.findall('RENAMEALL_\{[\w\d]+\}\([\w\d]+\)', ifrom);
      attrs = '';

      # for each context relation
      for rel in context_relations:

        table_name = rel[rel.index('(')+1:rel.index(')')];
        rename = rel[rel.index('{') + 1:rel.index('}')];
        
        # add the attributes of the context relation
        attrs += getParameters(schema, table_name, rename)
        
        ofrom_relalg = from_list_to_relalg(ofrom);
        ifrom_relalg = from_list_to_relalg(ifrom);

        # ofrom - [ ofrom |><| PROJECT_{cxt. rel. attrs}(SELECT_{iwhere}(ifrom)) ]
        minus_first = ofrom_relalg;
        minus_nj_first = ofrom_relalg;
        minus_nj_second = 'PROJECT_{' + str(attrs) + '}(SELECT_{' + iwhere + '}('  + ifrom_relalg + '))';
        minus_second = 'NATURALJOIN(' + minus_nj_first + ',' + minus_nj_second + ')';
        natty_join = 'MINUS(' + minus_first + ',' + minus_second + ')';

        # add this entry to an array of all NOT EXISTS relalgs
        notexists += [natty_join];


    # if the subwhere is an EXISTS statement, then we need to do some special
    # relational algebra
    elif 'EXISTS' in entry:

      # find all context relations (using RENAMEALL)
      context_relations = re.findall('RENAMEALL_\{[\w\d]+\}\([\w\d]+\)', ifrom);
      attrs = '';

      # for each context relation
      for rel in context_relations:

        table_name = rel[rel.index('(')+1:rel.index(')')];
        rename = rel[rel.index('{') + 1:rel.index('}')];
        
        # add the attributes of the context relation
        attrs += getParameters(schema, table_name, rename)

        # print(568,from_list_to_relalg(ofrom))
        # print(569,from_list_to_relalg(ifrom))

        # ofrom |><| PROJECT_{cxt. rel. attrs}(SELECT_{iwhere}(ifrom))
        nj_first = from_list_to_relalg(ofrom);
        nj_second = 'PROJECT_{' + str(attrs) + '}(SELECT_{' + iwhere + '}('  + from_list_to_relalg(ifrom) + '))';
        natty_join = 'NATURALJOIN(' + nj_first + ',' + nj_second + ')';
        
        # add this entry to an array of all EXISTS relalgs
        exists += [natty_join];
    
  # for any relational algebra created from EXISTS/NOT EXISTS statements
  for join in (exists + notexists):

    # apply the top-level query projection on the selection of the subquery free
    # part acting on the relational algebra join created prior, and add it to an
    # array to be intersected later
    to_union += ['PROJECT_{' + oselect + '}(' + 'SELECT_{' + subquery_free_part + '}(' + join + '))'];

  ### COMMENTS
  # if there were no EXISTS/NOT EXISTS statements, return simple statement
  if len(to_union) == 0:
    return relalg(oselect, ofrom, owhere);
    return to_union[0];

  # otherwise, (if there were EXISTS/NOT EXISTS)
  else:

    # intersect every relational algebra created from EXISTS/NOT EXISTS
    rel_alg = to_union[0];
    for i in range(1, len(to_union)):
      rel_alg = 'INTERSECT(' + to_union[i] + ',' + rel_alg + ')';

    # return the intersection
    return rel_alg;

################################################################################

def query_into_relational_algebra(query, sch):

  intermediate = query;
  print('### 770 ###: ' + intermediate);

  intermediate = normalize_with_ands(intermediate);
  print('### 772 ###: ' + intermediate);

  intermediate = fix_all_correlated_subquery(intermediate, sch);
  print('### 774 ###: ' + intermediate);

  intermediate = decorrelate_conjunctive(intermediate, sch);
  print('### 776 ###: ' + intermediate);

  return intermediate;