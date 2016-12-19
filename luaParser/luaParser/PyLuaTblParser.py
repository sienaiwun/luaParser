# -*- coding: UTF-8 -*-
class ParerError(Exception):
    pass

class Stack:
     def __init__(self):
         self.items = []

     def isEmpty(self):
         return self.items == []

     def push(self, item):
         self.items.append(item)

     def pop(self):
         return self.items.pop()

     def top(self):
         return self.items[len(self.items)-1]

     def size(self):
         return len(self.items)

class PyLuaTblParser(object):
    def reset(self):
        self._ch = ''
        self._at = 0
        self._depth = 0
        self._prev = -1
        self.is_top_table = True
        

        

    
    def __init__(self, text= "default") :
        self.reset()
        self._text = text
        if not text or not isinstance(text, basestring):
            raise ParerError("Text error")
   
        self._len = len(self._text)    
        self._esc_seq_table = {'\a': r'\a', '\b': r'\b', '\f': r'\f', '\n': r'\n',
                         '\r': r'\r', '\t': r'\t', '\v': r'\v', '\\': r'\\',
                         '\'': r'\'','\"': r'\"', '[': r'\[', ']': r'\]'}
        self._inv_seq_char_map = dict((v, k) for k, v in self._esc_seq_table.iteritems())
        self.indent_stack = Stack()
        self.indent_stack.push(0)
        self.incident_offset = 4

    def incident_store(self):
        return self.indent_stack,self.incident_offset
    
    def incident_refresh(self,offset = 4):
        self.indent_stack = Stack()
        self.indent_stack.push(0)
        self.incident_offset = offset

    def indident_load(self,value):
        self.indent_stack,self.incident_offset = value
    
    def eat_token(self):
        char = self.next_char()
        token_str = ""
        while char and (char.isalnum() or char == '_'):
            token_str += char
            char = self.next_char()
        if char is not None:
            self.back_char()
        return token_str
 
    #read lua_string,
    def eat_lua_string_with_equal_num(self,equal_num):
        ret_string = ''
        char = self.next_char()
        while True:
            if char is None:
                raise ParseEror('invalid lua xstring')
            elif char == ']':
                tem_str, i = ']', equal_num
                next_char = self.next_char()
                while next_char is not None:
                    if i == 0:
                        break
                    if next_char != '=':
                        break
                    i -= 1
                    tem_str += next_char
                    next_char = self.next_char()
                if i == 0 and next_char == ']':
                     return ret_string
                elif next_char is None:
                    raise ParseEror('invalid lua xstring')
                else:
                    ret_string += tem_str
                    char = next_char
                    continue
            if char == '\\':
                char += '\\'
            ret_string += char
            char = self.next_char()
       

    #return (return_string with "" and boolean indicating if it is good lua string)
    #lua string ::= [[...]] | [=[...]=] | ..
    def eat_lua_string(self):
        prev, at = self._prev, self._at
        char = self.next_char()
        if char != '[':#char ==  '['
            raise ParseError('lua string error')
        char = self.next_char()
        equal_num = 0
        while char == '=':
            equal_num += 1
            char = self.next_char()
            if char is None:
                break
        if char == '[':
            # if we are not a xstring, then a ParerError will be raised
            text = self.eat_lua_string_with_equal_num(equal_num)
            return '"' + text + '"', True
        self._prev, self._at = prev, at
        return '', False
    def eat_hex(self):
        intStr = ''
        hex_digit_str = "aAbBcCdDeEfF"
        while self._ch and (self._ch.isdigit() or self._ch in hex_digit_str):
            intStr += self._ch;    
            self.next_char()
        return intStr
    def make_digit(self):
        num_str = ''
        if self.eat_char('-'):
            num_str = '-'
            num_str += self.next_is_digit("minus error")
        num_str += self.eat_digit_string()
        is_int = True
        if num_str == '0' and self._ch in ['x','X']:
            num_str += self._ch
            self.next_char()
            num_str += self.next_is_digit("eat_hex error")
            num_str += self.eat_hex()
        else:
            if self.eat_char('.'):
                is_int = False
                num_str += '.'
                num_str += self.next_is_digit("point error")
                num_str += self.eat_digit_string()
            if self._ch and self._ch in ['e', 'E']:
                is_int = False
                num_str += self._ch
                self.next_char()
                if self._ch and self._ch  in ('+', '-'):
                    num_str += self._ch
                    self.next_char()
                num_str += self.next_is_digit("float error")
                num_str += self.eat_digit_string()
        try:
            if is_int:
                return int(num_str)
            else:
                return float(num_str)
        except:
            pass
   
     #digit string 's correctness is hanled by str_to_num function.
    def eat_digti(self):
        ret_str = ''
        char = self._ch
        if char.isdigit():
            ret_str += self.eat_digit_string()
            if ret_str == '0' and self._ch in ['x','X']:
                ret_str += self._ch
                self.next_char()
                ret_str += self.eat_hex()
            else :
                ret_str += self.eat_digit_string()
        elif char in '+-':
            ret_str += char
            self.next_char()
            ret_str += self.eat_digit_string()
        char = self._ch
        if char == '.':
            ret_str += char
            self.next_char()
            ret_str += self.eat_digit_string()
        char = self._ch
        if char in 'eE':
            ret_str += char
            self.next_char()
            next_char = self._ch
            if next_char.isdigit():
                ret_str += self.eat_digit_string()
            elif next_char in '+-':
                ret_str += next_char
                self.next_char()
                ret_str += self.eat_digit_string()
        try:
            self.str_to_num(ret_str)
        except:
            raise ParerError("digitError")
        
        self.back_char() #next char point to the char next to digit array
        return ret_str
   
    def eat_exp(self):
        char = self.next_valid_char()
        if char == '{':
            self.back_valid_char()
            table_str,_,_ =  self.eat_table()
            return table_str
        
        elif char in '\'\"':
            return self.eat_bracket_string(char)
        elif char.isdigit() or char in '-+.':
            return self.eat_digti()
        elif char.isalpha() or char == '_':
            self.back_valid_char()
            token_str = self.eat_token()
            return token_str
        elif char == '[':
            self.back_valid_char()
            str,lua_ok = self.eat_lua_string()
            if lua_ok:
                return str
            else:
                raise ParerError("lua Error")
             
        raise ParerError("expresion Error")

    def key_valid(self, key):
        n = len(key)
        if n == 0 :
            return False
        if not (key[0].isalpha() or  key[0] == '_'):
            return False
        for char in key[1:]:
            if not (char.isalnum() or char == '_'):
                return False
        return True

    def lua_string_valid(self,lua_str):
        n = len(lua_str)
        if self.isString_symmetry(lua_str):
            return True
        else:
            try:
                 self.str_to_num(lua_str)
            except:
                raise ParerError("lua string error")
            else:
                return True
           
    def eat_fields(self):
        '''
        field ::= '[' former ']' '=' later | expr1 '=' later | later, return (expr1,later)
        '''
        field_str = ''
        former = None 
        later = ''
        char = self.next_valid_char()
        if char == '[':
            self.back_char()
            xstr, ok = self.eat_lua_string()
            if ok:  # we get a xstring
                later += xstr
                field_str = later
            else:
                self.next_char()
                key = self.eat_exp()
                next_char = self.next_valid_char()
                if next_char == ']':
                    if not self.lua_string_valid(key):
                        raise ParseError('lua_string_valid ')
                    former = key
                    if self.next_valid_char() != '=':
                        raise ParseError('invalid table field')
                    later = self.eat_exp()
                    field_str = '[' + former + ']' + '= ' + later
                else:
                    raise ParseError('invalid table field_str')
        else:
            self.back_valid_char()
            former = self.eat_exp()
            char_2 = self.next_valid_char()
            if char_2 == '=':
                if not self.key_valid(former):
                    raise ParseError('invalid variable name : ' + former)
                later = self.eat_exp()
                field_str = former + '= ' + later
            elif char_2 is not None:
                self.back_valid_char()
                former, later = None, former
                field_str = later
            else:
                raise ParseError('invalid table field_str')

        char = self.next_valid_char()
        if char not in ',;}':
            raise ParseError('syntax error near \"' + later + '\"')
        else:
            self.back_char()
        return field_str, (self.parse_key(former), self.parse_expr(later))

    
    # return (tableString, [(expr_key_1,expr_value_1),(expr_key_2,expr_value_2).. ]) 
    def eat_table(self):
        '''
        tableconstructor ::= `{? [fieldlist] `}?
	    fieldlist ::= field {fieldsep field} [fieldsep]
	    field ::= `[? exp `]? `=? exp | Name `=? exp | exp
    	fieldsep ::= `,? | `;?
        '''
        table_str = '{'
        expresions = []
        char = self.next_valid_char()
        if char != '{':
            raise ParerError('table error ')
        while True:
            char = self.next_valid_char()
            if char is None:
                raise ParerError('a table must end with \'}\'')
            elif char == '}':
                break
            else:
                self.back_valid_char()
                field_text, field_expr = self.eat_fields()
                table_str += field_text
                expresions.append( field_expr)
            char = self.next_valid_char()
            if char in ',;':
                if self.next_valid_char() == '}':
                    break
                self.back_char()
            elif char == '}':
                break
            else:
                raise ParseException('table error')
            table_str += ','
        table_str += '}'
        containers,dump_str = self.getContainer(expresions)
        return table_str,containers,dump_str 

                
    def back_char(self):
        self._at -= 1


    def isString_symmetry(self,string):
        n = len(string)
        if n >1 :
            return  string[0] in '\'\"' and string[n-1] in '\'\"' and string[0] == string[n-1]# string
        else :
            return False
    def next_valid_char(self):
        self.skip_white()
        temp = self._at
        while self.skip_comment():
            self.skip_white()
            temp = self._at
        self._prev = temp
        return self.next_char()

    def back_valid_char(self):
       self._at = self._prev
       if self._at == -1:
            raise ParseError('Bug in back valid char')
    def cur(self):
        return self._text[self._at]
    def eat_char(self,char):
        if self._ch and char == self._ch:
            self.next_char()
            self._ch = self._text[self._at]
            return True
        return False
        

    #return the current one, index ++
    def next_char(self):
        if self._at >= self._len:
            self._ch = None
            return None
        self._ch = self._text[self._at]
        self._at += 1
        return self._ch

    def skip_comment(self):
         if self.eat_char('-'):
             if self.eat_char('-'):
                 self.do_skip_comment()
                 return True
             else:
                 self.back_char()
         else:
             return False
    def skip_line(self):
        char = self.next_char()
        while char and char!= '\n':
            char = self.next_char()

    def eat_bracket_string(self,endChar):
        ret_str = '"'
        mark = endChar
        while True:
            char = self.next_char()
            if char is None:
                raise ParerError('a string must end with \' or \"')
            elif char == mark:
                break
            elif char in '\'\"':
                ret_str += '\\' + char
            elif char == '\\': 
                ret_str += '\\' + self.next_char()
            else:
                ret_str += char
        ret_str += '"'
        return ret_str

    def skip_line_num(self,num):
        char = self.next_char()
        while char is not None:
            if char in '\'\"':
                self.back_char()
                self.eat_bracket_string(char)
            elif char == ']':
                next_char = self.next_char()
                count = num
                while next_char == '=' and count >0:
                    count -=1
                    self.next_char()
                if  (count == 0 and self._ch == ']') or next_char is None:
                    return
                elif next_char == ']':
                    continue
            char = self.next_char()
        
            
    def do_skip_comment(self):
        if self.eat_char('['):
            bracket_num = 0
            while self._ch and self.eat_char("="):
                bracket_num+= 1
            if self.eat_char('['):
                self.skip_line_num(bracket_num)
            else:
                self._skip_line()
        else:
           self.skip_line()

   
    def parse_key(self, index):
        if index == None:
            return None
        # the table index must be a string or a number
        n = len(index)
        if self.isString_symmetry(index):
            return self.parse_str(index[1:n-1])
        else:
            try:
                return self.str_to_num(index)
            except:
                return index
               

    
    key_words = {'true': True, 'false': False, 'nil': None}
    def parse_expr(self, expr):
        if self.key_words.has_key(expr):
           return  self.key_words[expr]
        if len(expr) > 0 and expr[0] == '{':  # tabl
            table_parser =  PyLuaTblParser(expr)
            expr_str,_ = table_parser.eat_text()
            return expr_str
        else:
            return self.parse_key(expr)

    def parse_str(self, str):
        ret = ''
        n, index = len(str), 0
        while index < n:
            if str[index] == '\\':
                test_idx = index + 1
                if test_idx < n:
                    next_char = str[test_idx]
                    if next_char.isdigit():
                        char_str, max_leng = '', 3
                        while next_char.isdigit():
                            char_str += next_char
                            test_idx += 1
                            if test_idx < n:
                                next_char = str[test_idx]
                            else:
                                break
                            max_leng -= 1
                            if max_leng == 0:
                                break
                        char = int(char_str)
                        if char > 255:
                            raise ParerError('char error')
                        ret +=  chr(char)
                    
                    else:
                        ret += self.parse_esc_seq('\\' + next_char)
                    index = test_idx
                    
                else:
                    ret += '\\'
                    break
            else:
                ret += str[index]
            index += 1
        return ret


    def parse_esc_seq(self, c):
        if self._inv_seq_char_map.has_key(c):
            return self._inv_seq_char_map[c]
        return '\\' + c

    def getContainer(self,expression_list):
        dct = dict((k,v) for (k,v) in expression_list if k is not None and v is not None)
        lst = [v for (k,v) in expression_list if k is None]
        if len(dct) == 0:
            return lst,'{' + ','.join([self.value_to_dump(item) for item in lst]) + '}'
        elif len(lst) == 0:
            old_Value = self.incident_store()
            self.incident_refresh()
            ret_str = dct,self.dict_to_dump(dct)
            self.indident_load(old_Value)
            return ret_str
        else:
            for i in range(len(lst)):
                if lst[i] is not None:
                    dct[i+1] = lst[i]
            old_Value = self.incident_store()
            self.incident_refresh()
            ret_str = dct,self.dict_to_dump(dct)
            self.indident_load(old_Value)
            return ret_str
    #return a container
    def eat_text(self):
        table_str,container,dump_str = self.eat_table()
        return container,dump_str

    def load(self, test_str):
        parser = PyLuaTblParser(test_str)
        self.container,self.dump_str = parser.eat_text()
        self.is_list = list == type(self.container)
        
    def loadLuaTable(self, file_name):
        fp = open(file_name, 'r')
        self.load(fp.read())
        fp.close() 

    #from a container to  a string
    def dump(self):
        return self.dump_str

     # dump a table to a file
    def dumpLuaTable(self, p):
        f = open(p, 'w')
        f.write(self.dump())
        f.close()

    def char_to_dump(self, c):
        if self._esc_seq_table.has_key(c):
            return self._esc_seq_table[c]
        return c

    def dict_to_dump(self, dct):
        length = len(dct)
        keys = dct.keys()
        is_indented = self.incident_offset > 0
        last_indent =  self.indent_stack.top()
        ret =  ' '*(last_indent) +'{'
        if length == 1:
            key = keys[0]
            ret += self.key_to_dump(key) + '='
            if is_indented:
                ret += ' '
            ret += self.value_to_dump(dct[key])
        elif length != 0:
            new_indent = last_indent + self.incident_offset
            self.indent_stack.push(new_indent)
            stringVec = []
            for key in keys:
                key_string = ''
                if is_indented:
                    key_string += '\n'
                key_string += ' '*(new_indent) + self.key_to_dump(key) + '='
                if is_indented:
                    key_string += ' '
                key_string += self.value_to_dump(dct[key])
                stringVec.append(key_string)
            ret += ','.join(stringVec)
            if is_indented:
                ret += '\n'
            ret += ' '*(last_indent)
            self.indent_stack.pop()
        ret += '}'
        return ret
    

    def value_to_dump(self, value):
        typeId = type(value)
        if bool == typeId:
            if value:
                return 'true'
            else:
                return 'false'
        elif int == typeId or float ==  typeId:
            return str(value)
        elif str == typeId:
            return r'"' + ''.join([self.char_to_dump(c) for c in value]) + r'"'
        elif list == typeId:
            old_Value = self.incident_store()
            self.incident_refresh()
            ret_str =  '{' + ','.join([self.value_to_dump(item) for item in value]) + '}'
            self.indident_load(old_Value)
            return ret_str
        elif dict == typeId:
            return self.dict_to_dump(value)
        return 'nil'

    def key_to_dump(self, index):
        typeId = type(index)
        if int == typeId or float ==  typeId:
            return '[' + str(index) + ']'
        elif str == typeId:
            return r'["'  + ''.join([self.char_to_dump(c) for c in index]) + r'"]'
        else:
            return ParseError('the table index must be a string or a number')
 

    def skip_white(self):
        char = self.next_char()
        while char is not None and char.isspace():
            char = self.next_char()
        if char is not None:
            self.back_char()

    def text_value(self):
        self.skip_white()
        if self.eat_char('{'):
            return self.note()
        elif self._ch in [r'\'',r'"',r'[']:
            return self.eat_bracket_string(self._ch);
        elif self._ch.isdigit() or self._ch == '-':
            return self.make_digit()
        elif self._ch.isalpha():    
            return self.make_word();
        raise ParerError('value no matched pattern')

    key_words = {'true': True, 'false': False, 'nil': None}
    def make_word(self):
        intStr = ''
        while self._ch and self._ch.isalnum():
            intStr += self._ch;    
            self.next_char()
        return self.key_words.get(intStr,intStr)

    

    def eat_digit_string(self):
        intStr = ''
        while self._ch and self._ch.isdigit():
            intStr += self._ch;    
            self.next_char()
        return intStr

    def str_to_num(self,s):
        err_msg = '\"' + s + '\" cannot be converted to a number'
        try:
            i = int(s,0)
        except:
            try:
                f = float(s)
            except:
                raise ParerError(err_msg)
            else:
                return f
        else:
            return i
    
   
    def next_is_digit(self, error_str):
        char = self.next_char()

        if not char.isdigit():
            raise ParerError(error_str)
        return char
    def loadDict(self, dct):
        for k in dct.keys():
            if not isinstance(k, (int, float, str)):
                del dct[k]
        old_Value = self.incident_store()
        self.incident_refresh()
        s = self.dict_to_dump(dct)
        self.indident_load(old_Value)
        self.load(s)
    
    # dump the internal data to a dict
    def dumpDict(self):
        parser = PyLuaTblParser(self.dump())
        tmp,_ = parser.eat_text()
        if isinstance(tmp, list):
            ret = {}
            n = len(tmp)
            for i in range(n):
                if tmp[i] is not None:
                    ret[i+1] = tmp[i]
            return ret
        return tmp

    def update(self,dct):
        if self.is_list:
            raise ParseError("not surport")
        else:
            self.container.update(dct)

    def __getitem__(self, item):
        if self.is_list:
            n = len(self.container)
            if item < 1 or item > n:
                raise ParseError('table index out of range')
            else:
                return self.container[item-1]
        else:
            return self.container[item]
  
    def isWord(ch):
        if ch.isalpha() or ch.isdigit():
            return True
        return False

    def note(self):
        dict = {}
        dict_index = 0
        index = 0
        self._depth += 1
        if self.eat_char('}'):
            self._depth -= 1
            return dict
        else:
            while self._ch:
                    self.skip_white()
                    if self.eat_char('}'):
                        if key is not None:
                            dict[self._index] = key
                            self._index += 1
                        if len( [key for key in dict.keys() if isinstance(key,int)]) ==len(dict):
                            ar = []
                            for key in dict:
                                ar.insert(key,dict[key])
                            dict = ar
                        self._depth -= 1
                        return dict
                    if  self._ch == ',':
                        self.next_char()
                        continue;
                    else:
                        key = self.text_value()
                        self.skip_white()
                        if self._ch in ['=',',']:
                            if self.eat_char('='):
                                value = self.text_value()
                                dict[key] = value
                            elif self.eat_char(','):
                                dict[dict_index] = key
                                dict_index += 1
                            key = None
            raise ParerError('note Error')


__all__ = ['PyLuaTblParser']
'''
if __name__ == '__main__':
    a1 = PyLuaTblParser()
    a2 = PyLuaTblParser()
    a3 = PyLuaTblParser()

    test_str = '{array =   [==[123123]==],}'
    a1.load(test_str)
    d1 = a1.dumpDict()
    print d1
    file_path = "test.txt"
    a2.loadDict(d1)
    a2.dumpLuaTable(file_path)
    a3.loadLuaTable(file_path)

    d3 = a3.dumpDict()
   # b = Encoder()
  #  test_dict = (1,2,3)
 #   print b.encode(test_dict)
 '''