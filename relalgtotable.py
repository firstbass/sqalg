#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import os
import io
import json
from subprocess import call
import sys

from subprocess import check_output

binary_operators = ['NATURALJOIN', 'ANTIJOIN', 'CROSS', 'UNION', 'INTERSECT', 'MINUS', 'DIVIDE']
unary_operators = ['PROJECT', 'SELECT', 'RENAME', 'RENAMEALL']

test = 'PROJECT_{  S.sname  }(SELECT_{  S.rating = 5 }(CROSS(S,R)))'
''' Parentheses code is courtesy of scipython.com/blog/parenthesis-matching-in-python '''
def check_parentheses(s):
    """ Return True if the parentheses in string s match, otherwise False. """
    j = 0
    for c in s:
        if c == ')':
            j -= 1
            if j < 0:
                return False
        elif c == '(':
            j += 1
    return j == 0

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

  #find condition
  if operator != 'CROSS':
    condition = s[s.index('{') + 1:s.index('}')];
  
  
  #get arguments
  open_paren_index = s.index('('); #first parentheses
  close_paren_index = parens[open_paren_index];
  comma_iter = re.finditer(',', s);
  for comma in comma_iter:
    comma_index = comma.start();
    is_separator = True
    if comma_index > open_paren_index and comma_index < close_paren_index:
        for op in parens.keys():
            cp = parens[op]
            if comma_index > op and comma_index < cp and op != open_paren_index:
                is_separator = False;
    if is_separator:
        first = s[open_paren_index+1:comma_index]
        second = s[comma_index + 1: close_paren_index]
        print(first, second);
        print('separator:',comma_index);
    else:
        first = s[open_paren_index+1:close_paren_index];
    
  #while comma_index:
  #  print(comma_index.start())
  #  comma_index = re.search('\,', comma_index.start() + 1, s, flags=0)
  
  
 


  #(0:8, 1:4, 2:3, 6:7)
  #if there is a comma such that it does fall between the outer parens
  #and it does not fall between any other parens ==> it separates two entries






  #find _



  #op_{}(,)


# operator_{condition}  (first,second)



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
    for op in binary_operators:
        if expr.startswith(op):
            return True;
    for op in unary_operators:
        if expr.startswith(op):
            return True;
    #also account for function statement
    return False;
    
#add function later!    
def createTree(expr):
    tree = {}
    if not startsWithOp(expr):
        #must be a table
        return getNode('table', expr);
        
    for op in binary_operators:
        if expr.startswith(op):
            (operator, condition, first, second) = parseOperator(op, expr)
            print(operator, condition, first, second);
            first_node = createTree(first)
            second_node = createTree(second)
            if operator != 'CROSS':
                text = operator + '_{' + condition + '}';
            else:
                text = operator;
            tree = getNode('operator', text);
            tree['children'] += [first_node, second_node];
            return tree;
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
            (operator, condition, first, second) = parseOperator(op, expr)
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
            (operator, condition, first, second) = parseOperator(op, expr)
            if (condition == first):
                #was not actually renamed
                return createTree(first);
            elif (createTree(first).type == 'table'):
                #is an alias
                text = condition;
                node = getNode('alias', text);
                node['children'] += [createTree(first)]
                return node;
            else:
                text = 'RENAME_{' + condition + '}';
                node = getNode('operator', text);
                node['children'] += [createTree(first)];
                return node;
        elif expr.startswith('SELECT'):
            (operator, condition, first, second) = parseOperator('SELECT', expr)
            first_node = createTree(first)
            text = operator + '_{' + condition + '}';
            tree = getNode('operator', text);
            print(tree);
            tree['children'] += [first_node];
            print(tree);
            return tree;        

def createTreeImage(query, image_name):
    tree_text = unicode(json.dumps(createTree(query)));
    with io.open('data.json', 'w', encoding='utf-8') as f:
        f.write(tree_text);
    check_output('.\\phantom\\bin\\phantomjs.exe github.js "' + image_name + '"')
    #os.remove('data.json');



createTreeImage(test, 'hoobaloo');