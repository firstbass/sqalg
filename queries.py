#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from functs import *

'''
    This file will give functions that allow for checking the ownership of
    attributes and tables, and rewriting SQL queries with proper relations
'''

def getSchema(s):
  schema = {};

  # the precedent precedes the schema provided
  precedent = 'Schemas of the underlying relations;\n'
  #additionally precedent is 1)
  start = s.find(precedent) + len(precedent)
  
  # the succeedent precedes the queries provided
  succedent = '2)';
  end = s.find(succedent);

  # obtain only the schema provided and take each line 
  # each line has information about exactly one table
  s = s[start:end].strip();
  s = s.upper();
  s = s.split('\n')

  # for each table, the schema is written in the format (as an example)
  #   a. Table(attr1:type1, attr2:type2, ...)
  for line in s:

    # remove the ordered list item
    match = re.search('\w\.\s*',line)
    line = line[match.end():]

    # change 'Table(...)' to 'schema['Table']={...}'
    line = re.sub('(\w*)','schema[\'\\1\']=', line, count=1);
    line = line.replace('(', '{');
    line = line.replace(')', '}')

    # replace all " attr1:type1 " with " 'attr1':'type1' "
    line = re.sub('(\w*):(\w*)', '\'\\1\':\'\\2\'',line);
    
    # execute and set schema[Table] as a dictionary 
    # with entries for each valid attribute
    exec(line);
  return schema;

################################################################################

def getParameters(schema, tableName, renamed_value = ''):
  ''' This obtains all valid attributes in a table as a CSL.
  Preconditions:  tableName is a valid entry in schema
  Postconditions: Returns all valid attributes as a CSL '''

  # if there is no renamed value, then its renamed value is its original name
  if renamed_value == '':
    renamed_value = tableName;

  # obtain a list of all the attributes
  list_of_params = schema[tableName].keys();
  param_text = ''

  # for each valid attribute of the given Table
  for i in range(len(list_of_params)):

    # add RenamedTable.Attribute
    list_of_params[i] = renamed_value + '.' + list_of_params[i];

  # compile into a string and separate with a comma
  for i in range(len(list_of_params)):
    param_text += list_of_params[i];
    if i != len(list_of_params) - 1:
      param_text += ', '

  return param_text;

################################################################################

def validAttribute(schema, table, attr):
  ''' Ensures that given a schema, an attribute is part of a table.
  Preconditions:  schema is a dictionary of table dictionaries
  Postconditions: returns true or false '''

  # if the attribute is given as 'R1.attr' then make it 'attr'
  if (re.match('\.', attr)):
    attr = attr[attr.index('.') + 1:]
  # return whether the given attribute is in the schema
  return attr in schema[table];

################################################################################

def hasSubquery(query):

  # cleanup the query
  query = simplify_whitespace(query).upper();
  
  # split at each space of the query
  query_arr = query.split(' ');
  selects = [];

  # look for any instance of SELECT within parentheses ([space]SELECT...)
  for select in re.finditer('\([\n\s]*SELECT\s+[\s\S]+\)', query):

    # add the subquery select to the list of subquery selects
    selects += [select.start()];

  # if there is more than one subquery select ==> return true
  return len(selects) >= 1;

################################################################################

# assumes there is a subquery
def getNextSubQuery(query):

  # cleanup the query
  query = simplify_whitespace(query).upper();

  # split at each space of the query
  query_arr = query.split(' ');
  selects = [];

  # look for any instance of SELECT within parentheses ([space]SELECT...)
  for select in re.finditer('\([\n\s]*SELECT[\s\S]+\)', query):

    # add the subquery select to the list of subquery selects
    selects += [select.start()];

  # return the first subquery
  return query[selects[0] + 1: -1];