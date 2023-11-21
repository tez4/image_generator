import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from copy import deepcopy


def create_white_background(
        experiment_name, object_number, mask_image_number, image_number, new_image_number, background_change,
        shadow_contrast_multiplier, object_contrast_multiplier):

    pic_1 = Image.open(f"./output/{experiment_name}/{object_number}__{mask_image_number}.png")
    pic_2 = Image.open(f"./output/{experiment_name}/{object_number}__{image_number}.png")
    pic_1 = pic_1.resize(pic_2.size)

    pic_1_array = np.array(pic_1).astype('float64')
    pic_2_array = np.array(pic_2).astype('float64')

    mask_array = pic_1_array / 230
    mask_array[mask_array > 1] = 1

    new_object = deepcopy(pic_2_array)
    new_object *= object_contrast_multiplier
    new_object[new_object > 255] = 255

    new_background = deepcopy(pic_2_array)
    new_background += background_change
    new_background[new_background >= 255] = 255
    new_background -= 255
    new_background *= shadow_contrast_multiplier
    new_background += 255
    new_background[new_background < 0] = 0

    new_array = mask_array * new_background + (1 - mask_array) * new_object
    new_image = Image.fromarray(np.uint8(new_array))
    new_image.save(f"./output/{experiment_name}/{object_number}__{new_image_number}.png")
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
    # loop over all images in the folder
    experiment = 'experiment_82'
    folder = f'./output/{experiment}'

    object_numbers = []
    for file in os.listdir(folder):
        if file.endswith(".json"):
            object_number = file.split('__')[0]
            object_numbers.append(object_number)

    for object_number in object_numbers:
        create_white_background(experiment, object_number, 4, 8, 12, 35, 1, 1)
        create_white_background(experiment, object_number, 4, 10, 13, 55, 1.6, 1.15)
        create_white_background(experiment, object_number, 4, 11, 14, 85, 1.4, 1.2)
