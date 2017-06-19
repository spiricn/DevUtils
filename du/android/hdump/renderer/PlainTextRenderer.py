import os

from du.android.hdump.renderer.BaseRenderer import BaseRenderer


class PlainTextRenderer(BaseRenderer):
    def __init__(self):
        BaseRenderer.__init__(self)


    def render(self, stream, node):
        self._stream = stream

        self._renderNode(0, node)

    def _renderNode(self, indent, node):
        if node.frame:
            self._stream.write('.' * indent)
            self._stream.write(os.path.basename(node.frame.library) + ' ' + node.frame.symbol.file + ' ' + node.frame.symbol.function + ':' + str(node.frame.symbol.line) + '\n')

        for child in node.children.values():
            self._renderNode(indent + 1, child)
