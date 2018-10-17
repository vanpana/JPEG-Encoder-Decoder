from src.domain.models.Image import Image

if __name__ == '__main__':
    ppm_filename = "../data/in.ppm"
    ppm_save_filename = "../data/out."

    print("Loading image...")
    image = Image.load(ppm_filename)

    print("Saving image...")
    image.save(ppm_save_filename)

    print("Task done...")
