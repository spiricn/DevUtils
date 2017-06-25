from PyQt4 import QtGui
from du.android.hdump.renderer.qt.MainWindow import MainWindow


class QtRenderer:
    def __init__(self):
        pass

    @classmethod
    def render(cls, renderObj):
        app = QtGui.QApplication([])
        window = MainWindow(renderObj)
        app.exec_()

