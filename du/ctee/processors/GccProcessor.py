from du.ctee.processors.BaseProcessor import BaseProcessor


class GccProcessor(BaseProcessor):
    def __init__(self, stylesheet=None):
        BaseProcessor.__init__(self, stylesheet)

    @staticmethod
    def getDefaultStylesheet():
        return '''\
{
'error' : Style(Color.RED),
'warning' : Style(Color.YELLOW),
'info' : Style(Color.CYAN),
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
            'Install: ',
            'target StaticLib: '
        ]

        warningStrings = [
            'warning:',
        ]

        data = (
            (self.stylesheet['error'], errorStrings),
            (self.stylesheet['info'], infoStrings),
            (self.stylesheet['warning'], warningStrings),
        )

        for style, strings in data:
            for i in strings:
                if i in line:
                    return style

        return None
