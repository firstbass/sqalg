import re
import fileinput
from test import *
document=''

for line in fileinput.input():
    document+=line;

for entry in re.findall('(SELECT[\s\S]+?;)',document):
    #print(count, entry);
    createTreeImage(decorrelate_conjunctive(fix_correlated_subquery(normalize_without_ands(entry))));
