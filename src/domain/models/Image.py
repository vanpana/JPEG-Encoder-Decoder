import math
from copy import deepcopy
from enum import Enum
from math import sqrt

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
            for line in range(0, self.height, 8):
                for col in range(0, self.width, 8):
                    y_blocks.append(
                        Block([[self.pixels[i][j].y for i in range(line, line + 8)] for j in
                               range(col, col + 8)], Global.position))

            # Construct U blocks
            u_blocks = []
            Global.position = 0
            for line in range(0, self.height, 8):
                for col in range(0, self.width, 8):
                    u_blocks.append(
                        Block([[self.pixels[i][j].u for i in range(line, line + 8)] for j in
                               range(col, col + 8)], Global.position))

            for i in range(0, len(u_blocks)):
                u_blocks[i].shrink()

            # Construct V blocks
            v_blocks = []
            Global.position = 0
            for line in range(0, self.height, 8):
                for col in range(0, self.width, 8):
                    v_blocks.append(
                        Block([[self.pixels[i][j].v for i in range(line, line + 8)] for j in
                               range(col, col + 8)], Global.position))

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
            if u_blocks[i].block_size != 8:
                u_blocks[i].grow()

        # Grow Y blocks
        for i in range(0, len(v_blocks)):
            if v_blocks[i].block_size != 8:
                v_blocks[i].grow()

        # Build pixels
        total_blocks = len(y_blocks)
        block_size = v_blocks[0].block_size
        pixels = [[0 for _ in range(0, width)] for _ in range(0, height)]
        step = width // block_size
        for block_no in range(0, total_blocks):
            starting_j = (y_blocks[block_no].position_in_image // step) * block_size
            starting_i = (y_blocks[block_no].position_in_image % step) * block_size

            for i in range(0, block_size):
                for j in range(0, block_size):
                    pixel = PixelYUV(y_blocks[block_no].items[i][j],
                                     u_blocks[block_no].items[i][j],
                                     v_blocks[block_no].items[i][j])
                    pixel_i = starting_i + i
                    pixel_j = starting_j + j

                    pixels[pixel_j][pixel_i] = pixel
                    # for block_i in range(0, len(y_blocks), step):  # For the blocks forming a 800x8
        #     for block_j in range(block_i, block_i + step):  # For the blocks in that line
        #         for i in range(0, block_size):  # For going through the current block_no
        #             for j in range(0, block_size):
        #                 pixel = PixelYUV(y_blocks[block_j].items[i][j],
        #                                  u_blocks[block_j].items[i][j],
        #                                  v_blocks[block_j].items[i][j])
        #                 pixels[block_i + i][block_j + block_size * j] = pixel

        # Return image
        return Image("P3", "# Description", width, height, depth, pixels, PixelType.YUV)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{0} image, {1} x {2}, {3} actual pixels".format(self.im_type, self.width, self.height,
                                                                len(self.pixels) * len(self.pixels[0]))


