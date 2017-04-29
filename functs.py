#!/usr/bin/env python
# -*- coding: utf-8 -*-




def simplify_whitespace ( inStr ):
  return re.sub('[\n\s]+', ' ', inStr);







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
