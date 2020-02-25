from PIL import Image, ImageFilter
import tensorflow as tf
import matplotlib.pyplot as plt
import cv2
import numpy as np
import selectivesearch
import math


def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)


def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)


def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')


class mnist():
    def __init__(self):
        # model init
        self.x = tf.placeholder(tf.float32, [None, 1296])
        W = tf.Variable(tf.zeros([1296, 10]))
        b = tf.Variable(tf.zeros([10]))

        W_conv1 = weight_variable([5, 5, 1, 32])
        b_conv1 = bias_variable([32])

        x_image = tf.reshape(self.x, [-1, 36, 36, 1])
        h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
        h_pool1 = max_pool_2x2(h_conv1)

        W_conv2 = weight_variable([5, 5, 32, 64])
        b_conv2 = bias_variable([64])

        h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
        h_pool2 = max_pool_2x2(h_conv2)

        W_fc1 = weight_variable([9 * 9 * 64, 1024])
        b_fc1 = bias_variable([1024])

        h_pool2_flat = tf.reshape(h_pool2, [-1, 9 * 9 * 64])
        h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

        self.keep_prob = tf.placeholder(tf.float32)
        h_fc1_drop = tf.nn.dropout(h_fc1, self.keep_prob)

        W_fc2 = weight_variable([1024, 10])
        b_fc2 = bias_variable([10])

        self.y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

        # session init
        self.init_op = tf.initialize_all_variables()
        self.saver = tf.train.Saver()
        self.sess = tf.Session()
        self.sess.run(self.init_op)
        self.saver.restore(self.sess, "./ckpg_model/model.ckpt")  # 这里使用了之前保存的模型参数

    def predict(self, image):
        image = list(image.reshape(-1))
        result = [i/255.0 for i in image]

        prediction = tf.argmax(self.y_conv, 1)
        predint = prediction.eval(feed_dict={self.x: [result], self.keep_prob: 1.0}, session=self.sess)
        predint_array = self.y_conv.eval(feed_dict={self.x: [result], self.keep_prob: 1.0}, session=self.sess)

        return predint#, predint_array



