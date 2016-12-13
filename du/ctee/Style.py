from du.ctee.Color import Color


class Style:
    def __init__(self, fgColor=Color.UNSPECIFIED, bgColor=Color.UNSPECIFIED, italic=False, bold=False, underline=False):
        self.fgColor = fgColor
        self.bgColor = bgColor
        self.italic = italic
        self.bold = bold
        self.underline = underline
