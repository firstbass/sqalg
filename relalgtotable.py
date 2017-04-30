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


#assume the operator has been found in the expression
#assume operator is not the functional operator/aggregates
#assume always has the underscore with brackets
def parseOperator(operator, expr):
  s = expr;
  parens = find_parentheses(s);
  condition = '';
  first = '';
  second = '';
  separating_comma_index = -1;

  #find the operator
  op_index = s.index(operator);
  print(op_index);

  #find conditions
  if operator != 'CROSS':
    condition = s[s.index('{') + 1 : s.index('}')];
  
  # get the first parenthesis in the expression
  open_paren_index = s.index('(');
  
  # find the pair for the first parenthesis
  close_paren_index = parens[open_paren_index];
  
  # get a list of all commas in the expression 
  comma_iter = re.finditer(',', s);

  # determine if there exists a comma in the same level as the top parentheses
  # if so, it is considered separating and its index is stored in
  # separating_comma_index, otherwise separating_comma_index = -1
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

  # if there exists a separating comma, then it is a binary operator
  # set first to first, second to the second operand
  if separating_comma_index != -1:
    first = s[open_paren_index+1:comma_index]
    second = s[comma_index + 1: close_paren_index]

  # otherwise, there is only one operand set as first
  else:
    first = s[open_paren_index+1:close_paren_index];

  # return pertinent data
  return (operator, condition, first, second);

def getNode(type_of, text):
    ''' Description
    Preconditions:  
    Postconditions:  '''
    node = {}
    node['type'] = type_of
    node['text'] = text
    node['children'] = []
    print(node)
    return node;

################################################################################

def startsWithOp(expr):
    ''' Description.
    Preconditions:  
    Postconditions:  '''

    # remove excess whitespace
    expr = expr.strip();

    # check if the operation is a binary operator
    for op in binary_operators:
        if expr.startswith(op):
            # return true if the operation is binary
            return True;

    # check if the operation is an unary operator
    for op in unary_operators:
        if expr.startswith(op):
            # return true if the operation is unary
            return True;

    # TODO: Account for Function statement

    # expr does not start with operation
    return False;

################################################################################
# TODO: Add aggregate F operator  
def createTree(expr):
    ''' Recursively builds tree from pseudo-relational algebra where the outermost
        operation is put at the root of the tree
    Preconditions:  
    Postconditions:  '''

    # create the placeholder
    tree = {}

    # remove unnecessary whitespace
    expr = expr.strip();

    # if the given expression is not recognized as a keyword then it is a table
    # and must become a table-node
    if not startsWithOp(expr):
        return getNode('table', expr);
    
    # if the expression is recognized then...

    # if the expression's outermost keyword is a projection
    elif expr.startswith('PROJECT'):
        (operator, condition, first, second) = parseOperator('PROJECT', expr)

        # if the projection is selecting everything, then 
        # simply ignore the projection and return whatever 
        # the projection is acting upon
        if condition == '*':
            print('==__DEBUG__==: This is a critical point: 141 ==__DEBUG__==')
            return first;

        # otherwise, return a specialized tree node that
        # specifies the projection
        else:
            text = 'PROJECT_{' + condition + '}'; 
            node = getNode('operator', text)
            node['children'] += [createTree(first)];
            return node;

    # if the expression's outermost keyword is RENAMEALL
    elif expr.startswith('RENAMEALL'):
        (operator, condition, first, second) = parseOperator('RENAMEALL', expr)

        # if the rename is changing the name to the original name
        if condition == first:

            # ignore the rename, it is not necessary
            return createTree(first);

        # otherwise, if the rename is operating on a table at the base level
        # then it is an alias and should be displayed differently
        elif createTree(first).type == 'table':
            text = condition;
            node = getNode('alias', text);
            node['children'] += [createTree(first)];
            return node;

        # any other case should be shown as a rho rename operation
        # acting on an intermediate table (i.e. not a base table)
        else:
            text = 'RENAME_{' + condition + '}';
            node = getNode('operator', text);
            node['children'] += [createTree(first)];
            return node;

    # if the expression's outermost operator is RENAME
    elif expr.startswith('RENAME'):
        (operator, condition, first, second) = parseOperator('RENAME', expr)
        
        # if the rename is changing the name to the original name
        if (condition == first):

            # ignore the rename, it is not necessary
            return createTree(first);

        # if the rename is actually changing the name
        else:

            # create the child node on which the rename is acting
            child = createTree(first);

            # if the child is acting on a base-table,
            # format the rename as an alias
            if child['type'] in ('table', 'alias'):
                text = condition;
                node = getNode('alias', text);
                node['children'] += [child];
                return node;

            # otherwise, format as a standard rho operator
            else:
                text = 'RENAME_{' + condition + '}';
                node = getNode('operator', text);
                node['children'] += [child];
                return node;

    # if the expression's outermost operator is a selection
    elif expr.startswith('SELECT'):
        (operator, condition, first, second) = parseOperator('SELECT', expr)
        
        # create a node with selection conditions and set the child node
        first_node = createTree(first)
        text = operator + '_{' + condition + '}';
        tree = getNode('operator', text);
        tree['children'] += [first_node];
        return tree;

    # if the expression is not a special/unary operation i.e. a binary operation
    else:
        # if the expression starts with a given binary operator
        for op in binary_operators:
            if expr.startswith(op):
                (operator, condition, first, second) = parseOperator(op, expr)
                
                # create trees for both of its operands
                first_node = createTree(first)
                second_node = createTree(second)

                # create an operator-node with children being operand trees
                text = operator;
                tree = getNode('operator', text);
                tree['children'] += [first_node, second_node];
                return tree;      

################################################################################

def createTreeImage(query, image_name):
    ''' Description.
    Preconditions:  
    Postconditions:  '''

    tree_text = unicode(json.dumps(createTree(query)));
    with io.open(JSON_TEMP_FILENAME, 'w', encoding='utf-8') as fileObj:
        fileObj.write(tree_text);
    check_output(PHANTOMJS_EXE_URL + ' ' + FUNCTION_FILE + ' "' + image_name + '"')
    os.remove(JSON_TEMP_FILENAME);