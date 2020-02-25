import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
import numpy as np
import cv2
slim = tf.contrib.slim
mnist = input_data.read_data_sets("MNIST_data", one_hot=True)


class alexnet():
    def __init__(self):
        self.x = tf.placeholder(tf.float32, [None, 1296])
        self.y = tf.placeholder(tf.float32, [None, 10])
        self.drop_param =  tf.placeholder(tf.float32)

        self.net = tf.reshape(self.x, shape=[-1, 36, 36, 1])

        # 第一层网络
        self.net = slim.conv2d(self.net, 64, [3, 3], scope='conv1')
        self.net = slim.batch_norm(self.net, activation_fn=tf.nn.relu)
        self.net = slim.max_pool2d(self.net, [2, 2], scope='pool1')
        # 第二层网络
        self.net = slim.conv2d(self.net, 128, [3, 3], scope='conv2')
        self.net = slim.batch_norm(self.net, activation_fn=tf.nn.relu)
        self.net = slim.max_pool2d(self.net, [2, 2], scope='pool2')
        # 第三层网络
        self.net = slim.conv2d(self.net, 256, [3, 3], scope='conv3')
        self.net = slim.batch_norm(self.net, activation_fn=tf.nn.relu)
        self.net = slim.max_pool2d(self.net, [2, 2], scope='pool3')
        # 全连接层
        self.net = tf.reshape(self.net, [-1, 4 * 4 * 256])
        self.net = slim.fully_connected(self.net, 1024, scope='fc/fc_1')
        self.net = slim.dropout(self.net, self.drop_param, scope='fc/dp_1')
        self.net = slim.fully_connected(self.net, 1024, scope='fc/fc_2')
        self.net = slim.dropout(self.net, self.drop_param, scope='fc/dp_2')
        self.net = slim.fully_connected(self.net, 10, activation_fn=None, scope='fc/fc_3')

        # 网络预测输出值
        self.prediction = self.net
        # 计算损失
        self.cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.prediction, labels=self.y))
        # 生成优化器
        self.optimizer = tf.train.AdamOptimizer(1e-4).minimize(self.cost)
        # 评判准确率
        self.correct_pred = tf.equal(tf.argmax(self.prediction, 1), tf.argmax(self.y, 1))
        self.accuracy = tf.reduce_mean(tf.cast(self.correct_pred, tf.float32))

        self.saver = tf.train.Saver()
        self.sess = tf.Session()
        self.init = tf.initialize_all_variables()

        self.sess.run(self.init)
    #训练模型
    def train(self, batches, show_info=None, save=False):
        batch_xs, batch_ys = self.batchWithNoise(batches)
        self.optimizer.run(feed_dict={self.x: batch_xs, self.y: batch_ys, self.drop_param: 0.5}, session=self.sess)
        train_accuracy = 0.

        if show_info != None:
            train_accuracy = self.accuracy.eval(feed_dict={
                self.x: batch_xs, self.y: batch_ys, self.drop_param: 0.5}, session=self.sess)
            loss = self.cost.eval(feed_dict={
                self.x: batch_xs, self.y: batch_ys, self.drop_param: 0.5}, session=self.sess)
            print("step %d, loss: %f, training accuracy %g" % (show_info, loss, train_accuracy))

        if save:
            self.save_model()
        return train_accuracy

    #预测模型
    def predict(self, image):
        self.restore_model()

        image = list(image.reshape(-1))

        result = [i/255.0  for i in image]

        prediction = tf.argmax(self.prediction, 1)
        predint = prediction.eval(feed_dict={self.x: [result], self.drop_param: 1.0}, session=self.sess)
        predint_array = self.prediction.eval(feed_dict={self.x: [result], self.drop_param: 1.0}, session=self.sess)

        return predint  # , predint_array

    #数据增强
    def batchWithNoise(self, batch):
        imgs = batch[0]
        label = batch[1]
        batch_len = len(label)

        new_batch_img = []
        new_batch = []

        for index, ori in enumerate(imgs):
            img = np.zeros((36, 36), dtype=np.float)
            ori = np.array(ori).reshape((28, 28))
            # img 36*36
            main_param = np.random.randint(0, 6)
            inn_param = np.random.randint(0, 2)
            param = np.random.randint(1, 5)
            # 旋转
            rotate = np.random.randint(-20, 20)

            rotate_matrix = cv2.getRotationMatrix2D((28 / 2, 28 / 2), rotate, 1)
            ori = cv2.warpAffine(ori, rotate_matrix, (28, 28), borderValue=0)

            if main_param > 3:
                if inn_param == 1:
                    if param == 1:
                        img[:2, :15] = np.random.rand(2, 15)
                        img[8:28 + 8, 4:28 + 4] = ori[:, :]
                    elif param == 2:
                        img[:15, 34:] = np.random.rand(15, 2)
                        img[4:28 + 4, 0:28 + 0] = ori[:, :]
                    elif param == 3:
                        img[34:, :15] = np.random.rand(2, 15)
                        img[0:28 + 0, 4:28 + 4] = ori[:, :]
                    elif param == 4:
                        img[:15, :2] = np.random.rand(15, 2)
                        img[4:28 + 4, 8:28 + 8] = ori[:, :]
                    else:
                        img[4:28 + 4, 4:28 + 4] = ori[:, :]
                else:
                    if param == 1:
                        img[:2, 20:] = np.random.rand(2, 16)
                        img[8:28 + 8, 4:28 + 4] = ori[:, :]
                    elif param == 2:
                        img[20:, 34:] = np.random.rand(16, 2)
                        img[4:28 + 4, 0:28 + 0] = ori[:, :]
                    elif param == 3:
                        img[34:, 20:] = np.random.rand(2, 16)
                        img[0:28 + 0, 4:28 + 4] = ori[:, :]
                    elif param == 4:
                        img[20:, :2] = np.random.rand(16, 2)
                        img[4:28 + 4, 8:28 + 8] = ori[:, :]
                    else:
                        img[4:28 + 4, 4:28 + 4] = ori[:, :]
            else:
                img[4:28 + 4, 4:28 + 4] = ori[:, :]

            img = img.reshape(-1)
            new_batch_img.append(img)

        new_batch.append(new_batch_img)
        new_batch.append(label)

        return tuple(new_batch)

    #保存模型
    def save_model(self):
        self.saver.save(self.sess, './alexnet_model/model.ckpt')

    #读取模型
    def restore_model(self):
        self.saver.restore(self.sess, './alexnet_model/model.ckpt')


import matplotlib.pyplot as plt


if __name__ == '__main__':
    Alexnet = alexnet()

    plt_y = []
    for i in range(1000):
        plt_y.append(Alexnet.train(mnist.train.next_batch(64), i))
        if i % 10 == 0:
            plt_y.append(  Alexnet.train(mnist.train.next_batch(64), i))
    Alexnet.save_model()

    plt_x = np.arange(0, len(plt_y))
    plt_y = np.array(plt_y)
    plt.plot(plt_x, plt_y)
    plt.show()


