from src.domain.models.Image import Image, PixelType, DCTImage, QuantizationImage

if __name__ == '__main__':
    ppm_filename = "../data/in.ppm"
    ppm_save_filename = "../data/out."
    ppm_blocks_save_filename = "../data/out_b."

    # Encoder
    print("Loading image...")
    image = Image.load(ppm_filename)

    print("Converting to YUV...")
    image.convert_color_space(PixelType.YUV)

    print("Splitting into blocks")
    yb, ub, vb = image.split_into_blocks()

    print("Getting entropy")
    yb[0].get_entropy()
    # print("fDCT")
    # dct_image = DCTImage(yb, ub, vb)
    #
    # print("Quantization")
    # quantization_image = QuantizationImage(dct_image)
    #
    # # Decoder
    # print("Dequantizing image")
    # quantization_image.dequantize()
    #
    # print("iDCT")
    # yb, ub, vb = DCTImage.inverse_dct(quantization_image)
    #
    # print("Building back image")
    # new_img = Image.construct_from_blocks([yb, ub, vb], width=image.width, height=image.height)
    #
    # print("Converting to RGB...")
    # image.convert_color_space(PixelType.RGB)
    # new_img.convert_color_space(PixelType.RGB)
    #
    # print("Saving image...")
    # image.save(ppm_save_filename)
    # new_img.save(ppm_blocks_save_filename)
    #
    # print("Task done...")
