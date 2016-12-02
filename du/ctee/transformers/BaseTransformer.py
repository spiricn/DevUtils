class BaseTransformer:
    def __init__(self):
        pass
    
    def getHeader(self):
        return ''
    
    def getTrailer(self):
        return ''
    
    def transform(self, line, style):
        raise RuntimeError('Not implemented')