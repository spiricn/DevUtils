from du.ctee.Color import Color
from du.ctee.transformers.BaseTransformer import BaseTransformer


class HtmlTransformer(BaseTransformer):
    COLOR_TO_STYLE_MAP = {
        Color.RED : 'red',
        Color.GREEN : 'green',
        Color.BLUE : 'blue',
        Color.YELLOW: 'yellow',
        Color.CYAN : 'cyan',
        Color.MAGENTA : 'magenta',
        Color.WHITE : 'white',
        Color.BLACK : 'black',
    }
    
    def __init__(self):
        BaseTransformer.__init__(self)
        
    def getHeader(self):
        return '<html><body style="background-color:black;">'
    
    def transform(self, line, style):
        clr = self.COLOR_TO_STYLE_MAP[style.color] if style else 'white'
        
        style="color:%s;" % clr 
        
        return '<p style="%s">%s</p>' % (style, line)
    
    def getTrailer(self):
        return '</body></html>'