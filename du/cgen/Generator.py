from collections import namedtuple


TYPE_STRING, \
TYPE_INT32, \
TYPE_BOOL = range(3)

Param = namedtuple('Param', 'type, name, value')

class Generator:
    def __init__(self, params):
        self._params = params

    def generate(self):
        raise NotImplementedError()

    @property
    def params(self):
        return self._params
