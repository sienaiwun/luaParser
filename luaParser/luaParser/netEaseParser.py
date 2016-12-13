# -*- coding: UTF-8 -*-
class ParerError(Exception):
    pass
class A:
    def f(self):
        print "123"
    pass

class Encoder(object):
    def encode(self, obj):
        returnString = ''
        typeId = type(obj)
        if typeId == str:
            return '"%s"' % obj.replace(r'"', r'\"')
        elif typeId in [type(5),type(5.0), type(2+3j),type(1<<31)]:
            return str(obj)
        elif typeId is bool:
            return str(obj).lowercase()
        elif object is None:
            return 'nil'
        elif typeId in [list,dict,tuple]:
            returnString +=  '{'            
            if typeId == dict:
                items = []
                for k, v in obj.iteritems():
                    if type(k) == int :
                        items.append(self.encode(v))
                    else:
                        items.append(str(k)+ '=' + self.encode(v))
                returnString += (',' ).join(items) 
            else:
                returnString += ','.join([self.encode(item) for item in obj]) 
            returnString +=  '}'
            return returnString
        pass
class Parser(object):
    def reset(self):
        self._ch = ''
        self._at = 0
        self._depth = 0
        
    def __init__(self):
        self.reset()
        pass

    def eat_char(self,c):
        if self._ch and c == self._ch:
            self.next_char()
            return True
        return False
    
    def parse_text(self,text):
        self.reset()
        if not text or not isinstance(text, basestring):
            return

        self._text = text
        self._len = len(text)        
        self.next_char()
        return self.text_value()
       

    def next_char(self):
        if self._at >= self._len:
            self._ch = None
            return None
        self._ch = self._text[self._at]
        self._at += 1
        return True

    def match_whie(self):
        if self._ch in  [' ', '\t' , '\n', '\r', '\f','\v']:
            return True
        return False

    def skip_white(self):
        while self._ch:
            if self.match_whie():
                self.next_char()
            break;

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

    def make_bracket_string(self,endChar):
        start_char = self._ch
        if endChar == r'[':
            endChar = r']'
        self.next_char()
        stringStr = ''
        while self._ch and self._ch !=endChar:
            stringStr += self._ch;    
            self.next_char()
        if self.eat_char(endChar):
            return stringStr
        raise ParerError("string erro")

    def make_digit_string(self):
        intStr = ''
        while self._ch and self._ch.isdigit():
            intStr += self._ch;    
            self.next_char()
        return intStr
    
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
    test_str2  = '{array = {65,23,5,},dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},}'
    digit_arar = '[-65.22]'
    a1 = Parser()
    a = a1.parse_text('0x3a')
    b =  a1.parse_text('3')
    print b
   # b = Encoder()
  #  test_dict = (1,2,3)
 #   print b.encode(test_dict)