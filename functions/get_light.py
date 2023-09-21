import numpy as np
from PIL import Image

pic_1 = Image.open("./output/experiment_48/0__1.png")
pic_2 = Image.open("./output/experiment_48/0__11.png")
pic_1_array = np.array(pic_1).astype('float64')
pic_2_array = np.array(pic_2).astype('float64')
new_array = (pic_2_array - pic_1_array + 255) / 2
new_array = new_array[:, :, :3].astype(np.uint8)
new_image = Image.fromarray(np.uint8(new_array))
new_image.save("./output/experiment_48/0__111.png")
new_image.show()
