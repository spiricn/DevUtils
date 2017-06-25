from collections import namedtuple
import logging
import symbol

from du.android.hdump.HeapDumpDoc import HeapDumpDoc
from du.android.hdump.SymbolResolver import SymbolResolver


logger = logging.getLogger(__name__.split('.')[-1])

class StackFrame:
    def __init__(self, address=0, library='', symbol=SymbolResolver.UNKOWN_SYMBOL):
        self._address = address
        self._library = library
        self._symbol = symbol

    @property
    def address(self):
        return self._address

    @property
    def library(self):
        return self._library

    @property
    def symbol(self):
        return self._symbol

class Node:
    def __init__(self, frame=None):
        if not frame:
            frame = StackFrame()

        self._frame = frame
        self._children = {}
        self._numAllocations = 0
        self._size = 0

    @property
    def size(self):
        return self._size

    @property
    def numAllocations(self):
        return self._numAllocations

    @property
    def frame(self):
        return self._frame

    def findChild(self, address, recursive=False):
        if address in self._children:
            return self._children[address]
        elif recursive:
            for child in self.children:
                res = child.findChild(address, True)
                if res:
                    return res

        return None

    @property
    def children(self):
        return self._children.values()

    def addStack(self, size, frameStack):
        self._size += size

        if frameStack:
            frame = frameStack[0]

            if not frame.address in self._children:
                self._children[frame.address] = Node(frame)

            self._children[frame.address].addStack(size, frameStack[1:])

ProcessedStacks = namedtuple('ResolvedSymbols', 'zygoteStacks, appStacks, frameMap')

Stack = namedtuple('Stack', 'size, numAllocations, frames')

class HeapDump:
    def __init__(self, string, symbolDirs=None):
        self._doc = HeapDumpDoc(string)

        res = self._processStacks(self._doc, SymbolResolver(symbolDirs))

        self._zygoteTree = self._buildTree(res.zygoteStacks)
        self._appTree = self._buildTree(res.appStacks)

    @property
    def doc(self):
        return self._doc

    @classmethod
    def _buildTree(cls, frameStacks):
        rootNode = Node()
        for frameStack in frameStacks:
            rootNode.addStack(frameStack.size, frameStack.frames)
        return rootNode

    @classmethod
    def _processStacks(cls, doc, resolver):
        # Mapping of offsetAddress to Symbol
        stackFrameMap = {}

        zygoteStacks = []
        appStacks = []
        for record in doc.allocationRecords:
            frameStack = []
            # Resolve each frame in backtrace
            for frameAddress in reversed(record.backtrace):
                # Frame already created ?
                if frameAddress in stackFrameMap:
                    stackFrame = stackFrameMap[frameAddress]
                else:
                    # Find address mapping
                    pm = None
                    for i in doc.pidMaps:
                        if frameAddress >= i.startAddress and frameAddress <= i.endAddress:
                            pm = i
                            break
                    if not pm:
                        raise RuntimeError('could not find address mapping')

                    offsetAddress = frameAddress - pm.startAddress + pm.offset

                    # We need to resolve this address
                    symbol = resolver.resolve(pm.pathname, offsetAddress)
                    stackFrame = StackFrame(frameAddress, pm.pathname, symbol)
                    stackFrameMap[frameAddress] = stackFrame

                frameStack.append(stackFrame)

            frameStack = Stack(record.size, record.number, frameStack)
            if record.zygoteChild:
                appStacks.append(frameStack)
            else:
                zygoteStacks.append(frameStack)
        return ProcessedStacks(zygoteStacks, appStacks, stackFrameMap)

    @property
    def zygoteRootNode(self):
        return self._zygoteTree

    @property
    def appRootNode(self):
        return self._appTree
