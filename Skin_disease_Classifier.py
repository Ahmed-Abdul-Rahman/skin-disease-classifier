# -*- coding: utf-8 -*-
"""Untitled7.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1A4ScIXSdSVeiwTqSEKjk9Md6UrCX2-kG
"""

import tensorflow as tf
import matplotlib.pyplot as plt
import os
import time
import glob
import pandas as pd
import numpy as np
import os
import cv2
from sklearn.preprocessing import LabelBinarizer
from PIL import Image
from tensorflow import keras
from tensorflow.keras.models import Sequential, Model
from  matplotlib import pyplot as plt
import matplotlib.image as mpimg
import random
from skimage import transform
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical,np_utils
from sklearn.utils import shuffle
from matplotlib import cm
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, BatchNormalization, Activation
from keras.layers.convolutional import Conv2D, MaxPooling2D

# %matplotlib inline
print("Imported")

#!unzip dataset/dataset

img_folder = r"dataset/Acne and Rosacea"
plt.figure(figsize=(20,20))
for i in range(5):
    file = random.choice(os.listdir(img_folder))
    image_path= os.path.join(img_folder, file)
    img=mpimg.imread(image_path)
    ax=plt.subplot(1,5,i+1)
    ax.title.set_text(file)
    plt.imshow(img)

def create_dataset(img_folder):
   
    img_data_array=[]
    class_name=[]
   
    for dir1 in os.listdir(img_folder):
        for file in os.listdir(os.path.join(img_folder, dir1)):
       
            image_path= os.path.join(img_folder, dir1,  file)
            image= cv2.imread( image_path)
            image=cv2.resize(image, (IMG_HEIGHT, IMG_WIDTH),interpolation = cv2.INTER_AREA)
            image=np.array(image)
            image = image.astype('float')
            image /= 255 
            img_data_array.append(image)
            class_name.append(dir1)
    return img_data_array, class_name
# extract the image array and class name
IMG_HEIGHT = 227
IMG_WIDTH = 227
img_data, class_name =create_dataset(r'dataset/')

CLASS_NAMES = ["Acne and Rosacea", "Alopecia Areata and Hair Disease", "Benign Moles and Tumors", "STD"]
strtoint = {"Acne and Rosacea":0, "Alopecia Areata and Hair Disease":1,"Benign Moles and Tumors":2,"STD":3}

labels1 = []
for name in class_name:
  labels1.append(strtoint[name])

print(len(img_data),len(labels1))

images = np.array(img_data)
labels = np.array(labels1)
lb = LabelBinarizer()
labels = lb.fit_transform(labels)
images,labels = shuffle(images, labels)
print(labels)
print(images.shape,labels.shape)

(train_images, test_images, train_labels, test_labels) = train_test_split(images, labels, test_size=0.15, random_state=42)
print(train_images.shape,test_images.shape)
print(train_labels.shape,test_labels.shape)

validation_images,validation_labels = train_images[600:],train_labels[600:]
train_images,train_labels = train_images[:600],train_labels[:600]
print(train_images.shape,train_labels.shape)
print(validation_images.shape,validation_labels.shape)

train_ds = tf.data.Dataset.from_tensor_slices((train_images, train_labels))
test_ds = tf.data.Dataset.from_tensor_slices((test_images, test_labels))
validation_ds = tf.data.Dataset.from_tensor_slices((validation_images, validation_labels))

train_ds_size = tf.data.experimental.cardinality(train_ds).numpy()
test_ds_size = tf.data.experimental.cardinality(test_ds).numpy()
validation_ds_size = tf.data.experimental.cardinality(validation_ds).numpy()
print("Training data size:", train_ds_size)
print("Test data size:", test_ds_size)
print("Validation data size:", validation_ds_size)

def process_images(image, label):
    # Normalize images to have a mean of 0 and standard deviation of 1
    image = tf.image.per_image_standardization(image)
    # Resize images from 32x32 to 227x227
    image = tf.image.resize(image, (227,227))
    return image, label

train_ds = (train_ds.map(process_images)
                  .shuffle(buffer_size=train_ds_size)
                  .batch(batch_size=32, drop_remainder=True))
test_ds = (test_ds
                  .map(process_images)
                  .shuffle(buffer_size=train_ds_size)
                  .batch(batch_size=32, drop_remainder=True))
validation_ds = (validation_ds
                  .map(process_images)
                  .shuffle(buffer_size=train_ds_size)
                  .batch(batch_size=32, drop_remainder=True))
print(train_ds)
print(len(train_ds))

model = keras.models.Sequential([
    keras.layers.Conv2D(filters=96, kernel_size=(11,11), strides=(4,4), activation='relu',padding="same", input_shape=(227,227,3)),
    keras.layers.BatchNormalization(),
    keras.layers.MaxPool2D(pool_size=(3,3), strides=(2,2)),
    keras.layers.Conv2D(filters=256, kernel_size=(5,5), strides=(1,1), activation='relu', padding="same"),
    keras.layers.BatchNormalization(),
    keras.layers.MaxPool2D(pool_size=(3,3), strides=(2,2)),
    keras.layers.Conv2D(filters=384, kernel_size=(3,3), strides=(1,1), activation='relu', padding="same"),
    keras.layers.BatchNormalization(),
    keras.layers.Conv2D(filters=384, kernel_size=(1,1), strides=(1,1), activation='relu', padding="same"),
    keras.layers.BatchNormalization(),
    keras.layers.Conv2D(filters=256, kernel_size=(1,1), strides=(1,1), activation='relu', padding="same"),
    keras.layers.BatchNormalization(),
    keras.layers.MaxPool2D(pool_size=(3,3), strides=(2,2)),
    keras.layers.Flatten(),
    keras.layers.Dense(4096, activation='relu'),
    keras.layers.Dropout(0.5),
    keras.layers.Dense(4096, activation='relu'),
    keras.layers.Dropout(0.5),
    keras.layers.Dense(4, activation='softmax')
])

opt1 = tf.optimizers.SGD(lr=0.001)
opt2 = "adam"
model.compile(loss='categorical_crossentropy', optimizer=opt2, metrics=['accuracy'])
model.summary()

model.fit(train_ds,
          epochs=100,
          validation_data=validation_ds,
          validation_freq=1)

score = model.evaluate(test_ds, verbose=0)
print(f'Test loss: {score[0]} / Test accuracy: {score[1]}')

image= cv2.imread("dataset/Benign Moles and Tumors/images18.jpg")
image=cv2.resize(image, (227, 227),interpolation = cv2.INTER_AREA)
image=np.array(image)
image = np.expand_dims(image, axis=0)  
image = image.astype('float')
image /= 255 
print(model.predict(image))