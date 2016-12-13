from du.ctee.processors.BaseProcessor import BaseProcessor


class GccProcessor(BaseProcessor):
    def __init__(self, stylesheet=None):
        BaseProcessor.__init__(self, stylesheet)

    @staticmethod
    def getDefaultStylesheet():
        return '''\
{
'error' : Style(Color.RED, bold=True),
'warning' : Style(Color.YELLOW, bold=True),
'info' : Style(Color.CYAN, bold=True),
'important' : Style(fgColor=Color.WHITE, bgColor=Color.BLUE, bold=True, underline=True),
}'''

    def getStyle(self, line):
        errorStrings = [': No such file or directory',
                  'error:',
                  'fatal:',
                  ': multiple definition',
                  ': cannot find',
                  '*** No rule to make target',
        ]

        infoStrings = [
            'note:',
            'required from',
            'In instantiation of',
            'In member',
            'In function',
            ': first defined here',
            'make: Entering directory',
            'make: Leaving directory'
        ]

        warningStrings = [
            'warning:',
        ]

        importantStrings = [
            # .so, .apk
            'Install: ',
            # .a
            'target StaticLib: ',
            # .jack
            'Building with Jack: ',
            # .jar
            'target Static Jar: '
        ]

        data = (
            (self.stylesheet['error'], errorStrings),
            (self.stylesheet['info'], infoStrings),
            (self.stylesheet['warning'], warningStrings),
            (self.stylesheet['important'], importantStrings),
        )

        for style, strings in data:
            for i in strings:
                if i in line:
                    return style

        return None
