class DiffNode:
    TYPE_ADDED, \
    TYPE_REMOVED, \
    TYPE_EQUAL, \
    TYPE_CHANGED = range(4)

    def __init__(self, oldNode, newNode):
        self._oldNode = oldNode
        self._newNode = newNode

        self._children = []

    @property
    def children(self):
        return [ i for i in self._children]

    def findChild(self, address):
        for child in self._children:
            if child.node.frame.address == address:
                return child
        return None

    @property
    def frame(self):
        node = self._oldNode if self._oldNode else self._newNode

        return node.frame

    @property
    def size(self):
        if self.type == self.TYPE_ADDED:
            return self._newNode.size
        elif self.type in [self.TYPE_REMOVED, self.TYPE_EQUAL]:
            return self._oldNode.size
        else:
            return self._newNode.size - self._oldNode.size

    @property
    def type(self):
        if self._oldNode and self._newNode:
            if self._oldNode.size == self._newNode.size:
                return self.TYPE_EQUAL
            else:
                return self.TYPE_CHANGED

        elif self._oldNode:
            return self.TYPE_REMOVED
        else:
            return self.TYPE_ADDED

    @property
    def oldNode(self):
        return self._oldNode

    @property
    def newNode(self):
        return self._newNode

    def addChild(self, child):
        self._children.append(child)

class HeapDumpDiff:
    def __init__(self, heap1, heap2):
        self._heap1 = heap1
        self._heap2 = heap2

        self._appTree = self._createTrees(None, self._heap1.appRootNode, self._heap2.appRootNode)
        self._zygoteTree = self._createTrees(None, self._heap1.zygoteRootNode, self._heap2.zygoteRootNode)

    def _createTrees(self, parentNode, oldTree, newTree):
        diffNode = DiffNode(oldTree, newTree)

        if parentNode:
            parentNode.addChild(diffNode)

        if oldTree:
            for oldChild in oldTree.children:
                newChild = None
                if newTree:
                    newChild = newTree.findChild(oldChild.frame.address)

                self._createTrees(diffNode, oldChild, newChild)

        if newTree:
            for newChild in newTree.children:
                oldChild = None
                if oldTree:
                    oldChild = oldTree.findChild(newChild.frame.address)

                if not oldChild:
                    self._createTrees(diffNode, oldChild, newChild)

        return diffNode

    @property
    def zygoteRootNode(self):
        return self._zygoteTree

    @property
    def appRootNode(self):
        return self._appTree
