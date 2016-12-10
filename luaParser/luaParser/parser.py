
class ParerError(Exception):
    pass

class Parser(object):
    def __init__(self):
        self._ch = ''
        self._at = 0
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
        self._depth = 0
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
            return self.make_string(self._ch);
        elif self._ch.isdigit() or self._ch == '-':
            return self.make_digit()
        else:    
            pass;
    def make_string(self,endChar):
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
        
    def note(self):
        dict = {}
        index = 0
        self.depth += 1
        if self.eat_char('}'):
            self._depth -= 1
            return dict


        pass


if __name__ == '__main__':
    test_str = '{array = {65,23,5,},dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},}'
    digit_arar = '[-65.22]'
    a1 = Parser()
    a= a1.parse_text(digit_arar)
    print a