from du.ctee.processors.BaseProcessor import BaseProcessor


class LogcatProcessor(BaseProcessor):
    def __init__(self, stylesheet=None):
        BaseProcessor.__init__(self, stylesheet)
        
    @staticmethod
    def getDefaultStylesheet():
        return '''\
{
'verbose' : Style(Color.WHITE),
'error' : Style(Color.RED),
'debug' : Style(Color.CYAN),
'warning' : Style(Color.YELLOW),
'fatal' : Style(Color.RED),
'info' : Style(Color.GREEN),
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