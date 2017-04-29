#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functs import *
import re
import os
import io
import json
from subprocess import call
import sys

from subprocess import check_output

binary_operators = ['NATURALJOIN', 'ANTIJOIN', 'CROSS', 'UNION', 'INTERSECT', 'EXCEPT', 'CONTAINS']
unary_operators = ['PROJECT', 'SELECT', 'RENAME', 'RENAMEALL']

PHANTOMJS_EXE_URL = '.\\phantom\\bin\\phantomjs.exe';
FUNCTION_FILE = 'github.js';
JSON_TEMP_FILENAME = 'data.json';


#test = 'PROJECT_{  S.sname  }(SELECT_{  S.rating = 5 }(CROSS(S,R)))'

#assume the operator has been found in the expression
#assume operator is not the functional operator/aggregates
#assume always has the underscore with brackets
def parseOperator(operator, expr):
  s = expr;
  parens = find_parentheses(s);
  print(parens);
  condition = '';
  first = '';
  second = '';

  #find the operator
  op_index = s.index(operator);
  print(op_index);

  separating_comma_index = -1;

  #find condition
  if operator != 'CROSS':
    condition = s[s.index('{') + 1:s.index('}')];
  
  #get arguments
  open_paren_index = s.index('('); #first parentheses
  close_paren_index = parens[open_paren_index];
  comma_iter = re.finditer(',', s);
  #if no comma, then its an unary operator
  # if comma, could be unary or binary
  #     #determine if there is a 'separating comma'
        # if separating comma --> binary
        # else unary

  for comma in comma_iter:
    comma_index = comma.start();
    is_separator = True
    if comma_index > open_paren_index and comma_index < close_paren_index:
        for op in parens.keys():
            cp = parens[op]
            if comma_index > op and comma_index < cp and op != open_paren_index:
                is_separator = False;
    if is_separator:
        separating_comma_index = comma_index;
        break;

  
  if separating_comma_index != -1:
    first = s[open_paren_index+1:comma_index]
    second = s[comma_index + 1: close_paren_index]
  else:
    first = s[open_paren_index+1:close_paren_index];

  return (operator, condition, first, second);

def getNode(type_of, text):
    node = {}
    node['type'] = type_of
    node['text'] = text
    node['children'] = []
    print(node)
    return node;


#
#binary_operators = ['NATURALJOIN', 'ANTIJOIN', 'CROSS', 'UNION', 'INTERSECT', 'MINUS', 'DIVIDE']
#unary_operators = ['PROJECT', 'SELECT', 'RENAME', 'RENAMEALL']
#
#special_operators = 'PROJECT', 'RENAME', 'RENAMEALL', 'FUNCTION

#no whitespace going in

def startsWithOp(expr):
    #print('invoked startsWithOP')
    expr = expr.strip();
    for op in binary_operators:
        if expr.startswith(op):
            #print(expr + ' starts with ' + op);
            return True;
    for op in unary_operators:
        if expr.startswith(op):
            #print(expr + ' starts with ' + op);
            return True;
    #also account for function statement

    #print(expr + ' does not starts with operation');
    return False;
    
# TODO: Add aggregate F operator  
def createTree(expr):
    tree = {}
    expr = expr.strip();
    if not startsWithOp(expr):
        #must be a table
        return getNode('table', expr);
    
    elif expr.startswith('PROJECT'):
        (operator, condition, first, second) = parseOperator('PROJECT', expr)
        if (condition == '*'):
            return first;
        else:
            text = 'PROJECT_{' + condition + '}'; 
            node = getNode('operator', text)
            node['children'] += [createTree(first)];
            return node;
    elif expr.startswith('RENAMEALL'):
        (operator, condition, first, second) = parseOperator('RENAMEALL', expr)
        if (condition == first):
            #was not actually renamed
            return createTree(first);
        elif (createTree(first).type == 'table'):
            #is an alias
            text = condition;
            node = getNode('alias', text);
            node['children'] += [createTree(first)];
            return node;
        else:
            text = 'RENAME_{' + condition + '}';
            node = getNode('operator', text);
            node['children'] += [createTree(first)];
            return node;
    elif expr.startswith('RENAME'):
        (operator, condition, first, second) = parseOperator('RENAME', expr)
        if (condition == first):
            #was not actually renamed
            return createTree(first);

        else:
            child = createTree(first);
            if child['type'] == 'table' or child['type'] == 'alias':
                text = condition;
                node = getNode('alias', text);
                node['children'] += [child];
                return node;
            else:
                text = 'RENAME_{' + condition + '}';
                node = getNode('operator', text);
                node['children'] += [child];
                return node;
    elif expr.startswith('SELECT'):
        (operator, condition, first, second) = parseOperator('SELECT', expr)
        first_node = createTree(first)
        text = operator + '_{' + condition + '}';
        tree = getNode('operator', text);
        ##print(tree);
        tree['children'] += [first_node];
        ##print(tree);
        return tree;
    else:
        #must be binary operation
        for op in binary_operators:
            if expr.startswith(op):
                #print(189, op, expr);
                (operator, condition, first, second) = parseOperator(op, expr)
                #print(operator, condition, first, second);
                first_node = createTree(first)
                second_node = createTree(second)
                text = operator;
                tree = getNode('operator', text);
                tree['children'] += [first_node, second_node];
                return tree;      








def createTreeImage(query, image_name):
    tree_text = unicode(json.dumps(createTree(query)));
    with io.open(JSON_TEMP_FILENAME, 'w', encoding='utf-8') as fileObj:
        fileObj.write(tree_text);
    check_output(PHANTOMJS_EXE_URL + ' ' + FUNCTION_FILE + ' "' + image_name + '"')
    os.remove(JSON_TEMP_FILENAME);