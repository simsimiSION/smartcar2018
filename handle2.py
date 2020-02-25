#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/5/27 21:44
# @File    : handle2.py
# @Software: PyCharm

import cv2
import numpy as np
import matplotlib.pyplot as plt
from map import Map
from info_handle import number_confirm
from knn import knn
import time
import math
from handle import no_boundary, get_info, get_near, get_direction, detect_all_black
from kmeans import kmeans

def imageRead(image_file, type=1, therehold=None):
    """
    :param image_file:
    :param type: 0 二值化 1 灰度 2彩色
    :return:
    """

    if type == 0:
        img = cv2.imread(image_file, cv2.IMREAD_COLOR)
    elif type == 1:
        img = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
    elif type == 2:
        assert therehold != None
        img = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
        _, img = cv2.threshold(img, therehold, 255, cv2.THRESH_BINARY)
    else:
        raise Exception('输入的图像类型有误')

    return img

def imageG2B(img, therehold):
    _, img = cv2.threshold(img, therehold, 255, cv2.THRESH_BINARY)
    return img

def imageShow(windows, imgs):
    assert len(windows) == len(imgs)

    for window, img in zip(windows, imgs):
        cv2.imshow('%s' % window, img)

def imageResize(img, size):
    return cv2.resize(img, size, interpolation=cv2.INTER_AREA)

def imagePerTransfer(img, src, dis, size=(300,300)):
# 自己选择要进行透视变换的点 [左上, 右上, 左下, 右下]
    src_array = np.array(src)
    dis_array = np.array(dis)
    M = cv2.getPerspectiveTransform(src_array, dis_array)
    dis_martix = cv2.warpPerspective(img, M, size)

    return dis_martix

def imageDilate(img, kernel=None):
    if kernel == None:
        kernel = np.zeros((5,5), dtype=np.uint8)
        kernel[1:4,1:4] = np.ones((3,3), dtype=np.uint8)

    dilated = cv2.dilate(img, kernel)

    return dilated

def imageErode(img, kernel=None):
    if kernel == None:
        kernel = np.zeros((5,5), dtype=np.uint8)
        kernel[1:4,1:4] = np.ones((3,3), dtype=np.uint8)

    eroded = cv2.erode(img, kernel)

    return eroded

def imageContoursFigure(img, reverse=True, area=[1000,20000] , limit=[0.25, 2]):
    image = img.copy()

    image, contours, hier = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for c in contours:
        #box  1 2
        #     0 3
        #rect = cv2.minAreaRect(c)
        x,y,w,h = cv2.boundingRect(c)
        box = np.array([[x,y+h],[x,y],[x+w,y],[x+w,y+h]])

        if (box[3][0] - box[0][0]) * (box[0][1] - box[1][1]) >= area[0] and \
                (box[3][0] - box[0][0]) * (box[0][1] - box[1][1]) <= area[1] and\
                float ((box[3][0] - box[0][0]) / (box[0][1] - box[1][1])) > limit[0] and\
                float((box[3][0] - box[0][0]) / (box[0][1] - box[1][1])) < limit[1]:
            boxes.append(box)


    boxes = no_boundary(boxes,[300, 300])
    return get_direction(boxes)

def imageCountourHandle(img, contours):
    image_list = []

    for index, contour in enumerate(contours):
        Xs = [i[0] for i in contour]
        Ys = [i[1] for i in contour]
        x1 = min(Xs)
        x2 = max(Xs)
        y1 = min(Ys)
        y2 = max(Ys)
        cropImg = img.copy()
        temp_img = imagePerTransfer(cropImg,
                                    np.float32([contour[1], contour[2], contour[0], contour[3]]),
                                    np.float32([[0, 0], [y2-y1, 0], [0, x2-x1], [y2-y1, x2-x1]]),
                                    (y2-y1,x2-x1))
        temp_img = imageResize(temp_img, (36,36))

        #防止全为黑的情况出现
        if detect_all_black(temp_img) == 0:
            image_list.append(temp_img)

    return image_list

