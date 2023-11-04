# -*- coding: utf-8 -*-
"""Image- Segmentation-on -Oxford.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-ATEgh5hPofsP1B_02-vzOrEGuGhmD8H
"""

from google.colab import drive
drive.mount('/content/drive')

file_paths = ['/content/drive/MyDrive/images', '/content/drive/MyDrive/trimaps']

import os

input_dir = '/content/drive/MyDrive/images'
target_dir = '/content/drive/MyDrive/trimaps'

# Check if the directories exist
if not os.path.exists(input_dir) or not os.path.exists(target_dir):
    print("Input or target directory does not exist.")
else:
    input_img_paths = sorted(
        [os.path.join(input_dir, fname)
         for fname in os.listdir(input_dir)
         if fname.endswith(".jpg")])
    target_paths = sorted(
        [os.path.join(target_dir, fname)
         for fname in os.listdir(target_dir)
         if fname.endswith(".png") and not fname.startswith(".")])

    print("Number of samples:", len(input_img_paths))

import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import load_img, img_to_array

plt.axis("off")
plt.imshow(load_img(input_img_paths[4]))

def display_target(target_array):
    normalized_array = (target_array.astype("uint8") - 1) * 127
    plt.axis("off")
    plt.imshow(normalized_array[:, :, 0])

img = img_to_array(load_img(target_paths[4], color_mode="grayscale"))
display_target(img)

import numpy as np
import random

img_size = (200, 200)
num_imgs = len(input_img_paths)

random.Random(1337).shuffle(input_img_paths)
random.Random(1337).shuffle(target_paths)

def path_to_input_image(path):
    return img_to_array(load_img(path, target_size=img_size))

def path_to_target(path):
    img = img_to_array(
        load_img(path, target_size=img_size, color_mode="grayscale"))
    img = img.astype("uint8") - 1
    return img

input_imgs = np.zeros((num_imgs,) + img_size + (3,), dtype="float32")
targets = np.zeros((num_imgs,) + img_size + (1,), dtype="uint8")
for i in range(num_imgs):
    input_imgs[i] = path_to_input_image(input_img_paths[i])
    targets[i] = path_to_target(target_paths[i])

num_val_samples = 1000
train_input_imgs = input_imgs[:-num_val_samples]
train_targets = targets[:-num_val_samples]
val_input_imgs = input_imgs[-num_val_samples:]
val_targets = targets[-num_val_samples:]

from tensorflow import keras
from keras import layers

num_classes=3

model = keras.Sequential([
    layers.experimental.preprocessing.Rescaling(1./255, input_shape=img_size + (3,)),
    layers.Conv2D(64, 3, strides=2, activation="relu", padding="same"),
    layers.Conv2D(64, 3, activation="relu", padding="same"),
    layers.Conv2D(128, 3, strides=2, activation="relu", padding="same"),
    layers.Conv2D(128, 3, activation="relu", padding="same"),
    layers.Conv2D(256, 3, strides=2, padding="same", activation="relu"),
    layers.Conv2D(256, 3, activation="relu", padding="same"),

    layers.Conv2DTranspose(256, 3, activation="relu", padding="same"),
    layers.Conv2DTranspose(256, 3, activation="relu", padding="same", strides=2),
    layers.Conv2DTranspose(128, 3, activation="relu", padding="same"),
    layers.Conv2DTranspose(128, 3, activation="relu", padding="same", strides=2),
    layers.Conv2DTranspose(64, 3, activation="relu", padding="same"),
    layers.Conv2DTranspose(64, 3, activation="relu", padding="same", strides=2),

    layers.Conv2D(num_classes, 3, activation="softmax", padding="same")
    ]
)

model.summary()

model.compile(optimizer="rmsprop", loss="sparse_categorical_crossentropy", metrics=['accuracy'])

callbacks = [keras.callbacks.ModelCheckpoint("oxford_segmentation.keras",save_best_only=True)]

history = model.fit(train_input_imgs, train_targets,
                    epochs=5,
                    callbacks=callbacks,
                    batch_size=64,
                    validation_data=(val_input_imgs, val_targets))

epochs = range(1, len(history.history["loss"]) + 1)
loss = history.history["loss"]
val_loss = history.history["val_loss"]
plt.figure()
plt.plot(epochs, loss, "bo", label="Training loss")
plt.plot(epochs, val_loss, "b", label="Validation loss")
plt.title("Training and validation loss")
plt.legend()

from keras.preprocessing.image import array_to_img

model = keras.models.load_model("oxford_segmentation.keras")

i = 1
test_image = val_input_imgs[i]
plt.axis("off")
plt.imshow(array_to_img(test_image))

mask = model.predict(np.expand_dims(test_image, 0))[0]

def display_mask(pred):
    mask = np.argmax(pred, axis=-1)
    mask *= 127
    plt.axis("off")
    plt.imshow(mask)

display_mask(mask)