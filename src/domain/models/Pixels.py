import math


class PixelRGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def get_pixel_yuv(self):
        y = 0.299 * self.r + 0.587 * self.g + 0.114 * self.b
        u = 128 - 0.1687 * self.r - 0.3312 * self.g + 0.5 * self.b
        v = 128 + 0.5 * self.r - 0.4186 * self.g - 0.0813 * self.b
        return PixelYUV(y, u, v)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "RGB({0}, {1}, {2})".format(self.r, self.g, self.b)


class PixelYUV:
    def __init__(self, y, u, v):
        self.y = y
        self.u = u
        self.v = v

    def get_pixel_rgb(self):
        r = self.y + 1.402 * (self.v - 128)
        g = self.y - 0.344136 * (self.u - 128) - 0.714136 * (self.v - 128)
        b = self.y + 0.1772 * (self.u - 128)
        return PixelRGB(math.trunc(r), math.trunc(g), math.trunc(b))

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "YUV({0}, {1}, {2})".format(self.y, self.u, self.v)
