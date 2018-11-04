from copy import deepcopy
from enum import Enum

from src.domain.exceptions.FormatNotSupportedException import FormatNotSupportedException
from src.domain.exceptions.InvalidSizeException import InvalidSizeException
from src.domain.exceptions.PixelFormatException import PixelFormatException
from src.domain.models import Block
from src.domain.models.Block import Block
from src.domain.models.Pixels import PixelRGB, PixelYUV
from src.util import Global
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
            pixels = [[] for _ in range(0, width) for _ in range(0, height)]

        try:
            _ = pixels[0][0]
            self.pixels = deepcopy(pixels)
        except Exception as e:
            self.pixels = [[pixels[i + j * self.width] for i in range(0, width)] for j in range(0, height)]
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

        if len(self.pixels) * len(self.pixels[0]) != self.width * self.height:
            raise InvalidSizeException("Actual pixels are less than the specified size")

        if self.im_type == ImageType.PPM:
            # Specify PPM file format
            ppm_file_format = "{0}\n{1}\n{2}\n{3}\n{4}"

            if self.pixel_type != PixelType.RGB:
                raise PixelFormatException("Pixel type must be RGB")

            image_string = ""
            for line in self.pixels:
                for pixel in line:
                    image_string += "{0}\n{1}\n{2}\n".format(pixel.r, pixel.g, pixel.b)

            # Construct data string
            ppm_image = ppm_file_format.format(self.im_type.value,
                                               self.description,
                                               "{0} {1}".format(self.width, self.height),
                                               self.depth,
                                               image_string)

            write_lines_to_file(ppm_image, filename, ".ppm")

    def convert_color_space(self, pixel_type):
        if pixel_type != self.pixel_type:
            self.pixel_type = pixel_type

            if self.pixel_type == PixelType.RGB:
                self.pixels = [[pixel.get_pixel_rgb() for pixel in line] for line in self.pixels]
            elif self.pixel_type == PixelType.YUV:
                self.pixels = [[pixel.get_pixel_yuv() for pixel in line] for line in self.pixels]

    def split_into_blocks(self):
        if self.pixel_type == PixelType.YUV:
            # Construct Y blocks
            y_blocks = []
            Global.position = 0
            for col in range(0, self.width, 8):
                for line in range(0, self.height, 8):
                    y_blocks.append(
                        Block([[self.pixels[j][i].y for i in range(col, col + 8)] for j in
                               range(line, line + 8)], Global.position))

            # Construct U blocks
            u_blocks = []
            Global.position = 0
            for col in range(0, self.width, 8):
                for line in range(0, self.height, 8):
                    u_blocks.append(
                        Block([[self.pixels[j][i].u for i in range(col, col + 8)] for j in
                               range(line, line + 8)], Global.position))

            for i in range(0, len(u_blocks)):
                u_blocks[i].shrink()

            # Construct V blocks
            v_blocks = []
            Global.position = 0
            for col in range(0, self.width, 8):
                for line in range(0, self.height, 8):
                    v_blocks.append(
                        Block([[self.pixels[j][i].v for i in range(col, col + 8)] for j in
                               range(line, line + 8)], Global.position))

            for i in range(0, len(v_blocks)):
                v_blocks[i].shrink()

            return y_blocks, u_blocks, v_blocks
        else:
            raise FormatNotSupportedException("Can't yet split into RGB blocks")

    @staticmethod
    def construct_from_blocks(blocks, width=800, height=600, depth=255):
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
        total_blocks = len(y_blocks)
        block_size = v_blocks[0].block_size
        pixels = [[0 for _ in range(0, width)] for _ in range(0, height)]
        step = width // block_size
        for block_no in range(0, total_blocks):
            starting_i = (y_blocks[block_no].position_in_image // step) * block_size
            starting_j = (y_blocks[block_no].position_in_image % step) * block_size

            for i in range(0, block_size):
                for j in range(0, block_size):
                    pixel = PixelYUV(y_blocks[block_no].items[i][j],
                                     u_blocks[block_no].items[i][j],
                                     v_blocks[block_no].items[i][j])

                    pixels[starting_i + i][starting_j + j] = pixel
                    # for block_i in range(0, len(y_blocks), step):  # For the blocks forming a 800x8
        #     for block_j in range(block_i, block_i + step):  # For the blocks in that line
        #         for i in range(0, block_size):  # For going through the current block_no
        #             for j in range(0, block_size):
        #                 pixel = PixelYUV(y_blocks[block_j].items[i][j],
        #                                  u_blocks[block_j].items[i][j],
        #                                  v_blocks[block_j].items[i][j])
        #                 pixels[block_i + i][block_j + block_size * j] = pixel

        # Return image TODO Lol calculate w, h
        return Image("P3", "# Description", width, height, depth, pixels, PixelType.YUV)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{0} image, {1} x {2}, {3} actual pixels".format(self.im_type, self.width, self.height, len(self.pixels))
