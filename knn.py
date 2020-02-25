#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/5/28 19:44
# @File    : knn.py
# @Software: PyCharm
import numpy as np
from numpy import tile
import cv2
import operator

class knn():
    def __init__(self):
        def getPath(num, index):
            return 'digital/' + str(num) + '_' + str(index) + '.jpg'

        dataset = []

        for i in range(10):
            for j in range(1, 4):
                img = cv2.imread(getPath(i, j), cv2.IMREAD_GRAYSCALE)
                _, img = cv2.threshold(img, 210, 255, cv2.THRESH_BINARY)
                img = self.img_resize(img)
                dataset.append(img)
        self.dataset = np.array(dataset).reshape(30, -1)
        self.labels = np.zeros((30), dtype=np.int)
        for i in range(30):
            self.labels[i] = i / 3

    def img_resize(self, img):
        assert img.shape[0] == 36 and img.shape[1] == 36
        return np.array(img).reshape((1,-1))


    def predict(self, img):
        img_vector = self.img_resize(img)
        dataSetSize = self.dataset.shape[0]
        diffMat = tile(img_vector, (dataSetSize, 1)) - self.dataset
        sqDiffMat = diffMat ** 2
        sqDistance = sqDiffMat.sum(axis=1)
        distance = sqDistance ** 0.5
        sortedDistIndicies = distance.argsort()
        classCount = {}

        for i in range(4):
            voteIlabel = self.labels[sortedDistIndicies[i]]
            classCount[voteIlabel] = classCount.get(voteIlabel, 0) + 1
        sortedClassCount = sorted(classCount.items(), key=operator.itemgetter(1), reverse=True)
        return [sortedClassCount[0][0]]






