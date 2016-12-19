# luaParser
The parser interprets Lua tables that have the following syntax form:https://www.lua.org/manual/5.1/manual.html
There is mainly one class in this project. PyLuaTblParser provides both the interface and the Lua table parser function. 
The load() method loads and parses a lua table from a string, the dump() method dumps the string which represents the abstract syntax tree built during load() functon.
The eat_text() method read the table code, and decode it into an abstract syntax tree called container as well as parse the abstract syntax tree into dump string recursively. A incident stack is used to dump a dict into a readable form.
This parser surport hex digit representation.
# Basic usage

from PyLuaTblParser import * ＜/br＞
a1 = PyLuaTblParser()＜/br＞
a2 = PyLuaTblParser()＜/br＞
a3 = PyLuaTblParser()＜/br＞
＜/br＞

test_str = '{array = {0x6A,23,5,},dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},}'＜/br＞
a1.load(test_str)＜/br＞
d1 = a1.dumpDict()＜/br＞
＜/br＞
a2.loadDict(d1)＜/br＞
file_path = "test.txt"＜/br＞
a2.dumpLuaTable(file_path)＜/br＞
a3.loadLuaTable(file_path)＜/br＞
＜/br＞
d3 = a3.dumpDict()＜/br＞

