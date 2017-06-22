from collections import namedtuple
import logging
import symbol

from du.android.hdump.HeapDumpDoc import HeapDumpDoc
from du.android.hdump.SymbolResolver import SymbolResolver


logger = logging.getLogger(__name__.split('.')[-1])

class StackFrame:
    def __init__(self, address=0, library='', symbol=SymbolResolver.UNKOWN_SYMBOL):
        self.address = address
        self.library = library
        self.symbol = symbol

class Node:
    def __init__(self, frame=None):
        if not frame:
            frame = StackFrame()

        self.frame = frame
        self.children = {}

    def addStack(self, frameStack):
        if frameStack:
            frame = frameStack[0]

            if not frame.address in self.children:
                self.children[frame.address] = Node(frame)

            self.children[frame.address].addStack(frameStack[1:])

ProcessedStacks = namedtuple('ResolvedSymbols', 'zygoteStacks, appStacks, frameMap')

class HeapDump:
    def __init__(self, string, symbolResolver):
        self._doc = HeapDumpDoc(string)

        res = self._processStacks(self._doc, symbolResolver)

        self._zygoteTree = self._buildTree(res.zygoteStacks)
        self._appTree = self._buildTree(res.appStacks)

    @property
    def doc(self):
        return self._doc

    @classmethod
    def _buildTree(cls, frameStacks):
        logger.debug('building tree ..')
        rootNode = Node()
        for frameStack in frameStacks:
            rootNode.addStack(frameStack)
        return rootNode

    @classmethod
    def _processStacks(cls, doc, resolver):
        # Mapping of offsetAddress to Symbol
        stackFrameMap = {}

        logger.debug('resolving symbols ..')

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
                        if frameAddress in range(i.startAddress, i.endAddress):
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

            if record.zygoteChild:
                zygoteStacks.append(frameStack)
            else:
                appStacks.append(frameStack)

        return ProcessedStacks(zygoteStacks, appStacks, stackFrameMap)

    @property
    def zygoteRootNode(self):
        return self._zygoteTree

    @property
    def appRootNode(self):
        return self._appTree
