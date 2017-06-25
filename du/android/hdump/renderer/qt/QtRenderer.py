from PyQt4 import QtGui
from du.android.hdump.renderer.qt.MainWindow import MainWindow


class QtRenderer:
    def __init__(self):
        pass

    @classmethod
    def render(cls, heapDump):
        app = QtGui.QApplication([])
        window = MainWindow(heapDump)
        app.exec_()

