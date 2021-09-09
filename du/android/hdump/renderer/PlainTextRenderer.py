import os

from du.android.hdump.HeapDump import HeapDump
from du.android.hdump.HeapDumpDiff import HeapDumpDiff, DiffNode
from du.android.hdump.renderer.BaseRenderer import BaseRenderer


class PlainTextRenderer(BaseRenderer):
    def __init__(self):
        BaseRenderer.__init__(self)

    def render(self, stream, renderObj):
        self._stream = stream

        if isinstance(renderObj, HeapDump) or isinstance(renderObj, HeapDumpDiff):
            nodes = (
                ("Zygote", renderObj.zygoteRootNode),
                ("App", renderObj.appRootNode),
            )

            for nodeName, node in nodes:
                self._stream.write("#" * 80 + "\n")
                self._stream.write("%s\n\n" % nodeName)

                if isinstance(renderObj, HeapDump):
                    self._renderTree(0, node)
                else:
                    self._renderDiff(0, node)

        else:
            raise NotImplementedError()

    def _renderDiff(self, indent, node):
        typeMap = {
            DiffNode.TYPE_CHANGED: "M",
            DiffNode.TYPE_REMOVED: "D",
            DiffNode.TYPE_ADDED: "A",
            DiffNode.TYPE_EQUAL: "",
        }

        if node.frame:
            self._stream.write("." * indent)

            self._stream.write(
                typeMap[node.type]
                + " "
                + os.path.basename(node.frame.library)
                + " "
                + node.frame.symbol.file
                + " "
                + node.frame.symbol.function
                + ":"
                + str(node.frame.symbol.line)
                + "\n"
            )

        for child in sorted(node.children, key=lambda child: child.size, reverse=True):
            self._renderDiff(indent + 1, child)

    def _renderTree(self, indent, node):
        if node.frame:
            self._stream.write("." * indent)
            self._stream.write(
                os.path.basename(node.frame.library)
                + " "
                + node.frame.symbol.file
                + " "
                + node.frame.symbol.function
                + ":"
                + str(node.frame.symbol.line)
                + "\n"
            )

        for child in sorted(node.children, key=lambda child: child.size, reverse=True):
            self._renderTree(indent + 1, child)
