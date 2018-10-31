from copy import deepcopy
from enum import Enum

from src.domain.exceptions.FormatNotSupportedException import FormatNotSupportedException
from src.domain.exceptions.InvalidSizeException import InvalidSizeException
from src.domain.exceptions.PixelFormatException import PixelFormatException
from src.domain.models.Block import Block
from src.domain.models.Pixels import PixelRGB, PixelYUV
from src.util.file_handler import write_lines_to_file, read_lines_from_file


class PixelType(Enum):
    RGB = 1
    YUV = 2


class ImageType(Enum):
    PPM = "P3"


class Image:
    def __init__(self, im_type, description, width, height, depth=255, pixels=None, pixel_type=None):
        if im_type == "P3":
            self.im_type = ImageType.PPM

        self.description = description
        self.width = width
        self.height = height
        self.depth = depth

        if pixels is None:
            pixels = []
        self.pixels = pixels
        self.pixel_type = pixel_type

    @staticmethod
    def load(filename: str):
        """
        Reads an image from a file. The type is set by the file extension.
        :param filename: The file where the image should be read from
        :return: None if file does not exist / Image with a type
        """

        # Get generator form file
        file_generator = read_lines_from_file(filename)

        # Check if file generator was created
        if file_generator is None:
            return None

        if filename.lower().endswith(".ppm"):
            # Get image type
            image_type = next(file_generator)

            # Get image description
            image_description = next(file_generator)

            # Get image size
            width, height = tuple(map(int, next(file_generator).split(' ')))

            # Get image depth
            depth = int(next(file_generator))

            # Construct rgb pixel list
            pixels = []
            for r_value in file_generator:
                g_value = next(file_generator)
                b_value = next(file_generator)
                pixels.append(PixelRGB(int(r_value), int(g_value), int(b_value)))

            # Construct and return image
            return Image(image_type, image_description, width, height, depth, pixels, PixelType.RGB)
        else:
            raise FormatNotSupportedException("Format .{0} is not yet supported :(".format(filename.split(".")[-1]))

    def save(self, filename: str):
        """
        Saves an image to the disk based on the image type.
        :param filename: The filename for the image to be saved.
        :return: None
        :raise: InvalidSizeException if actual pixels are less than the specified size
        :raise: PixelFormatException if pixel type is not suitable to image type
        """

        if len(self.pixels) != self.width * self.height:
            raise InvalidSizeException("Actual pixels are less than the specified size")

        if self.im_type == ImageType.PPM:
            # Specify PPM file format
            ppm_file_format = "{0}\n{1}\n{2}\n{3}\n{4}"

            if self.pixel_type != PixelType.RGB:
                raise PixelFormatException("Pixel type must be RGB")

            # Construct data string
            ppm_image = ppm_file_format.format(self.im_type.value,
                                               self.description,
                                               "{0} {1}".format(self.width, self.height),
                                               self.depth,
                                               ''.join(
                                                   ["{0}\n{1}\n{2}\n".format(pixel.r, pixel.g, pixel.b) for pixel in
                                                    self.pixels]))

            write_lines_to_file(ppm_image, filename, ".ppm")

    def convert_color_space(self, pixel_type):
        if pixel_type != self.pixel_type:
            self.pixel_type = pixel_type

            if self.pixel_type == PixelType.RGB:
                self.pixels = [pixel.get_pixel_rgb() for pixel in self.pixels]
            elif self.pixel_type == PixelType.YUV:
                self.pixels = [pixel.get_pixel_yuv() for pixel in self.pixels]

    def split_into_blocks(self):
        if self.pixel_type == PixelType.YUV:
            # Construct Y blocks
            y_blocks = []
            pos = 0
            for line in range(0, self.height, 8):
                for col in range(0, self.width, 8):
                    y_blocks.append(
                        Block([self.pixels[self.width * i + j].y for i in range(line, line + 8) for j in
                               range(col, col + 8)], pos))
                pos += 1

            # Construct U blocks
            u_blocks = []
            pos = 0
            for line in range(0, self.height, 8):
                for col in range(0, self.width, 8):
                    u_blocks.append(
                        Block([self.pixels[self.width * i + j].u for i in range(line, line + 8) for j in
                               range(col, col + 8)], pos))
                pos += 1

            for i in range(0, len(u_blocks)):
                u_blocks[i].shrink()

            # Construct V blocks
            v_blocks = []
            pos = 0
            for line in range(0, self.height, 8):
                for col in range(0, self.width, 8):
                    v_blocks.append(
                        Block([self.pixels[self.width * i + j].v for i in range(line, line + 8) for j in
                               range(col, col + 8)], pos))
                pos += 1

            for i in range(0, len(v_blocks)):
                v_blocks[i].shrink()

            return y_blocks, u_blocks, v_blocks
        else:
            raise FormatNotSupportedException("Can't yet split into RGB blocks")

    @staticmethod
    def construct_from_blocks(blocks):
        y_blocks = deepcopy(blocks[0])
        u_blocks = deepcopy(blocks[1])
        v_blocks = deepcopy(blocks[2])

        # Grow U blocks
        for i in range(0, len(u_blocks)):
            u_blocks[i].grow()

        # Grow Y blocks
        for i in range(0, len(v_blocks)):
            v_blocks[i].grow()

        # Build pixels
        pixels = [PixelYUV(y_blocks[i].items[j], u_blocks[i].items[j], v_blocks[i].items[j]) for i in
                  range(0, len(y_blocks)) for j in range(0, len(y_blocks[i].items))]

        # Return image TODO Lol calculate w, h
        return Image("P3", "# Description", 800, 600, 255, pixels, PixelType.YUV)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{0} image, {1} x {2}, {3} actual pixels".format(self.im_type, self.width, self.height, len(self.pixels))
