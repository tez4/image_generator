import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from copy import deepcopy


def create_white_background():
    pic_1 = Image.open("./output/experiment_76/0__4.png")
    pic_2 = Image.open("./output/experiment_76/0__5.png")
    pic_1_array = np.array(pic_1).astype('float64')
    pic_2_array = np.array(pic_2).astype('float64')
    binary_array = (pic_1_array < 125).astype(int)
    new_object = deepcopy(pic_2_array)
    new_object[binary_array == 0] = 255
    new_background = deepcopy(pic_2_array)
    new_background[binary_array == 1] = 255
    new_background += 60
    new_background[new_background >= 255] = 255
    new_background -= 255
    new_background *= 2
    new_background += 255
    new_array = np.minimum(new_object, new_background)
    new_image = Image.fromarray(np.uint8(new_array))
    new_image.save("./output/experiment_76/0__12.png")
    # new_image.show()


def create_histogram(image):
    image_gray = image.convert('L')
    image_array = np.array(image_gray)
    pixel_array = image_array.flatten()
    histogram_array = np.bincount(pixel_array, minlength=256)

    plt.bar(range(256), histogram_array, color='black')
    plt.title('Histogram')
    plt.xlabel('Pixel value')
    plt.ylabel('Frequency')
    plt.yticks([])
    plt.show()


def get_image_from_array(array):
    if len(array.shape) == 3:
        image = Image.fromarray(array.astype(np.uint8))
    elif len(array.shape) == 2:
        image = Image.fromarray(array[:, :, 3].astype(np.uint8))
    else:
        raise ValueError("Array shape not supported")

    return image


if __name__ == "__main__":
    create_white_background()
