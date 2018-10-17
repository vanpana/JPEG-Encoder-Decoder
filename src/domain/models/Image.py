class Image:
    def __init__(self, im_type, description, width, height, depth, pixels=None):
        self.im_type = im_type
        self.description = description
        self.width = width
        self.height = height
        self.depth = depth

        if pixels is None:
            pixels = []
        self.pixels = pixels

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{0} image, {1} x {2}, {3} actual pixels".format(self.im_type, self.width, self.height, len(self.pixels))
