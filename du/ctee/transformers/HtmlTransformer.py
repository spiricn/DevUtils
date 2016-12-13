from du.ctee.Color import Color
from du.ctee.transformers.BaseTransformer import BaseTransformer


class HtmlTransformer(BaseTransformer):
    COLOR_TO_STYLE_MAP = {
        Color.RED : '#f00',
        Color.GREEN : '#0f0',
        Color.BLUE : 'blue',
        Color.YELLOW: '#ff0',
        Color.CYAN : '#0ff',
        Color.MAGENTA : 'magenta',
        Color.WHITE : 'white',
        Color.BLACK : 'black',
    }

    def __init__(self):
        BaseTransformer.__init__(self)

    def getHeader(self):

        css = '''\
body {
    background-color:black
}

p {
    white-space: pre-wrap;
    margin: 0;
    padding:0;
    font-family: monospace;
    font-weight: bold;
}

'''
        res = ''


        res += '<html><head>'

        res += '<style>'

        res += css

        res += '</style></head>'

        return res


    def transform(self, line, style):
        clr = self.COLOR_TO_STYLE_MAP[style.fgColor] if style else 'white'

        style = "color:%s;" % clr

        return '<p style="%s">%s</p>' % (style, line)

    def getTrailer(self):
        return '</body></html>'