def getMeanPiexl(image):
    #get image size
    if len(image.shape) > 2:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    w, h = image.shape
    size = h * w

    #compute the mean piexl
    image_array = np.array(image).reshape(-1)
    image_array = sorted(image_array)
    mean_piexl = (image_array[0] + image_array[size-1] ) / 2

    return mean_piexl

def imagePiexlDistrib(img):
    _, image = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
    height, width = image.shape

    WHITE = 255
    piexl_distrib = []
    for i in range(width):
        piexl_distrib.append(sum(image[:,i] == WHITE))

    return piexl_distrib

def get_rotate_angel(img):
    angel = 0
    angel_n = []
    angel_p = []

    edges = cv2.Canny(img, 50, 200)

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 30, minLineLength=150, maxLineGap=10)

    if lines is None:
        return 0

    lines1 = lines[:, 0, :]  # 提取为二维

    for x1, y1, x2, y2 in lines1[:]:
        if x2 != x1:
            temp = math.atan((y2 - y1) / (x2 - x1)) * 360 / 2 / math.pi

            if temp < 30.0 and temp > 0.0:
                angel_n.append(temp)
            if temp < -30.0:
                angel_n.append(temp+90.0)
            if temp > -30.0 and temp < 0.0:
                angel_p.append(temp)
            if temp > 30.0:
                angel_p.append(temp-90.0)


        #cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 1)

    if angel_n != [] and angel_p == []:
        angel = sum(angel_n) / len(angel_n)
    if angel_p != [] and angel_n == []:
        angel = sum(angel_p) / len(angel_p)

    angel = float(int(angel))

    return angel

def get_rotate_angel_2(img):
    angel = 0
    neg = []
    pos = []

    edges = cv2.Canny(img, 50, 200)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 30, minLineLength=50, maxLineGap=10)

    if lines is None:
        return 0,img

    lines1 = lines[:, 0, :]  # 提取为二维

    line_list = []
    for x1, y1, x2, y2 in lines1[:]:
        if x2 != x1:
            temp = math.atan((y2 - y1) / (x2 - x1)) * 360 / 2 / math.pi
            line_list.append([[x1, y1, x2, y2], temp])

        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 0), 2)

    for a in line_list:
        if a[1] > 0:
            pos.append(a[1])
        else:
            pos.append(a[1]+90)

    if len(pos >= 3):
        angel = kmeans((pos))
        if angel > 45.0:
            angel -= 90.0
    else:
        angel = 0.0


    return angel, img

def detect_big(img):
    BLACK = 0
    WHITE = 255

    img_circle = img.copy()

    for i in range(10):
        for j in range(300):
            img_circle[i,j] = BLACK
            img_circle[300-i-1,j] = BLACK
            img_circle[j,i] = BLACK
            img_circle[j,300-i-1] = BLACK

    bit, contours, loc = imageContoursFigure(img_circle)

    best_countour = []
    centre = []
    centre_countour = []
    size = 0
    is_circle = 0

    if contours != []:
        for contour in contours:
            if abs(contour[0][1] - contour[1][1]) > 120 and abs(contour[0][0] - contour[2][0]) > 120 and \
                    abs(contour[0][1] - contour[1][1]) < 250 and abs(contour[0][0] - contour[2][0]) < 250:
                if abs(contour[0][1] - contour[1][1]) * abs(contour[0][0] - contour[2][0]) > size:
                    best_countour = contour


    if best_countour != []:

        x_start = best_countour[0][0]
        x_stop  = best_countour[2][0]
        y_start = best_countour[1][1]
        y_stop  = best_countour[0][1]

        np_img = np.array(img_circle[y_start:y_stop+1,x_start:x_stop+1])
        count_white = int(np.sum(np.sum(np_img, axis=1) / 255))
        count = (y_stop-y_start+1)*(x_stop-x_start+1)

        if float(1.0*count_white/count) > 0.6:
            is_circle = 1

    return is_circle

