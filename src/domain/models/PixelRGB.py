class PixelRGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "RGB({0}, {1}, {2})".format(self.r, self.g, self.b)
