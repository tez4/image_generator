import os
import random
from PIL import Image


def create_image_grid(path, grid_size=(2, 2), cell_size=(200, 200), margin=5, output_name='auto', randomness=True):
    images = os.listdir(path)
    if randomness:
        random.shuffle(images)

    # Check if provided enough images
    if len(images) < grid_size[0] * grid_size[1]:
        raise ValueError("Not enough images provided for the grid size.")

    # Calculate the size of the output image
    width = grid_size[1] * (cell_size[0] + margin) + margin
    height = grid_size[0] * (cell_size[1] + margin) + margin

    # Create a blank (white) image with the calculated width and height
    grid_image = Image.new('RGB', (width, height), (255, 255, 255))

    # Place each image into the grid
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            img = Image.open(f"{path}{images[j * grid_size[0] + i]}")
            img = img.resize(cell_size, Image.BILINEAR)

            x_offset = j * (cell_size[0] + margin) + margin
            y_offset = i * (cell_size[1] + margin) + margin

            grid_image.paste(img, (x_offset, y_offset))

    if not os.path.exists('./output/grids/'):
        os.makedirs('./output/grids/')

    if output_name == 'auto':
        output_name = path.split("/")[-2]

    grid_image.save(f"./output/grids/{output_name}.jpg")

    return grid_image


# Example usage:
grid_image = create_image_grid(
    "./output/experiment_19/",
    grid_size=(2, 6),
    randomness=False
)
grid_image.show()
