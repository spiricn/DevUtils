class Color:
    RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE, BLACK, UNSPECIFIED = range(9)

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
