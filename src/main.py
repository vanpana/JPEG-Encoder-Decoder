from src.domain.models.Image import Image, PixelType

if __name__ == '__main__':
    ppm_filename = "../data/in.ppm"
    ppm_save_filename = "../data/out."

    print("Loading image...")
    image = Image.load(ppm_filename)

    print("Converting to YUV...")
    image.convert_color_space(PixelType.YUV)
    print(image.pixel_type)

    print("Converting to RGB...")
    image.convert_color_space(PixelType.RGB)
    print(image.pixel_type)

    print("Saving image...")
    image.save(ppm_save_filename)

    print("Task done...")
