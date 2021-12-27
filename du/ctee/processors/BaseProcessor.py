from du.ctee.Color import Color
from du.ctee.Style import Style


class BaseProcessor:
    def __init__(self, stylesheet=None):
        self._stylesheet = {}

        if not stylesheet:
            stylesheet = self.getDefaultStylesheet()

        try:
            sheetGlobals = {"Style": Style, "Color": Color}
            sheetLocals = {}
            self._stylesheet = eval(stylesheet, sheetLocals, sheetGlobals)

        except Exception as e:
            raise RuntimeError("Error parsing stylesheet: %r" % str(e))

    @property
    def stylesheet(self):
        return self._stylesheet

    @staticmethod
    def getDefaultStylesheet():
        return """\
{
'verbose' : Style(fgColor=Color.WHITE, bold=True),
'error' : Style(fgColor=Color.RED, bold=True),
'debug' : Style(fgColor=Color.CYAN, bold=True),
'warning' : Style(fgColor=Color.YELLOW, bold=True),
'fatal' : Style(fgColor=Color.RED, bold=True),
'info' : Style(fgColor=Color.GREEN, bold=True),
'meta' : Style(fgColor=Color.WHITE, bgColor=Color.BLACK),
}
"""

    def transform(self, line):
        raise RuntimeError("Not implemented")
