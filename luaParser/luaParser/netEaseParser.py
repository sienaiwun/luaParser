# -*- coding: UTF-8 -*-
class ParerError(Exception):
    pass

escape_dict = {'a': '\a', 'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t', 'v': '\v'}

class Parser(object):
    def reset(self):
        self._ch = ''
        self._at = 0
        self._depth = 0
        self._prev = -1
        self.is_top_table = True

    def __init__(self, text):
        self.reset()
        self._text = text
        if not text or not isinstance(text, basestring):
            raise ParerError("Text error")
   
        self._len = len(self._text)    
    #parse a string
    def parse(self):
        lua_list,lua_table = [],{}
        table_string, table_fields = self.parseTable()
        for filed in table_fields:
            pass    
    def parse_token(self):
        char = self.next_char()
        token_str = ""
        while char and (char.isalnum() or char == '_'):
            token_str += char
            char = self.next_char()
        if char is not None:
            self.back_char()
        return token_str
    def make_digit_string(self):
        '''
        char = self._ch
        ret_str = ''
        while char.isdigit():
            ret_str += ret_str
            self.next_char()
            char = self._ch
        return ret_str
        '''
        ret_str = ''
        c = self.next_char()
        while c.isdigit():
            ret_str += c
            c = self.next_char()
        if c is not None:
            self.back_char()

        return ret_str
    #read lua_string,
    def __read_lua_string_with_equal_num(self,equal_num):
        ret_string = ''
        char = self.next_char()
        while True:
            if char is None:
                raise Exception('invalid lua xstring')
            elif char == ']':
                tem_str, i = ']', equal_num
                x = self.next_char()
                while x is not None:
                    if i == 0:
                        break
                    if x != '=':
                        break
                    i -= 1
                    tem_str += x
                    x = self.next_char()
                if i == 0 and x == ']':
                     return ret_string
                elif x is None:
                    raise ParseEror('invalid lua xstring')
                else:
                    ret_string += tem_str
                    char = x
                    continue
            if char == '\\':
                char += '\\'
            ret_string += char
            char = self.next_char()
       

    #return (return_string with "" and boolean indicating if it is good lua string)
    #lua string ::= [[...]] | [=[...]=] | ..
    def read_lua_string(self):
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
            # if we are not a xstring, then a exception will be raised
            text = self.__read_lua_string_with_equal_num(equal_num)
            return '"' + text + '"', True
        self._prev, self._at = prev, at
        return '', False

    def parse_digit(self):
        ret_str = ''
        char = self._ch
        if char.isdigit():
            ret_str += self.make_digit_string()
        elif char in '+-':
            ret_str += char
            self.next_char()
            ret_str += self.make_digit_string()
        char = self._ch
        if char == '.':
            ret_str += char
            self.next_char()
            ret_str += self.make_digit_string()
        char = self._ch
        if char in 'eE':
            ret_str += char
            self.next_char()
            x = self._ch
            if x.isdigit():
                ret_str += self.make_digit_string()
            elif x in '+-':
                ret_str += x
                self.next_char()
                ret_str += self.make_digit_string()
     
        try:
            self.str_to_num(ret_str)
        except:
            raise ParerError("digitError")
        
        self.back_char() #next char point to the char next to digit array
        return ret_str
    def parse_exp(self):
        char = self.next_valid_char()
        if char == '{':
            self.back_valid_char()
            table_str,array =  self.parseTable()
            return table_str
        
        elif char in '\'\"':
            return self.make_bracket_string(char)
        elif char.isdigit() or char in ['-+.']:
            return self.parse_digit()
        elif char.isalpha() or char == '_':
            self.back_valid_char()
            token_str = self.parse_token()
            return token_str
        elif char == '[':
            self.back_valid_char()
            str = self.parse_lua_string()
            return str
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
           
    #parse lua fieds, field ::= '[' expr1 ']' '=' expr2 | expr1 '=' expr2 | expr2, return (expr1,expr2)
    def parse_fields(self):
        '''
        field ::= '[' expr1 ']' '=' expr2 | expr1 '=' expr2 | expr2, return (expr1,expr2)
        '''
        field_str = ''
        expr1 = None #if expre1 == None, expr1 is invalid
        expr2 = ''
        char = self.next_valid_char()
        if char == '[':
            self.back_char()
            xstr, ok = self.read_lua_string()
            if ok:  # we get a xstring
                expr2 += xstr
                field = expr2
            else:
                self.next_char()
                key = self.parse_exp()
                x = self.next_valid_char()
                if x == ']':
                    if not self.lua_string_valid(key):
                        raise ParseError('lua_string_valid ')
                    expr1 = key
                    if self.next_valid_char() != '=':
                        raise ParseError('invalid table field')
                    expr2 = self.parse_exp()
                    field = '[' + expr1 + ']' + '= ' + expr2
                else:
                    raise ParseError('invalid table field')
        else:
            self.back_valid_char()
            expr1 = self.parse_exp()
            char_2 = self.next_valid_char()
            if char_2 == '=':
                if not self.key_valid(expr1):
                    raise ParseError('invalid variable name : ' + expr1)
                expr2 = self.parse_exp()
                field = expr1 + '= ' + expr2
            elif char_2 is not None:
                self.back_valid_char()
                expr1, expr2 = None, expr1
                field = expr2
            else:
                raise ParseError('invalid table field')

        char = self.next_valid_char()
        if char not in ',;}':
            raise ParseError('syntax error near \"' + expr2 + '\"')
        else:
            self.back_char()
        return field, [expr1, expr2]
    # return (tableString, [(expr_key_1,expr_value_1),(expr_key_2,expr_value_2).. ]) 
    def parseTable(self):
        '''
        tableconstructor ::= `{? [fieldlist] `}?
	    fieldlist ::= field {fieldsep field} [fieldsep]
	    field ::= `[? exp `]? `=? exp | Name `=? exp | exp
    	fieldsep ::= `,? | `;?
        '''
        table_str = '{'
        fields = []
        char = self.next_valid_char()
        if char != '{':
            raise ParerError('table error ')
        while True:
            char = self.next_valid_char()
            if char is None:
                raise Exception('a table must end with \'}\'')
            elif char == '}':
                table_str += '}'
                return table_str,fields
            else:
                self.back_valid_char()
                field_text, field_fields = self.parse_fields()
                table_str += field_text
                fields.append(field_fields)
            char = self.next_valid_char()
            if char in ',;':
                if self.next_valid_char() == '}':
                    table_str += '}'
                    return table_str,fields
                self.back_char()
            elif char == '}':
                table_str += '}'
                return table_str,fields
            else:
                raise ParseException('table error')
            table_str += ','


                
    def back_char(self):
        self._at -= 1

    def next_char(self):
        ret_str = None
        if self._at < self._len:
            ret_str = self._text[self._at]
            self._at += 1
        return ret_str
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

    def eat_char(self,char):
        if self._ch and char == self._ch:
            self.next_char()
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

    def make_bracket_string(self,endChar):
        ret_str = '"'
        mark = endChar
        while True:
            char = self.next_char()
            if char is None:
                raise Exception('a string must end with \' or \"')
            elif char == mark:
                break
            elif char in '\'\"':
                ret_str += '\\' + c
            elif char == '\\': 
                ret_str += '\\' + self.__next()
            else:
                ret_str += char
        ret_str += '"'
        return ret_str

    def skip_line_num(self,num):
        while self._ch is not None:
            if self._ch in '\'\"':
                self.next_char()
                make_bracket_string(self._ch)
            elif self.eat_char(']'):
                count = num
                while self._ch == '=' and count >0:
                    count -=1
                    self.next_char()
                if  (count == 0 and self._ch == ']') or self._ch is None:
                    return
                else:
                    continue
        self.__next()

            
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

    def pause_key_value(self, field):
        expr_k, expr_v = field[0], field[1]
        if expr_k is None:
            return None, self.__eval_expr(expr_v)
        else:
            return self.__eval_index(expr_k), self.__eval_expr(expr_v)

    def __eval_index(self, index):
        # the table index must be a string or a number
        n = len(index)
        if self.isString_symmetry(index):
            return self.__eval_string(index[1:n-1])
        else:
            try:
                x =  self.str_to_num(index)
            except:
                return index
            else:
                return x

    def __merge_result(self, lst, dct):
        if len(dct) == 0:
            return lst
        elif len(lst) == 0:
            return dct
        else:
            l = len(lst)
            for i in range(l):
                if lst[i] is not None:
                    dct[i+1] = lst[i]
            return dct

    def __eval_expr(self, expr):
        if expr == 'nil':
            return None
        if expr == 'true':
            return True
        elif expr == 'false':
            return False

        n = len(expr)
        if n > 0 and expr[0] == '{':  # table
            table_parser =  Parser(expr)
            return table_parser.parse_text()
        elif self.isString_symmetry(expr): # string
            return self.__eval_string(expr[1:n - 1])
        try:
            x =  self.str_to_num(expr)
        except: # nil
            return None
        else:   # number
            return x

    def __eval_string(self, s):
        ret = ''
        n, i = len(s), 0
        while i < n:
            if s[i] == '\\':
                i += 1
                if i < n:
                    t, j = self.__eval_string_aux(s, i, n)
                    i = j
                    ret += t
                else:
                    ret += '\\'
                    break
            else:
                ret += s[i]
                i += 1
        return ret

    def __eval_string_aux(self, s, i, n):
        c = s[i]
        if c.isdigit():
            x, m = '', 3
            while c.isdigit():
                x += c
                i += 1
                if i < n:
                    c = s[i]
                else:
                    break
                m -= 1
                if m == 0:
                    break
            y = int(x)
            if y > 255:
                raise Exception('invalid escape sequence \"\\'+ x \
                                + '\", only ASCII code is allowed')
            return chr(y), i
        else:
            return self.__eval_esc_seq(c), i+1

    def __eval_esc_seq(self, c):
        esc_seq_table = {'a': '\a', 'b': '\b', 'f': '\f', 'n': '\n',
                         'r': '\r', 't': '\t', 'v': '\v'}
        if esc_seq_table.has_key(c):
            return esc_seq_table[c]
        elif c in '\\\'\"[]':
            return c
        return '\\' + c

    #return a container
    def parse_text(self):
        table_str,table_fieds = self.parseTable()
        lst, dct = [], {}
        for field in table_fieds:
            # print '__parse_field : ' + str(field)
            k, v = self.pause_key_value(field)
            if k is not None:
                if v is not None:
                    dct[k] = v
            else:
                lst.append(v)
        return self.__merge_result(lst, dct)

    def load(self, s):
        parser = Parser(test_str2)
        self.container = parser.parse_text()
        
    def loadLuaTable(self, file_name):
        fp = open(file_name, 'r')
        self.load(fp.read())
        fp.close() 

    #from a container to  a string
    def dump(self):
        return self.to_dump_string()

     # dump a table to a file
    def dumpLuaTable(self, p):
        f = open(p, 'w')
        f.write(self.dump())
        f.close()

    def to_dump_string(self):
        typeId = type(self.container)
        if typeId == list:
            return self.dump_from_list(self.container)
        return self.dump_from_dict(self.container, 4, 0)
    def __dump_char(self, c):
        esc_seq_table = {'\a': 'a', '\b': 'b', '\f': 'f', '\n': 'n',
                         '\r': 'r', '\t': 't', '\v': 'v'}
        if esc_seq_table.has_key(c):
            return '\\' + esc_seq_table[c]
        elif c in '\\\'\"[]':
            return '\\' + c
        return c

    def dump_from_dict(self, d,indent_factor, indent):
        commanate = False
        length = len(d)
        keys = d.keys()
        if self.is_top_table :
            ret = self.__indent(indent)+'{'
            self.is_top_table = False
        else:
            ret = '{'
        if length == 1:
            key = keys[0]
            ret += self.__dump_index(key)
            ret += '='
            if indent_factor > 0:
                ret += ' '
            ret += self.__dump_value(d[key], indent_factor, indent)
        elif length != 0:
            new_indent = indent + indent_factor
            stringVec = []
            for key in keys:
                '''
                if commanate:
                    ret += ','
                if indent_factor > 0:
                    ret += '\n'
                ret += self.__indent(new_indent)
                ret += self.__dump_index(key)
                ret += '='
                if indent_factor > 0:
                    ret += ' '
                ret += self.__dump_value(d[key], indent_factor, new_indent)
                commanate = True
                '''
                key_string = ''
                if indent_factor > 0:
                    key_string += '\n'
                key_string += self.__indent(new_indent)
                key_string += self.__dump_index(key)
                key_string += '='
                if indent_factor > 0:
                    key_string += ' '
                key_string += self.__dump_value(d[key], indent_factor, new_indent)
                stringVec.append(key_string)
            ret += ','.join(stringVec)
            if indent_factor > 0:
                ret += '\n'
            ret += self.__indent(indent)
        ret += '}'
        return ret

    def __indent(self, indent):
        ret = ''
        for i in range(indent):
            ret += ' '
        return ret

    def __dump_value(self, v, indent_factor, indent):
        if isinstance(v, bool):
            if v:
                return 'true'
            else:
                return 'false'
        elif isinstance(v, (int, float)):
            return str(v)
        elif isinstance(v, str):
            return self.__dump_string(v)
        elif isinstance(v, list):
            return self.dump_from_list(v)
        elif isinstance(v, dict):
            return self.dump_from_dict(v, indent_factor, indent)
        return 'nil'

    def __dump_string(self, s):
        ret = ''
        for c in s:
            ret += self.__dump_char(c)
        return '\"' + ret + '\"'

    def dump_from_list(self,list_str):
        if type(list_str) != list:
            raise ParerError("bug")

        commanate = False
        ret = '{'
        for elem in list_str:
            if commanate:
                ret += ','
            ret += self.__dump_value(elem, 0, 0)
            commanate = True
        ret += '}'
        return ret

    def __dump_index(self, index):
        if isinstance(index, (int, float)):
            return '[' + str(index) + ']'
        elif isinstance(index, str):
            return '[' + self.__dump_string(index) + ']'
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
            return self.make_bracket_string(self._ch);
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

    

    def make_digit_string(self):
        intStr = ''
        while self._ch and self._ch.isdigit():
            intStr += self._ch;    
            self.next_char()
        return intStr

    def str_to_num(self,s):
        err_msg = '\"' + s + '\" cannot be converted to a number'
        try:
            i = int(s)
        except:
            try:
                f = float(s)
            except:
                raise ParerError(err_msg)
            else:
                return f
        else:
            return i
    
    def hex(self):
        intStr = ''
        hex_digit_str = "aAbBcCdDeEfF"
        while self._ch and (self._ch.isdigit() or self._ch in hex_digit_str):
            intStr += self._ch;    
            self.next_char()
        return intStr
    def next_is_digit(self, error_str):
        char = self._ch;
        self.next_char();
        if not char.isdigit():
            raise ParerError(error_str)
        return char

    def make_digit(self):
        num_str = ''
        if self.eat_char('-'):
            num_str = '-'
            num_str += self.next_is_digit("minus error")
        num_str += self.make_digit_string()
        is_int = True
        if num_str == '0' and self._ch in ['x','X']:
            num_str += self._ch
            self.next_char()
            num_str += self.next_is_digit("hex error")
            num_str += self.hex()
        else:
            if self.eat_char('.'):
                is_int = False
                num_str += '.'
                num_str += self.next_is_digit("point error")
                num_str += self.make_digit_string()
            if self._ch and self._ch in ['e', 'E']:
                is_int = False
                num_str += self._ch
                self.next_char()
                if self._ch and self._ch  in ('+', '-'):
                    num_str += self._ch
                    self.next_char()
                num_str += self.next_is_digit("float error")
                num_str += self.make_digit_string()
        try:
            if is_int:
                return int(num_str)
            else:
                return float(num_str)
        except:
            pass
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


if __name__ == '__main__':
    test_str2  =   '{array = {65,23,5,},dict = {mixed = {43,nil,false,9,string = "value",},array = {3,6,4,},string = "value",},}'
    digit_arar = '[-65.22]'
    a1 = Parser(test_str2)
    #b = a1.parse_text()
    a1.load(test_str2)
    str = a1.dump()
    print str
   # b = Encoder()
  #  test_dict = (1,2,3)
 #   print b.encode(test_dict)