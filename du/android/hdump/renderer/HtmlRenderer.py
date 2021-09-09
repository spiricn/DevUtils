import os

from du.android.hdump.HeapDump import HeapDump
from du.android.hdump.HeapDumpDiff import HeapDumpDiff
from du.android.hdump.renderer.BaseRenderer import BaseRenderer


htmlBase = """\
<html>

<head>
<style>

.css-treeview ul,
.css-treeview li
{
    padding: 0;
    margin: 0;
    list-style: none;
}

.css-treeview input
{
    position: absolute;
    opacity: 0;
}

.css-treeview
{
    font: normal 11px "Segoe UI", Arial, Sans-serif;
    -moz-user-select: none;
    -webkit-user-select: none;
    user-select: none;
}

.css-treeview a
{
    color: #00f;
    text-decoration: none;
}

.css-treeview a:hover
{
    text-decoration: underline;
}

.css-treeview input + label + ul
{
    margin: 0 0 0 22px;
}

.css-treeview input ~ ul
{
    display: none;
}

.css-treeview label,
.css-treeview label::before
{
    cursor: pointer;
}

.css-treeview input:disabled + label
{
    cursor: default;
    opacity: .6;
}

.css-treeview input:checked:not(:disabled) ~ ul
{
    display: block;
}

.css-treeview label,
.css-treeview label::before
{

    background: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAACgCAYAAAAFOewUAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAApxJREFUeNrslM1u00AQgGdthyalFFOK+ClIIKQKyqUVQvTEE3DmAhLwAhU8QZoH4A2Q2gMSFace4MCtJ8SPBFwAkRuiHKpA6sRN/Lu7zG5i14kctaUqRGhGXnu9O/Pt7MzsMiklvF+9t2kWTDvyIrAsA0aKRRi1T0C/hJ4LUbt5/8rNpWVlp8RSr9J40b48fxFaTQ9+ft8EZ6MJYb0Ok+dnYGpmPgXwKIAvLx8vYXc5GdMAQJgQEkpjRTh36TS2U+DWW/D17WuYgm8pwJyY1npZsZKOxImOV1I/h4+O6vEg5GCZBpgmA6hX8wHKUHDRBXQYicQ4rlc3Tf0VMs8DHBS864F2YFspjgUYjKX/Az3gsdQd2eeBHwmdGWXHcgBGSkZXOXohcEXebRoQcAgjqediNY+AVyu3Z3sAKqfKoGMsewBeEIOPgQxxPJIjcGH6qtL/0AdADzKGnuuD+2tLK7Q8DhHHbOBW+KEzcHLuYc82MkEUekLiwuvVH+guQBQzOG4XdAb8EOcRcqQvDkY2iCLuxECJ43JobMXoutqGgDa2T7UqLKwt9KRyuxKVByqVXXqIoCCUCAqhUOioTWC7G4TQEOD0APy2/7G2Xpu1J4+lxeQ4TXBbITDpoVelRN/BVFbwu5oMMJUBhoXy5tmdRcMwymP2OLQaLjx9/vnBo6V3K6izATmSnMa0Dq7ferIohJhr1p01zrlz49rZF4OMs8JkX23vVQzYp+wbYGV/KpXKjvspl8tsIKCrMNAYFxj2GKS5ZWxg4ewKsJfaGMIY5KXqPz8LBBj6+yDvVP79+yDp/9F9oIx3OisHWwe7Oal0HxCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgwD8E/BZgAP0qhKj3rXO7AAAAAElFTkSuQmCC") no-repeat;
}

.css-treeview label,
.css-treeview a,
.css-treeview label::before
{
    display: inline-block;
    height: 16px;
    line-height: 16px;
    vertical-align: middle;
}

.css-treeview label
{
    background-position: 18px 0;
}

.css-treeview label::before
{
    content: "";
    width: 16px;
    margin: 0 22px 0 0;
    vertical-align: middle;
    background-position: 0 -32px;
}

.css-treeview input:checked + label::before
{
    background-position: 0 -16px;
}

/* webkit adjacent element selector bugfix */
@media screen and (-webkit-min-device-pixel-ratio:0)
{
    .css-treeview
    {
        -webkit-animation: webkit-adjacent-element-selector-bugfix infinite 1s;
    }

    @-webkit-keyframes webkit-adjacent-element-selector-bugfix
    {
        from
        {
            padding: 0;
        }
        to
        {
            padding: 0;
        }
    }
}

</style>

</head>

<body>
"""


class HtmlRenderer(BaseRenderer):
    def __init__(self):
        BaseRenderer.__init__(self)

    def render(self, stream, renderObj):
        if isinstance(renderObj, HeapDump) or isinstance(renderObj, HeapDumpDiff):
            heapDump = renderObj

            self._stream = stream

            self._stream.write(htmlBase)

            nodes = (("Zygote", heapDump.zygoteRootNode), ("App", heapDump.appRootNode))

            self._idCounter = 0

            for nodeName, node in nodes:
                self._stream.write('<div class="css-treeview">\n')

                self._stream.write("<ul>\n")

                self._renderNode(nodeName, 0, node)

                self._stream.write("</ul>\n")

                self._stream.write("</div>\n")

            self._stream.write("</body></html>")
        else:
            raise NotImplementedError()

    def _renderNode(self, rootName, indent, node):
        if node.frame:
            indentStr = indent * "  "

            self._idCounter += 1

            itemId = "item-%d" % self._idCounter

            if rootName:
                label = str(node.size) + " " + rootName
            else:
                label = (
                    str(node.size)
                    + " "
                    + os.path.basename(node.frame.library)
                    + " "
                    + node.frame.symbol.file
                    + " "
                    + node.frame.symbol.function
                    + ":"
                    + str(node.frame.symbol.line)
                )

            if node.children:
                self._stream.write(
                    indentStr
                    + '<li><input type="checkbox" id="%s"><label for="%s">%s</label>\n'
                    % (itemId, itemId, label)
                )
            else:
                self._stream.write(indentStr + "<li>%s</li>" % label)

            self._stream.write(indentStr + "<ul>\n")

            # Iterate trough children, sorted by size
            for child in sorted(
                node.children, key=lambda child: child.size, reverse=True
            ):
                self._renderNode(None, indent + 1, child)
            self._stream.write("</li>")

            self._stream.write(indentStr + "</ul>\n")
