import time

from du.android import LogcatParser
from du.android.LogcatParser import INVERSE_LOGCAT_LEVEMAP
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
'meta' : Style(fgColor=Color.WHITE, bgColor=Color.BLACK),
}
'''

    def getStyle(self, line):
        parsed = LogcatParser.parseLine(line)
        if not parsed:
            return ((line, self._findStyle(line)),)

        meta = ''
        meta += parsed.time.strftime('%M:%H:%S.%f') + str(parsed.level)

        paddingSize = 5 - len(str(parsed.pid))

        paddedPid = (paddingSize * '0') + str(parsed.pid)
        meta += ' ' + INVERSE_LOGCAT_LEVEMAP[parsed.level] + ' ' + paddedPid + ' ' + parsed.tag + ':'

        return (
            (meta, self.stylesheet['meta']), (' ', None), (parsed.message, self._findStyle(line))
        )

    def _findStyle(self, line):
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
