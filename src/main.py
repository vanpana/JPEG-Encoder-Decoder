from src.util.file_handler import read_ppm_image

if __name__ == '__main__':
    ppm_filename = "../data/in.ppm"

    image = read_ppm_image(ppm_filename)

    print(image)