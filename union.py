#UNIONS, INTERSECTS, CONTAINS, MINuS

import re
import os
import json
from subprocess import call
import sys

def shedParens(query):
  query = re.sub('[\n\s]+', ' ', query);
  parens = find_parentheses(query);
  if re.match('\s*\(',query) and parens[query.index('(')] == len(query) - 2:
    print('')
    return shedParens(query[1:parens[query.index('(')]]);
  else:
    return query;



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

def queryToRelalg(query):
  query = re.sub('[\n\s]+', ' ', query);
  query = shedParens(query);

  print(49,query);
  print(50,shedParens(query));
  return separateAtConjunction(query);

#only works on top level conjunctions, not in subqueries
#almost works on multiple levels
def separateAtConjunction(query):
  conjunctions = ['UNION', 'INTERSECT', 'CONTAINS', 'MINUS']
  parens = find_parentheses(query);
  conj_sep_list = re.split('[\s\n]+(UNION|INTERSECT|CONTAINS|EXCEPT)[\s\n]+', query);
  first_actual_conjunction = -1;
  last = '';
  i = 0;
  parens = find_parentheses(query)
  conjs = re.finditer('[\s\n]+(UNION|INTERSECT|CONTAINS|EXCEPT)[\s\n]+', query)
  first_actual_conj = None;
  for conj in conjs:
    ci = conj.start();
    is_separator = True
    for op in parens:
      cp = parens[op];
      if ci > op and ci < cp:
        is_separator = False;
    if is_separator:
      first_actual_conj = conj;
  if first_actual_conj != None:
    return_str = '';
    return_str += query[first_actual_conj.start():first_actual_conj.end()];
    return_str += '_{}('
    return_str += queryToRelalg(query[0:first_actual_conj.start()]);
    return_str += ' , '
    return_str += queryToRelalg(query[first_actual_conj.end():]) + ')';
    print(return_str);
    return return_str;
  else:
    return 'TORELALG('+shedParens(query)+')';
    #return postSplitting(query);


test = """
(SELECT S.sname
FROM Sailors S, Reserves R, Boats B
WHERE S.sid = R.sid AND R.bid = B.bid AND B.color = 'red')
INTERSECT
((SELECT S2.sname
FROM Sailors S2, Boats B2, Reserves R2
WHERE S2.sid = R2.sid AND R2.bid = B2.bid AND B2.color= 'green')
UNION
SELECT S2.sname
FROM Sailors S2, Boats B2, Reserves R2
WHERE S2.sid = R2.sid AND R2.bid = B2.bid AND B2.color= 'green')
"""

#queryToRelalg(test);