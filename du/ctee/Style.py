from du.ctee.Color import Color


class Style:
    def __init__(self, fgColor=Color.WHITE, bgColor=Color.BLACK, italic=False, bold=False, underline=False):
        self.fgColor = fgColor
        self.bgColor = bgColor
        self.italic = False
        self.bold = False
        self.underline = False
