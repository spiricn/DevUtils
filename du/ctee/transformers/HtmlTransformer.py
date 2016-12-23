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

    def onLineStart(self):
        return '<p>'

    def onLineEnd(self):
        return '</p>'

    def transform(self, line, style):
        color = 'white'
        background = 'black'

        if style:
            if style.fgColor in self.COLOR_TO_STYLE_MAP:
                color = self.COLOR_TO_STYLE_MAP[style.fgColor]

            if style.bgColor in self.COLOR_TO_STYLE_MAP:
                background = self.COLOR_TO_STYLE_MAP[style.bgColor]

        css = 'color:%s; background-color:%s' % (color, background)

        return '<span style="%s">%s</span>' % (css, line)

    def getTrailer(self):
        return '</body></html>'
