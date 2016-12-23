from du.ctee.processors.BaseProcessor import BaseProcessor

class PasstroughProcessor(BaseProcessor):
    def __init__(self, stylesheet=None):
        BaseProcessor.__init__(self, stylesheet)

    @staticmethod
    def getDefaultStylesheet():
        return '{}'

    def getStyle(self, line):
        return ((line, None),)
