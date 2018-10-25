from src.domain.models.Image import Image, PixelType

if __name__ == '__main__':
    ppm_filename = "../data/in.ppm"
    ppm_save_filename = "../data/out."

    print("Loading image...")
    image = Image.load(ppm_filename)

    print("Converting to YUV...")
    image.convert_color_space(PixelType.YUV)

    print("Splitting into blocks")
    yb, ub, vb = image.split_into_blocks()

    print("Building back image")
    new_img = Image.construct_from_blocks([yb, ub, vb])

    print("Converting to RGB...")
    new_img.convert_color_space(PixelType.RGB)

    print("Saving image...")
    new_img.save(ppm_save_filename)

    print("Task done...")
