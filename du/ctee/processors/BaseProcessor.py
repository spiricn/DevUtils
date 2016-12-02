class BaseProcessor:
    def __init__(self):
        pass
    
    def transform(self, line):
        raise RuntimeError('Not implemented')
    