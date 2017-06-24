import argparse
import logging
import os
import sys

from PyQt4 import QtGui, uic
from du.android.hdump.HeapDump import HeapDump
from du.android.hdump.SymbolResolver import SymbolResolver


class MainWindow(QtGui.QMainWindow):
    def __init__(self, inputFile):
        super(MainWindow, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'ui/main.ui'), self)
        self.show()

        self._nodes = {}

        with open(inputFile, 'r') as fileObj:
            self._heapDump = HeapDump(fileObj.read())
        self.treeWidget.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.treeWidget.header().setStretchLastSection(False)
        nodes = (('Zygote', self._heapDump.zygoteRootNode), ('App', self._heapDump.appRootNode))
        for nodeName, node in nodes:
            self.render(nodeName, self.treeWidget, node)

    def render(self, rootName, parentItem, node):
        item = QtGui.QTreeWidgetItem(parentItem)

        item.setText(1, str(node.size))

        if rootName:
            print(rootName)
            item.setText(0, rootName)
        else:
            item.setText(0, os.path.basename(node.frame.library))

            if node.frame.symbol != SymbolResolver.UNKOWN_SYMBOL:
                item.setText(2, str(node.frame.symbol))

        for child in sorted(node.children, key=lambda child: child.size, reverse=True):
            self.render(None, item, child)
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s/%(name)s: %(message)s')

    parser = argparse.ArgumentParser()
    parser.add_argument('-inputFile')
    args = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    window = MainWindow(args.inputFile)
    sys.exit(app.exec_())
