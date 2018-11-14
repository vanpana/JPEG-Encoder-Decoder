position = 0


def normalize(pixel_value):
    if pixel_value > 255:
        pixel_value = 255
    if pixel_value < 0:
        pixel_value = 0
    return pixel_value
