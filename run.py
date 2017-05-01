import re
import fileinput
import sys
from queries import *
from test import *
from relalgtotable import *
import traceback
document = None;
schema = None;
count  = 0;
fileObj = None;

# this function replaces all combinations of whitespace and
# newlines with a single space
def simplify_whitespace ( inStr ):
  return re.sub('[\n\s]+', ' ', inStr);


# 

def shedParens ( query ):

  # simplify the whitespace in the query
  query = simplify_whitespace(query);

  # find the parentheses
  parens = find_parentheses(query);
  
  if re.match('\s*\(', query) and parens[query.index('(')] == len(query) - 2:

    # this is the text inside the outer most parentheses
    inner_text = query[1:parens[query.index('(')]];

    # shed the parentheses of the inner text
    return shedParens(inner_text);
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
    
    # go through each character in the string
    for index, char in enumerate(s):
        
        # push opening parentheses
        if char == '(':
            stack.append(index)

        # when closing parentheses come, add the pair to parentheses_locs
        elif char == ')':
            try:
                parentheses_locs[stack.pop()] = index
            except IndexError:
                raise IndexError('Too many closing parentheses at index {}'.format(index))
    
    # if there is still entries on the stack, then error
    if stack:
        raise IndexError('No matching closing parenthesis to opening parenthesis at index {}'.format(stack.pop()))
    
    # return the dictionary
    return parentheses_locs


def queryToRelalg(query,sch):

  # remove superfluous parentheses
  query = shedParens(query);

  # print(49,query);
  # print(50,shedParens(query));
  return separateAtConjunction(query,sch);

#only works on top level conjunctions, not in subqueries
#almost works on multiple levels

def separateAtConjunction(query,sch):

  # conjunctions are places where it is acceptable to split
  conjunctions = ['UNION', 'INTERSECT', 'CONTAINS', 'EXCEPT']

  # obtain dictionary of all parentheses
  parens = find_parentheses(query);

  SPLIT_AT_CONJ_REGEX = '[\s\n]+(UNION|INTERSECT|CONTAINS|EXCEPT)[\s\n]+';
  # create a list that creates new entries at all conjunctions, including the conjunctions
  # e.g. A UNION B ==> [A, UNION, B]
  conj_sep_list = re.split(SPLIT_AT_CONJ_REGEX, query);


  first_actual_conjunction = -1;
  last = '';

  i = 0;
  # obtain the same dictionary of all parentheses
  parens = find_parentheses(query)


  conjs = re.finditer(SPLIT_AT_CONJ_REGEX, query)
  first_actual_conj = None;

  # look at all conjunctions and finds the first conjunction that acts on the
  # top-level query and sets it as first_actual_conj
  for conj in conjs:
    # ci is the start index of the conjunction
    ci = conj.start();
    is_separator = True
    # for all opening parentheses
    for op in parens:
      # cp is the closing parenthesis
      cp = parens[op];
      # if the conjunction index is in its own parentheses, it is not a separator
      # for the top-level query
      if ci > op and ci < cp:
        is_separator = False;
    # we have found the first conjunction
    if is_separator:
      first_actual_conj = conj;

  first_subquery = '';
  second_subquery = '';
  # if no top-level query conjunction is found
  if first_actual_conj != None:
    return_str = '';

    first_subquery = queryToRelalg(query[0:first_actual_conj.start()],sch);
    second_subquery = queryToRelalg(query[first_actual_conj.end():],sch);

    return_str += query[first_actual_conj.start():first_actual_conj.end()].strip();
    return_str += '(' + first_subquery + ' , ' + second_subquery + ')';
    print(return_str);
    return return_str;
  else:
    return query_into_relational_algebra(shedParens(query), sch);
    #return decorrelate_conjunctive(fix_all_correlated_subquery(normalize_with_ands(shedParens(query)),sch),sch);
    #return postSplitting(query);

# commands must be given as 'run.py <filename>'
if len(sys.argv) != 2: 
  print('Invalid command: must provide a file to run input on');

# if valid input is given
else:

  # get the contents of the input file
  filename = sys.argv[1];
  fileObj = open(filename);
  document = fileObj.read();

  # set schema to a dictionary of the valid schema
  schema = getSchema(document);

  # cut off the schema portion of the document
  document = document[document.index('2)'):];

  # transform any whitespace and newline combination into single spaces
  # and turn everything into uppercase, because case does not matter in SQL
  document = re.sub('[\s\n]+', ' ', document).upper();

  # selects queries presented to us of the form (a. ----- ;)
  for entry in re.findall('\w\.\s+(.+?)\;',document):
    if count < 1:
      count = count + 1;
      continue;
    # in the event that an error arises, we exit the current query's execution
    # and move on to the next without any output for the erroring query
    try:
      #print('__174');
      tree_string = separateAtConjunction(entry, schema);
      #print('__176');
      tree_name = 'tree_' + str(count);
      #print('__178');
      createTreeImage(tree_string, tree_name);
      #print('__180');
      # save the query in a data file
      fileObj = open(tree_name + '.dat', 'wb');
      #print('__183');
      fileObj.write(entry);
      #print('__185');
      # Close opened file
      fileObj.close()
      #print('__188');
      '''createTreeImage(separatdecorrelate_conjunctive(fix_all_correlated_subquery(normalize_with_ands(entry),schema)), 'tree_'+str(count));
         createTreeImage(decorrelate_conjunctive(fix_all_correlated_subquery(normalize_with_ands(entry))),'tree_'+str(count));
      '''

    # if the user wishes to exit the program, then allow it
    except KeyboardInterrupt:
      break;

    # any other sort of exception should be dealt with as if the parsing failed
    except:
      print('Error: that query was not successfully parsed by our program :(');
      traceback.print_tb(sys.exc_info()[2]);
      traceback.print_exc();
    
    # no matter what, make sure we move on to the next query
    finally:
      count += 1;
      raw_input('Press enter (' + str(count-1) + ')...');