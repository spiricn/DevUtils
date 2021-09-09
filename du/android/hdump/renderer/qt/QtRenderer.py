from PyQt4 import QtGui
from du.android.hdump.HeapDump import HeapDump
from du.android.hdump.HeapDumpDiff import HeapDumpDiff
from du.android.hdump.renderer.qt.DiffViewer import DiffViewer
from du.android.hdump.renderer.qt.HeapViewer import HeapViewer


class QtRenderer:
    def __init__(self):
        pass

    @classmethod
    def render(cls, renderObj):
        app = QtGui.QApplication([])
        if isinstance(renderObj, HeapDumpDiff):
            window = DiffViewer(renderObj)
        elif isinstance(renderObj, HeapDump):
            window = HeapViewer(renderObj)
        else:
            raise NotImplementedError()

        app.exec_()
