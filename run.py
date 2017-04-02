import re
import fileinput
import sys
from queries import *
from test import *
from relalgtotable import *
from union import *
document=''
schema = None;
count = 0;
f = None;
if len(sys.argv) != 2:
  print('FAILURE NEED EXACTLY ONE ARGUMENT (FILE WITH INPUT)');
else:
  f = open(sys.argv[1]);
  document = f.read();
  schema = getSchema(document);
  print(18,schema);
  
  document = re.sub('[\s\n]+', ' ', document).upper();
  for entry in re.findall('\w\.\s+(.+?)\;',document):
    print('20: '+entry);

    print('24: '+normalize_with_ands(entry));
    #createTreeImage(decorrelate_conjunctive(fix_all_correlated_subquery(normalize_with_ands(entry))),'tree_'+str(count));
    count+=1;
