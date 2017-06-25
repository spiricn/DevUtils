class BaseRenderer:
    def __init__(self):
        pass

    def render(self, stream, obj):
        raise NotImplementedError()