class DCTImage:
    sqrt2 = sqrt(2)

    def __init__(self, y_blocks, u_blocks, v_blocks, must_build=True):
        Global.position = 0
        if must_build:
            # Blocks are tuples of (y/cb/cr)
            self.dct_blocks = [DCTImage.block_to_dct(y_blocks[i], u_blocks[i], v_blocks[i]) for i in
                               range(len(y_blocks))]
        else:
            self.dct_blocks = [(y_blocks[i], u_blocks[i], v_blocks[i]) for i in range(0, len(y_blocks))]

    @staticmethod
    def a(u):
        if u > 0:
            return 1
        return 1 / DCTImage.sqrt2

    # <editor-fold desc="Block to dct">
    @staticmethod
    def block_to_dct(y_block: Block, u_block: Block, v_block: Block):
        y_block = deepcopy(y_block)
        u_block = deepcopy(u_block)
        v_block = deepcopy(v_block)

        y_block.subtract_from_values(128)

        u_block.grow()
        u_block.subtract_from_values(128)

        v_block.grow()
        v_block.subtract_from_values(128)

        block_size = y_block.block_size

        y_dct_block = Block([[0 for _ in range(0, block_size)] for _ in range(0, block_size)], Global.position)
        u_dct_block = Block([[0 for _ in range(0, block_size)] for _ in range(0, block_size)], Global.position)
        v_dct_block = Block([[0 for _ in range(0, block_size)] for _ in range(0, block_size)], Global.position)

        for u in range(0, block_size):
            for v in range(0, block_size):
                base_value = 1 / 4 * DCTImage.a(u) * DCTImage.a(v)
                y_dct_block.items[u][v] = base_value * DCTImage.outer_sum_to_dct(y_block, u, v, block_size)
                u_dct_block.items[u][v] = base_value * DCTImage.outer_sum_to_dct(u_block, u, v, block_size)
                v_dct_block.items[u][v] = base_value * DCTImage.outer_sum_to_dct(v_block, u, v, block_size)
        return y_dct_block, u_dct_block, v_dct_block

    @staticmethod
    def outer_sum_to_dct(block: Block, u, v, block_size=8):
        total = 0.0
        for x in range(0, block_size):
            total += DCTImage.inner_sum_to_dct(block, u, v, x, block_size)
        return total

    @staticmethod
    def inner_sum_to_dct(block: Block, u, v, x, block_size=8):
        total = 0.0
        for y in range(0, block_size):
            total += DCTImage.product_dct(block.items[x][y], x, y, u, v)
        return total

    @staticmethod
    def product_dct(block_value, x, y, u, v):
        u_val = ((2 * x + 1) * u * math.pi) / 16
        v_val = ((2 * y + 1) * v * math.pi) / 16
        return block_value * math.cos(u_val) * math.cos(v_val)

    # </editor-fold>

    @staticmethod
    def inverse_dct(quantization_image):
        y_blocks = []
        u_blocks = []
        v_blocks = []

        y_q_blocks = [block[0] for block in quantization_image.blocks]
        u_q_blocks = [block[1] for block in quantization_image.blocks]
        v_q_blocks = [block[2] for block in quantization_image.blocks]

        for block_no in range(0, len(y_q_blocks)):
            result = DCTImage.inverse_dct_per_block(y_q_blocks[block_no], u_q_blocks[block_no], v_q_blocks[block_no])

            y_blocks.append(result[0])
            u_blocks.append(result[1])
            v_blocks.append(result[2])

        for i in range(0, len(y_q_blocks)):
            y_blocks[i].add_to_values()
            y_blocks[i].position_in_image = i
            u_blocks[i].add_to_values()
            u_blocks[i].position_in_image = i
            v_blocks[i].add_to_values()
            v_blocks[i].position_in_image = i

        return y_blocks, u_blocks, v_blocks

    @staticmethod
    def inverse_dct_per_block(y_q_block: Block, u_q_block: Block, v_q_block: Block):
        block_size = y_q_block.block_size

        y_dct_block = Block([[0 for _ in range(0, block_size)] for _ in range(0, block_size)], Global.position)
        u_dct_block = Block([[0 for _ in range(0, block_size)] for _ in range(0, block_size)], Global.position)
        v_dct_block = Block([[0 for _ in range(0, block_size)] for _ in range(0, block_size)], Global.position)

        for x in range(0, block_size):
            for y in range(0, block_size):
                base_value = 1 / 4
                y_dct_block.items[x][y] = base_value * DCTImage.outer_sum_from_dct(y_q_block, x, y, block_size)
                u_dct_block.items[x][y] = base_value * DCTImage.outer_sum_from_dct(u_q_block, x, y, block_size)
                v_dct_block.items[x][y] = base_value * DCTImage.outer_sum_from_dct(v_q_block, x, y, block_size)

        return y_dct_block, u_dct_block, v_dct_block

    @staticmethod
    def outer_sum_from_dct(block: Block, x, y, block_size=8):
        total = 0.0
        for u in range(0, block_size):
            total += DCTImage.inner_sum_from_dct(block, x, y, u, block_size)
        return total

    @staticmethod
    def inner_sum_from_dct(block: Block, x, y, u, block_size=8):
        total = 0.0
        for v in range(0, block_size):
            total += DCTImage.a(u) * DCTImage.a(v) * DCTImage.product_dct(block.items[u][v], x, y, u, v)
        return total


class QuantizationImage:
    def __init__(self, dct_image: DCTImage):
        self.blocks = deepcopy(dct_image.dct_blocks)  # Blocks are tuples of (y/cb/cr)
        self.quantize()
        self.entropy_blocks = None

    def quantize(self):
        for i in range(0, len(self.blocks)):
            for m in range(0, 8):
                for n in range(0, 8):
                    for k in range(0, 3):
                        self.blocks[i][k].items[m][n] //= self.get_quantization_matrix()[m][n]

    def entropy_encoding(self):
        self.entropy_blocks = []
        for i in range(0, len(self.blocks)):
            self.entropy_blocks.append((self.blocks[i][0].get_entropy(),
                                        self.blocks[i][1].get_entropy(),
                                        self.blocks[i][2].get_entropy()))

    def entropy_decoding(self):
        if self.entropy_blocks is None:
            raise KeyError('Entropy hasn\'t ran yet')

        for i in range(0, len(self.entropy_blocks)):
            self.blocks[i] = (Block.get_from_entropy(self.entropy_blocks[i][0]),
                              Block.get_from_entropy(self.entropy_blocks[i][1]),
                              Block.get_from_entropy(self.entropy_blocks[i][2]))

    def dequantize(self):
        for i in range(0, len(self.blocks)):
            for m in range(0, 8):
                for n in range(0, 8):
                    for k in range(0, 3):
                        self.blocks[i][k].items[m][n] *= self.get_quantization_matrix()[m][n]

    def get_quantization_matrix(self):
        return \
            [
                [6, 4, 4, 6, 10, 16, 20, 24],
                [5, 5, 6, 8, 10, 23, 24, 22],
                [6, 5, 6, 10, 16, 23, 28, 22],
                [6, 7, 9, 12, 20, 35, 32, 25],
                [7, 9, 15, 22, 27, 44, 41, 31],
                [10, 14, 22, 26, 32, 42, 45, 37],
                [20, 26, 31, 35, 41, 48, 48, 40],
                [29, 37, 38, 39, 45, 40, 41, 40]
            ]
