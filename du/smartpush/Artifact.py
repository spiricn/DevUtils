class Artifact(object):
    def __init__(self, artifactType, source=None, destination=None, checkDifference=None, install=True, opts={}):
        self._type = artifactType
        self._source = source
        self._destination = destination
        self._checkDifference = checkDifference
        self._opts = opts
        self._install = install

    @property
    def type(self):
        return self._type

    @property
    def source(self):
        return self._source

    @property
    def destination(self):
        return self._destination

    @property
    def checkDifference(self):
        return self._checkDifference

    @property
    def install(self):
        return self._install

    @property
    def opts(self):
        return self._opts