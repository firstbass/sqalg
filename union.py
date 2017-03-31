#UNIONS, INTERSECTS, CONTAINS, MINuS

import re
import os
import json
from subprocess import call
import sys


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
  return 'RelAlg(' + query + ')';

#only works on top level conjunctions, not in subqueries
def separateAtConjunctions(query):
  conjunctions = ['UNION', 'INTERSECT', 'CONTAINS', 'MINUS']
  parens = find_parentheses(query);
  conj_sep_list = re.split('\s+(UNION|INTERSECT|CONTAINS|EXCEPT)\s+', query);
  last = '';
  i = 0;
  while i <  len(conj_sep_list):
    entry = conj_sep_list[i];
    if entry in conjunctions:
      last = entry + '_{}(' + last + ' , ' + queryToRelalg(conj_sep_list[i+1]) + ')';
      i += 2;
    else:
      last = queryToRelalg(entry);
      i+= 1;

  print(last);

test = """
SELECT S.sname
FROM Sailors S, Reserves R, Boats B
WHERE S.sid = R.sid AND R.bid = B.bid AND B.color = 'red'
INTERSECT
SELECT S2.sname
FROM Sailors S2, Boats B2, Reserves R2
WHERE S2.sid = R2.sid AND R2.bid = B2.bid AND B2.color= 'green' AND 
UNION
(SELECT S2.sname
FROM Sailors S2, Boats B2, Reserves R2
WHERE S2.sid = R2.sid AND R2.bid = B2.bid AND B2.color= 'green');
"""

separateAtConjunctions(test);