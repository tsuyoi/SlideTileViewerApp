import numpy as np
import os

from skimage.io import imread, imsave

images_path = 'images/'
source_data_path = os.path.join(images_path, 'source')
train_data_path = os.path.join(images_path, 'train')

image_width = 256
image_height = 256

def create_training_data():
    images = os.listdir()