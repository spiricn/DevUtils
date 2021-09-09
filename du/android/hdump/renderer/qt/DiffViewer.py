import os

from PyQt4 import QtGui, QtCore
from du.android.hdump.HeapDump import HeapDump
from du.android.hdump.HeapDumpDiff import HeapDumpDiff, DiffNode
from du.android.hdump.SymbolResolver import SymbolResolver
from du.android.hdump.renderer.qt.ui.diffWindow import Ui_MainWindow


class DiffViewer(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, heapDiff):
        super(DiffViewer, self).__init__(None)

        self.setupUi(self)

        self._heapDiff = heapDiff
        self.treeWidget.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.treeWidget.header().setStretchLastSection(False)

        self._display()

        self.cbShowChanged.stateChanged.connect(lambda: self._display())
        self.cbShowEqual.stateChanged.connect(lambda: self._display())
        self.cbShowNewcheckBox.stateChanged.connect(lambda: self._display())
        self.cbShowRemoved.stateChanged.connect(lambda: self._display())

        self.show()

    def _display(self):
        self.treeWidget.clear()

        nodes = (
            ("Zygote", self._heapDiff.zygoteRootNode),
            ("App", self._heapDiff.appRootNode),
        )
        for nodeName, node in nodes:
            self._renderDiff(nodeName, self.treeWidget, node)

    def _renderDiff(self, rootName, parentItem, node):
        item = QtGui.QTreeWidgetItem(parentItem)

        colorMap = {
            DiffNode.TYPE_CHANGED: QtGui.QColor(255, 240, 187),
            DiffNode.TYPE_REMOVED: QtGui.QColor(251, 208, 210),
            DiffNode.TYPE_ADDED: QtGui.QColor(197, 243, 210),
            DiffNode.TYPE_EQUAL: QtGui.QBrush(QtCore.Qt.white),
        }

        for i in range(4):
            item.setBackground(i, colorMap[node.type])

        if rootName:
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

        for child in node.children:
            self._renderDiff(None, item, child)
