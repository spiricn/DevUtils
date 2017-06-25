import os

from PyQt4 import QtGui, QtCore
from du.android.hdump.HeapDump import HeapDump
from du.android.hdump.HeapDumpDiff import HeapDumpDiff, DiffNode
from du.android.hdump.SymbolResolver import SymbolResolver
from du.android.hdump.renderer.qt.ui.main import Ui_MainWindow


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, renderObj):
        super(MainWindow, self).__init__(None)

        self.setupUi(self)

        self.treeWidget.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.treeWidget.header().setStretchLastSection(False)

        nodes = (('Zygote', renderObj.zygoteRootNode), ('App', renderObj.appRootNode))
        for nodeName, node in nodes:
            if isinstance(renderObj, HeapDump):
                self._renderTree(nodeName, self.treeWidget, node)
            elif isinstance(renderObj, HeapDumpDiff):
                self._renderDiff(nodeName, self.treeWidget, node)

        self.show()

    def _renderDiff(self, rootName, parentItem, node):
        item = QtGui.QTreeWidgetItem(parentItem)

        colorMap = {
            DiffNode.TYPE_CHANGED : QtGui.QBrush(QtCore.Qt.yellow),
            DiffNode.TYPE_REMOVED : QtGui.QBrush(QtCore.Qt.red),
            DiffNode.TYPE_ADDED : QtGui.QBrush(QtCore.Qt.green),
            DiffNode.TYPE_EQUAL : QtGui.QBrush(QtCore.Qt.white),
        }

        item.setBackground(0, colorMap[node.type])

        if rootName:
            item.setText(0, rootName)
        else:

            item.setText(0, os.path.basename(node.frame.library))

            if node.frame.symbol != SymbolResolver.UNKOWN_SYMBOL:
                item.setText(3, str(node.frame.symbol))

        item.setText(1, str(node.size))

        for child in node.children:
            self._renderDiff(None, item, child)

    def _renderTree(self, rootName, parentItem, node):
        item = QtGui.QTreeWidgetItem(parentItem)

        if rootName:
            self._rootSize = node.size
            item.setText(0, rootName)

        else:
            item.setText(0, os.path.basename(node.frame.library))

            if node.frame.symbol != SymbolResolver.UNKOWN_SYMBOL:
                item.setText(3, str(node.frame.symbol))

        item.setText(1, str(node.size))
        item.setText(2, ' %.2f %%' % ((float(node.size) / float(self._rootSize)) * 100))

        for child in sorted(node.children, key=lambda child: child.size, reverse=True):
            self._renderTree(None, item, child)