def get_rotate_angel_3(img_g):
    angel = 0
    neg = []
    pos = []
    _, img = cv2.threshold(img_g, 245, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(img, 50, 200)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 30, minLineLength=100, maxLineGap=10)

    if lines is None:
        return 0,img_g

    lines1 = lines[:, 0, :]  # 提取为二维

    line_list = []
    for x1, y1, x2, y2 in lines1[:]:
        if x2 != x1:
            temp = math.atan((y2 - y1) / (x2 - x1)) * 360 / 2 / math.pi
            line_list.append([[x1, y1, x2, y2], temp])

        #cv2.line(img_g, (x1, y1), (x2, y2), (0, 0, 0), 2)

    for a in line_list:
        if a[1] > 0:
            pos.append(a[1])
        else:
            pos.append(a[1]+90)

    if len(pos) >= 3:
        angel = kmeans((pos))
        if angel > 45.0:
            angel -= 90.0
    else:
        angel = 0

    return angel, img_g


def imageRotate(img, angel):
    affineShrinkTranslationRotation = cv2.getRotationMatrix2D((300 / 2, 300 / 2), angel, 1)
    ShrinkTranslationRotation = cv2.warpAffine(img, affineShrinkTranslationRotation, (300, 300),
                                               borderValue=0)
    return ShrinkTranslationRotation



def batchWithNoise(batch):
    imgs  = batch[0]
    label = batch[1]
    batch_len = len(label)

    new_batch_img = []
    new_batch = []

    for index, ori in enumerate(imgs):
        img = np.zeros((36,36), dtype=np.float)
        ori = np.array(ori).reshape((28,28))


        # img 36*36
       # img[4:28+4, 4:28+4] = ori[:,:]
        main_param = np.random.randint(0,6)
        inn_param = np.random.randint(0,2)
        param = np.random.randint(1,5)

        if main_param > 3:
            if inn_param == 1:
                if param == 1:
                    img[:2,:15]  = np.random.rand(2,15)
                    img[8:28+8, 4:28+4] = ori[:,:]
                elif param == 2:
                    img[:15,34:] = np.random.rand(15,2)
                    img[4:28+4,0:28+0] = ori[:,:]
                elif param == 3:
                    img[34:,:15] = np.random.rand(2,15)
                    img[0:28+0,4:28+4] = ori[:,:]
                elif param == 4:
                    img[:15,:2] = np.random.rand(15,2)
                    img[4:28+4,8:28+8] = ori[:,:]
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

def getNumber(img, Model):

    number_list = []
    number = 100
    font = cv2.FONT_HERSHEY_SIMPLEX

    # 生成二值化图像
    img_b = imageG2B(img, 245)
    for _ in range(2):
        img_b = imageDilate(img_b)



    # 找框框
    bit, contours, loc = imageContoursFigure(img_b)

    if bit != 0:
        image_list = imageCountourHandle(img, contours)
        bit = len(image_list)

    if bit != 0:
        for image, contour in zip(image_list, contours):
            _, im_1 = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
            number_list.append(Model.predict(im_1)[0])

            cv2.putText(img, str(Model.predict(im_1)[0]), (contour[0][0], contour[0][1]), font, 0.8, (0, 255, 0), 2)
            cv2.drawContours(img, [contour], 0, (0, 0, 255), 3)

    if bit == 0:
        pass
    elif bit == 1:
        number = number_list[0]
    elif bit == 2:
        number = number_list[0] * 10 + number_list[1]
    return number, loc, img, img_b

def pre_handle(img):
    img_g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_origin = img_g.copy()
    #src = np.float32([[110, 18], [460, 10], [100, 383], [480, 375]])
    src = np.float32([[125, 38], [475, 40], [115, 383], [495, 375]])
    #src = np.float32([[55, 10], [460, 0], [20, 470], [495, 470]])
    dis = np.float32([[0, 0], [300, 0], [0, 300],[300, 300]])
    img_g = imagePerTransfer(img_g, src, dis)

    return img_g












