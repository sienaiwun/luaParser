# -*- coding: UTF-8 -*-
from netEaseParser import *
from netEaseParser import Parser 
lua = Parser()

def number_test():
    """
    Integer and float:
    >>> assert lua.parse_text('3') == 3
    >>> assert lua.parse_text('4.1') == 4.1
    >>> assert lua.parse_text('-0.45') == -0.45
    Scientific:
    >>> assert lua.parse_text('3e-7') == 3e-7
    >>> assert lua.parse_text('-3.23e+17') == -3.23e+17
    Hex:
    >>> assert lua.parse_text('0x3a') == 0x3a
    """

    pass

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    