from du.ctee.Color import Color
from du.ctee.transformers.BaseTransformer import BaseTransformer


class TerminalTransformer(BaseTransformer):
    FG_BLACK = "30"
    FG_RED = "31"
    FG_GREEN = "32"
    FG_BLUE = "34"
    FG_CYAN = "36"
    FG_MAGENTA = "35"
    FG_YELLOW = "33"
    FG_WHITE = "97"

    BG_BLACK = "40"
    BG_RED = "41"
    BG_GREEN = "42"
    BG_BLUE = "44"
    BG_CYAN = "46"
    BG_MAGENTA = "45"
    BG_YELLOW = "43"
    BG_WHITE = "47"

    STYLE_BOLD = "1"
    STYLE_UNDERLINE = "4"

    CODE_START = "\x1b["
    CODE_CLEAR = "0"
    CODE_END = "m"

    COLOR_TO_FG = {
        Color.BLACK: FG_BLACK,
        Color.RED: FG_RED,
        Color.GREEN: FG_GREEN,
        Color.BLUE: FG_BLUE,
        Color.YELLOW: FG_YELLOW,
        Color.CYAN: FG_CYAN,
        Color.MAGENTA: FG_MAGENTA,
        Color.WHITE: FG_WHITE,
    }

    COLOR_TO_BG = {
        Color.BLACK: BG_BLACK,
        Color.RED: BG_RED,
        Color.GREEN: BG_GREEN,
        Color.BLUE: BG_BLUE,
        Color.YELLOW: BG_YELLOW,
        Color.CYAN: BG_CYAN,
        Color.MAGENTA: BG_MAGENTA,
        Color.WHITE: BG_WHITE,
    }

    def __init__(self):
        BaseTransformer.__init__(self)

    def transform(self, line, style):
        if not style:
            return line
        else:
            return self._getCode(style) + line + self._getCode(None)

    @staticmethod
    def _getCode(style):
        if style:
            fgCode = None
            if style.fgColor != Color.UNSPECIFIED:
                fgCode = TerminalTransformer.COLOR_TO_FG[style.fgColor]

            bgCode = None
            if style.bgColor != Color.UNSPECIFIED:
                bgCode = TerminalTransformer.COLOR_TO_BG[style.bgColor]

            res = TerminalTransformer.CODE_START

            if style.bold:
                res += TerminalTransformer.STYLE_BOLD + ";"

            if style.underline:
                res += TerminalTransformer.STYLE_UNDERLINE + ";"

            if fgCode:
                res += fgCode + ";"

            if bgCode:
                res += bgCode + ";"

            if res[-1] == ";":
                res = res[:-1]

            res += TerminalTransformer.CODE_END

            return res
        else:
            return (
                TerminalTransformer.CODE_START
                + TerminalTransformer.CODE_CLEAR
                + TerminalTransformer.CODE_END
            )
