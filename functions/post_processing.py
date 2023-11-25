import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path
from copy import deepcopy


def create_white_background(
        input_folder, output_folder, object_number, mask_image_number, image_number, new_image_name,
        background_change, shadow_contrast_multiplier, object_contrast_multiplier):

    pic_1 = Image.open(f"{input_folder}/{object_number}__{mask_image_number}.png")
    pic_2 = Image.open(f"{input_folder}/{object_number}__{image_number}.png")
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
    new_image = Image.fromarray(np.uint8(new_array)).convert('RGB')
    new_image.save(f"{output_folder}/{new_image_name}.png")
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


def create_folder(folder_path, remove_content):
    directory = Path(folder_path)
    if directory.exists() and directory.is_dir():
        if remove_content:
            shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)


def copy_image(
        input_folder, output_folder, object_number, image_number, new_image_name, is_grayscale=False, new_size=None):

    image = Image.open(f"{input_folder}/{object_number}__{image_number}.png")
    if new_size is not None:
        image = image.resize(new_size)
    if is_grayscale:
        image = image.convert('L')
    else:
        image = image.convert('RGB')

    image.save(f"{output_folder}/{new_image_name}.png")


if __name__ == "__main__":
    experiment = 'experiment_95'
    folder = f'./output/{experiment}'

    object_numbers = []
    for file in os.listdir(folder):
        if file.endswith(".json"):
            object_number = file.split('__')[0]
            object_numbers.append(object_number)

    create_folder(f'{folder}_preprocessed', remove_content=True)

    for i, object_number in enumerate(object_numbers):
        if i <= int(len(object_numbers) / 10):
            new_folder = f'{folder}_preprocessed/test/{i}'
        elif i <= int(len(object_numbers) / 10 * 3):
            new_folder = f'{folder}_preprocessed/validation/{i}'
        else:
            new_folder = f'{folder}_preprocessed/training/{i}'

        create_folder(new_folder, remove_content=True)
        copy_image(folder, new_folder, object_number, 1, 'input')
        copy_image(folder, new_folder, object_number, 2, 'normals')
        copy_image(folder, new_folder, object_number, 3, 'distance', is_grayscale=True)
        copy_image(folder, new_folder, object_number, 4, 'mask', is_grayscale=True, new_size=(1024, 1024))
        create_white_background(folder, new_folder, object_number, 4, 11, 'output_1', 85, 1.4, 1.2)
        create_white_background(folder, new_folder, object_number, 4, 10, 'output_2', 55, 1.6, 1.15)
        create_white_background(folder, new_folder, object_number, 4, 8, 'output_3', 35, 1, 1)
        shutil.copy(f'{folder}/{object_number}__0.json', f'{new_folder}/metadata.json')
