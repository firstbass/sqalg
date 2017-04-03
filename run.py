import re
import fileinput
import sys
from queries import *
from test import *
from relalgtotable import *
document=''
schema = None;
count = 0;
f = None;




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

def queryToRelalg(query,sch):
  query = re.sub('[\n\s]+', ' ', query);
  query = shedParens(query);

  print(49,query);
  print(50,shedParens(query));
  return separateAtConjunction(query,sch);

#only works on top level conjunctions, not in subqueries
#almost works on multiple levels
def separateAtConjunction(query,sch):
  conjunctions = ['UNION', 'INTERSECT', 'CONTAINS', 'EXCEPT']
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
    return_str += query[first_actual_conj.start():first_actual_conj.end()].strip();
    return_str += '('
    return_str += queryToRelalg(query[0:first_actual_conj.start()],sch);
    return_str += ' , '
    return_str += queryToRelalg(query[first_actual_conj.end():],sch) + ')';
    print(return_str);
    return return_str;
  else:
    return decorrelate_conjunctive(fix_all_correlated_subquery(normalize_with_ands(shedParens(query)),sch),sch);
    #return postSplitting(query);





if len(sys.argv) != 2:
  print('FAILURE NEED EXACTLY ONE ARGUMENT (FILE WITH INPUT)');
else:
  f = open(sys.argv[1]);
  document = f.read();
  schema = getSchema(document);
  
  document = document[document.index('2)'):];
  document = re.sub('[\s\n]+', ' ', document).upper();
  for entry in re.findall('\w\.\s+(.+?)\;',document):
    try:
      print('----------------------------')
      print('----------------------------')
      print('----------------------------')
      print(entry);
      print('----------------------------')
      print('----------------------------')

      createTreeImage(separateAtConjunction(entry,schema), 'tree_' +str(count));
      # Open a file
      fo = open('tree_'+str(count)+'.dat', "wb")
      fo.write(entry);

      # Close opend file
      fo.close()

      #createTreeImage(separatdecorrelate_conjunctive(fix_all_correlated_subquery(normalize_with_ands(entry),schema)), 'tree_'+str(count));
      #createTreeImage(decorrelate_conjunctive(fix_all_correlated_subquery(normalize_with_ands(entry))),'tree_'+str(count));
    except KeyboardInterrupt:
      break;
    except:
      print('That query was not successfully parsed by our program :(');
      print(sys.exc_info()[0]);
    finally:
      count+=1;
