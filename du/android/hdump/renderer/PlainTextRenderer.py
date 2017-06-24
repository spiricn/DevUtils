import os

from du.Utils import getHumanReadableSize
from du.android.hdump.renderer.BaseRenderer import BaseRenderer


class PlainTextRenderer(BaseRenderer):
    def __init__(self):
        BaseRenderer.__init__(self)


    def render(self, stream, heapDump):
        self._stream = stream

        self._stream.write('Total memory: %s\n\n' % getHumanReadableSize(heapDump.doc.totalMemory))

        nodes = (('Zygote', heapDump.zygoteRootNode), ('App', heapDump.appRootNode))

        for nodeName, node in nodes:
            self._stream.write('#' * 80 + '\n')
            self._stream.write('%s\n\n' % nodeName)
            self._renderNode(0, node)

    def _renderNode(self, indent, node):
        if node.frame:
            self._stream.write('.' * indent)
            self._stream.write(os.path.basename(node.frame.library) + ' ' + node.frame.symbol.file + ' ' + node.frame.symbol.function + ':' + str(node.frame.symbol.line) + '\n')

        for child in sorted(node.children, key=lambda child: child.size, reverse=True):
            self._renderNode(indent + 1, child)
