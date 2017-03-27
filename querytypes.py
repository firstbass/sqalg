#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

q1 = 'SELECT * FROM SAILORS AS S, RESERVE AS R, DOGS D, OTHER WHERE X > 5'


def select_from_where_nosubquery(query):
  SELECT_FROM_WHERE = '(SELECT|FROM|WHERE)'# ([\W\w]+) FROM ([\W\w]+) WHERE ([\W\w]+)';
  arr = re.split(SELECT_FROM_WHERE, query);


  q1 = re.sub('[\n\s]+', ' ', query);

  select_list = arr[arr.index('SELECT') + 1];
  from_list = arr[arr.index('FROM') + 1];
  where_list = arr[arr.index('WHERE') + 1];

  from_arr = from_list.split(',')
  #print(from_arr);
  from_list = '';
  for i in range(len(from_arr)):
    from_arr[i].strip();
    word_arr = re.findall('\w+', from_arr[i]);
    if len(word_arr) > 1:
      from_arr[i] = 'RENAME_{' + word_arr[-1] + '}(' + word_arr[0] + ')';
    else:
      from_arr[i] = word_arr[0];

  cross_text = '';
  for i in range(len(from_arr)):
    if i != len(from_arr)-1:
      cross_text += 'CROSS(' + from_arr[i] + ',';
    else:
      cross_text += from_arr[i] + (')' * (i));

  #print(cross_text);

  return 'PROJECT_{' + select_list + '}(SELECT_{' + where_list + '}(' + cross_text + '))';

print(select_from_where_nosubquery(q1));

