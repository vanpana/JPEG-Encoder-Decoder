import os

from src.domain.models.Image import Image
from src.domain.models.PixelRGB import PixelRGB


def read_lines_from_file(filename):
    """
    Yields all lines from a file. Lines are stripped from line breaks and empty spaces.
    :param filename: Path to the file
    :return None if file was not found
    """
    if not os.path.isfile(filename):
        return None
    with open(filename, 'r') as file:
        for line in file:
            yield line.strip('\n').strip(' ')


def read_ppm_image(filename):
    """
    Reads a PPM file and returns an image object containing that data
    :param filename: Path to the image file
    :return: Image object containing PPM data / None if image file not existent
    """
    # Get generator form file
    file_generator = read_lines_from_file(filename)

    # Check if file generator was created
    if file_generator is None:
        return None

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
    return Image(image_type, image_description, width, height, depth, pixels)
