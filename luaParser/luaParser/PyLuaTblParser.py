g_text = "" 
g_length = 0
g_index = 0
g_prevp = -1
class ParerError(Exception):
    pass

def setText(s):
    g_text = s
    g_length = len(s)
    g_index = 0
    g_prevp = -1
def next_char():
    value = None
    if g_index < g_length:
            ret = g_text[g_index]
            g_index += 1
    return ret
def eat_char(char):
    if char == g_text[g_index]:

class PyLuaTblParser:
    def load(self, s):
        pass
    def dump(self):
        pass
    def loadLuaTable(self, f):
        pass
    def dumpLuaTable(self, f):
        pass
    def loadDict(self, d):
        pass
    def dumpDict(self):
        pass 

if __name__ == '__main__':
    pass