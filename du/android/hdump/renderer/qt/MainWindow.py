import os

from PyQt4 import QtGui
from du.android.hdump.SymbolResolver import SymbolResolver
from du.android.hdump.renderer.qt.ui.main import Ui_MainWindow


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, heapDump):
        super(MainWindow, self).__init__(None)

        self.setupUi(self)

        self._heapDump = heapDump

        self.treeWidget.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.treeWidget.header().setStretchLastSection(False)

        nodes = (('Zygote', self._heapDump.zygoteRootNode), ('App', self._heapDump.appRootNode))
        for nodeName, node in nodes:
            self.render(nodeName, self.treeWidget, node)

        self.show()

    def render(self, rootName, parentItem, node):
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
            self.render(None, item, child)

