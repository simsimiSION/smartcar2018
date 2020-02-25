from detect_img import mnist
from imageHandle import batchWithNoise
import cv2
import numpy as np
from tensorflow.examples.tutorials.mnist import input_data
mnist_data = input_data.read_data_sets('MNIST_data', one_hot=True)


batch = mnist_data.train.next_batch(50)
print(batch[1][0])
batch = batchWithNoise(batch)
images, labels = batch[0], batch[1]


model = mnist()



#print(list(np.array(images[0]).reshape((36,36))))
cv2.imshow('la',np.array(images[0]).reshape((36,36)))
affineShrinkTranslationRotation = cv2.getRotationMatrix2D((36 / 2, 36 / 2), -15, 1)
ShrinkTranslationRotation = cv2.warpAffine(np.array(images[0]).reshape((36,36)), affineShrinkTranslationRotation, (36, 36),
                                           borderValue=0)

cv2.imshow('xi',ShrinkTranslationRotation)
cv2.waitKey(0)



