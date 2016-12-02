from du.ctee.Color import Color
from du.ctee.Style import Style
from du.ctee.processors.BaseProcessor import BaseProcessor


class LogcatProcessor(BaseProcessor):
    def __init__(self):
        BaseProcessor.__init__(self)
        self._styleSheet = {
            'verbose' : Style(Color.WHITE),
            'error' : Style(Color.RED),
            'debug' : Style(Color.CYAN),
        }
        
    def getStyle(self, line):
        if 'V/' in line:
            return self._styleSheet['verbose']
        elif 'E/' in line:
            return self._styleSheet['error']
        elif 'D/' in line:
            return self._styleSheet['debug']
        return None