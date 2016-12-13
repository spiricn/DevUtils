from du.ctee.transformers.BaseTransformer import BaseTransformer


class PasstroughTransformer(BaseTransformer):
    def __init__(self):
        BaseTransformer.__init__(self)

    def transform(self, line, style):
        return line
