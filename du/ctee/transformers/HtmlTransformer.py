from du.ctee.Color import Color
from du.ctee.transformers.BaseTransformer import BaseTransformer
import html


class HtmlTransformer(BaseTransformer):
    COLOR_TO_STYLE_MAP = {
        Color.RED: "rgb(195, 96, 44)",
        Color.GREEN: "rgb(78, 201, 176)",
        Color.BLUE: "blue",
        Color.YELLOW: "rgb(220, 220, 170)",
        Color.CYAN: "rgb(86, 156, 214)",
        Color.MAGENTA: "magenta",
        Color.WHITE: "rgb(212, 212, 212)",
        Color.BLACK: "rgb(30, 30, 30)",
    }

    def __init__(self):
        BaseTransformer.__init__(self)

    def getHeader(self):
        res = """
<!DOCTYPE html>

<html lang="en">

<head>
<meta charset="UTF-8">

<title> Log </title>

<style>
body {
    background-color:rgb(30, 30, 30)
}

p {
    white-space: pre-wrap;
    margin: 0;
    padding:0;
    font-family: monospace;
    font-weight: bold;
}
</style>
</head>

<body>

"""

        return res

    def onLineStart(self):
        return "<p>"

    def onLineEnd(self):
        return "</p>"

    def transform(self, line, style):
        color = "white"
        background = "rgb(30, 30, 30)"

        if style:
            if style.fgColor in self.COLOR_TO_STYLE_MAP:
                color = self.COLOR_TO_STYLE_MAP[style.fgColor]

            if style.bgColor in self.COLOR_TO_STYLE_MAP:
                background = self.COLOR_TO_STYLE_MAP[style.bgColor]

        css = "color:%s; background-color:%s" % (color, background)

        return '<span style="%s">%s</span>' % (css, html.escape(line))

    def getTrailer(self):
        return "</body></html>"
