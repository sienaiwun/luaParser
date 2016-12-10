
class ParerError(Exception):
    pass

class Parser(object):
    def __init__(self):
        self._ch = ''
        self._at = 0
        self._depth = 0
        self._index = 0
        pass

    def eat_char(self,c):
        if self._ch and c == self._ch:
            self.next_char()
            return True
        return False
    def parse_text(self,text):
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
    #解析一段文字符号的值
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

    def make_word(self):
        intStr = ''
        while self._ch and self._ch.isalnum():
            intStr += self._ch;    
            self.next_char()
        return intStr

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

    def make_digit(self):
        num_str = ''
        if self.eat_char('-'):
            num_str = '-'
        num_str += self.make_digit_string()
        is_int = True
        if self.eat_char('.'):
            is_int = False
            num_str += '.' + self.make_digit_string()
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
                        continue;
                    else:
                        key = self.text_value()
                        self.skip_white()
                        if self._ch in ['=',',']:
                            if self.eat_char('='):
                                value = self.text_value()
                                dict[key] = value
                            elif self.eat_char(','):
                                dict[self._index] = key
                                self._index += 1
                            key = None
            raise ParerError('note Error')


if __name__ == '__main__':
    test_str = '{array = {65,23,5}}'
    digit_arar = '[-65.22]'
    a1 = Parser()
    a= a1.parse_text(test_str)
    print a