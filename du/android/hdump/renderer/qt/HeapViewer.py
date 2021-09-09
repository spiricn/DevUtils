import os

from PyQt4 import QtGui, QtCore
from du.android.hdump.HeapDump import HeapDump
from du.android.hdump.SymbolResolver import SymbolResolver
from du.android.hdump.renderer.qt.ui.heapWindow import Ui_MainWindow


class HeapViewer(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, renderObj):
        super(HeapViewer, self).__init__(None)

        self.setupUi(self)

        self.treeWidget.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.treeWidget.header().setStretchLastSection(False)

        nodes = (("Zygote", renderObj.zygoteRootNode), ("App", renderObj.appRootNode))
        for nodeName, node in nodes:
            if isinstance(renderObj, HeapDump):
                self._renderTree(nodeName, self.treeWidget, node)

        self.show()

    def _renderTree(self, rootName, parentItem, node):
        item = QtGui.QTreeWidgetItem(parentItem)

        if rootName:
            self._rootSize = node.size
            item.setText(0, rootName)

        else:
            item.setText(0, os.path.basename(node.frame.library))

            if node.frame.symbol != SymbolResolver.UNKOWN_SYMBOL:
                symbol = "[%s] %s:%d" % (
                    os.path.basename(node.frame.symbol.file),
                    node.frame.symbol.function,
                    node.frame.symbol.line,
                )

                item.setText(3, symbol)

        item.setText(1, str(node.size))
        item.setText(2, " %.2f %%" % ((float(node.size) / float(self._rootSize)) * 100))

        for child in sorted(node.children, key=lambda child: child.size, reverse=True):
            self._renderTree(None, item, child)
