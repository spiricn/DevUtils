from du.ctee.processors.BaseProcessor import BaseProcessor


class LogcatProcessor(BaseProcessor):
    def __init__(self, stylesheet=None):
        BaseProcessor.__init__(self, stylesheet)

    @staticmethod
    def getDefaultStylesheet():
        return '''\
{
'verbose' : Style(fgColor=Color.WHITE, bold=True),
'error' : Style(fgColor=Color.RED, bold=True),
'debug' : Style(fgColor=Color.CYAN, bold=True),
'warning' : Style(fgColor=Color.YELLOW, bold=True),
'fatal' : Style(fgColor=Color.RED, bold=True),
'info' : Style(fgColor=Color.GREEN, bold=True),
}
'''

    def getStyle(self, line):
        if 'V/' in line:
            return self.stylesheet['verbose']
        elif 'E/' in line:
            return self.stylesheet['error']
        elif 'D/' in line:
            return self.stylesheet['debug']
        elif 'W/' in line:
            return self.stylesheet['warning']
        elif 'F/' in line:
            return self.stylesheet['fatal']
        elif 'I/' in line:
            return self.stylesheet['info']

        return None
