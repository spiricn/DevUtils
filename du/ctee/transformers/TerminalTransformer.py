from du.ctee.Color import Color
from du.ctee.transformers.BaseTransformer import BaseTransformer


class TerminalTransformer(BaseTransformer):
    CODE_START = '\x1b['
    CODE_CLEAR = CODE_START + '0m'
    CODE_RED = CODE_START + '31m'
    CODE_GREEN = CODE_START + '32m'
    CODE_BLUE = CODE_START + '34m'
    CODE_YELLOW = CODE_START + '33m'
    CODE_CYAN  = CODE_START + '36m'
    CODE_MAGENTA = CODE_START + '35m'
    CODE_WHITE = CODE_START + '97m'
    CODE_BLACK = CODE_START + '30m'
    
    COLOR_TO_CODE_MAP = {
        Color.RED : CODE_RED,
        Color.GREEN : CODE_GREEN,
        Color.BLUE : CODE_BLUE,
        Color.YELLOW: CODE_YELLOW,
        Color.CYAN : CODE_CYAN,
        Color.MAGENTA : CODE_MAGENTA,
        Color.WHITE : CODE_WHITE,
        Color.BLACK : CODE_BLACK,
    }
    
    def __init__(self):
        BaseTransformer.__init__(self)
        
    def transform(self, line, style):
        if not style:
            return line
        else:
            return self.COLOR_TO_CODE_MAP[style.color] + line  + self.CODE_CLEAR