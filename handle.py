#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/6/6 13:05
# @File    : handle.py
# @Software: PyCharm

import pandas as pd
import numpy as np
import cv2
from handle2 import *
import time

def imageContoursFigure_2(img, reverse=True, area=[1000,80000] , limit=[0.25, 2]):
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

    return boxes

#去除掉靠近边界的框（因为容易识别错误）
def no_boundary(bboxs, limit, boundary=5):
    left = right = up = down = 0

    new_bbox = []
    for bbox in bboxs:
        left  = bbox[0][0]
        down  = bbox[0][1]
        right = bbox[2][0]
        up    = bbox[2][1]

        if left > boundary and up > boundary and down < limit[1] and right < limit[0]:
            new_bbox.append(bbox)

    return new_bbox

#检测是否全为黑
def detect_all_black(img, limit = 0.08, debug=0):
    shape = img.shape
    size = shape[0] * shape[1]
    WHITE = 255
    counter = 0

    for i in range(shape[0]):
        for j in range(shape[1]):
            if img[i,j] == WHITE:
                counter += 1

    ratio = float(counter / size)
    if debug:
        print(ratio)

    if ratio <  limit:
        return 1
    else:
        return 0



#检测圆
def detect_circle(img, debug=False):
    circle_list = []
    is_circle = -1
    #CANNY边缘检测
    # if detect_all_black(img, limit=0.5):
    #     is_circle = 0

    # if is_circle != 0:
    img = cv2.GaussianBlur(img, (3,3), 0)

    xgrad = cv2.Sobel(img, cv2.CV_16SC1, 1, 0)
    ygrad = cv2.Sobel(img, cv2.CV_16SC1, 0, 1)
    edge = cv2.Canny(xgrad, ygrad, 50, 150)

    #霍夫变换圆检测
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 100, param1=100, param2=30, minRadius=30, maxRadius=150)

    if isinstance(circles,np.ndarray):
        for circle in circles[0]:
            # 坐标行列
            x = int(circle[0])
            y = int(circle[1])
            # 半径
            r = int(circle[2])
            if r > 50:
                circle_list.append([x, y, r])

                if is_circle != 1:
                    is_circle = 1

                if debug:
                    img = cv2.circle(img, (x, y), r, (255, 255, 255), -1)

    if is_circle:
        if len(circle_list) > 1:
            circle_list = sorted(circle_list, key=lambda x: x[2])
            circle_list = circle_list[-1]
        elif len(circle_list) == 1:
            circle_list = circle_list[0]

    return is_circle, circle_list, img


def detect_circle_2(img, debug=False):
    BLACK = 0
    WHITE = 255


    img_circle = np.array(img.copy())

    img_circle[0:10, :] = BLACK
    img_circle[290:300,:] = BLACK
    img_circle[:,0:10] = BLACK
    img_circle[:,290:300] = BLACK

    contours = imageContoursFigure_2(img_circle)

    best_countour = []
    centre = []
    centre_countour = []
    size = 0
    is_circle = 0

    if contours != []:
        for contour in contours:
            if abs(contour[0][1] - contour[1][1]) > 90 and abs(contour[0][0] - contour[2][0]) > 120 and \
                    abs(contour[0][1] - contour[1][1]) < 250 and abs(contour[0][0] - contour[2][0]) < 250:
                if abs(contour[0][1] - contour[1][1]) * abs(contour[0][0] - contour[2][0]) > size:
                    best_countour = contour

    if best_countour != []:
        centre = [int((best_countour[0][0] + best_countour[2][0]) / 2),
                  int((best_countour[0][1] + best_countour[1][1]) / 2)]

        centre_countour = [[centre[0]-5, centre[1]+5],
                           [centre[0]-5, centre[1]-5],
                           [centre[0]+5, centre[1]-5],
                           [centre[0]+5, centre[1]+5]]

        x_start = best_countour[0][0]
        x_stop  = best_countour[2][0]
        y_start = best_countour[1][1]
        y_stop  = best_countour[0][1]

        np_img = np.array(img_circle[y_start:y_stop+1,x_start:x_stop+1])
        count_white = int(np.sum(np.sum(np_img, axis=1) / 255))
        count = (y_stop-y_start+1)*(x_stop-x_start+1)

        if float(1.0*count_white/count) > 0.65:
            is_circle = 1

    return np.array(best_countour), centre, is_circle


def get_info(bboxs):
    size_list = []
    position_list = []
    bias = []

    for bbox in bboxs:
        size_list.append((bbox[2][0]-bbox[0][0])*(bbox[0][1]-bbox[2][1]))
        position_list.append([int((bbox[0][0]+bbox[2][0])/2), int((bbox[0][1]+bbox[2][1])/2)])
        bias.append(int(bbox[2][0] - bbox[0][0]))

    return size_list, position_list, bias


def get_near(bbox):
    size = len(bbox)
    _, position, temp = get_info(bbox)

    dis_array = np.zeros((size, size), dtype=np.int)
    for i in range(size):
        for j in range(size):
            dis_array[i,j] = 1000

    for i in range(size):
        for j in range(i):
            dis_array[i,j] = abs(position[i][1] - position[j][1])   if i != j else 1000

    re = np.where( dis_array == np.min(dis_array) )
    re = [re[0][0], re[1][0]]
    return  re


def get_direction(bboxs):
    number = len(bboxs)
    bit = 0
    new_bbox = []
    location = []
    bias_list = []

    size, position, bias = get_info(bboxs)

    if number == 0:
        bit = 0
    elif number == 1:
        bit = 1
        new_bbox.append(bboxs[0])

        location = position[0]
    elif number == 2:
        bit = 2
        if abs(position[0][0] - position[1][0]) < 150:
            if position[0][0] > position[1][0]:
                new_bbox.append(bboxs[1])
                new_bbox.append(bboxs[0])
                bias_list.append(bias[1])
                bias_list.append(bias[0])
            else:
                new_bbox.append(bboxs[0])
                new_bbox.append(bboxs[1])
                bias_list.append(bias[0])
                bias_list.append(bias[1])

            for i, j in zip(position[0], position[1]):
                location.append(int((i+j)/2))
            location[0] = location[0] - int((bias_list[0] - bias_list[1])/2)
        else:
            bit = 0
    else:
        bit = 2

        index = get_near(bboxs)
        if abs(position[index[0]][0] - position[index[1]][0]) < 150:
            if position[index[0]][0] > position[index[1]][0]:
                new_bbox.append(bboxs[index[1]])
                new_bbox.append(bboxs[index[0]])
                bias_list.append(bias[index[1]])
                bias_list.append(bias[index[0]])
            else:
                new_bbox.append(bboxs[index[0]])
                new_bbox.append(bboxs[index[1]])
                bias_list.append(bias[index[1]])
                bias_list.append(bias[index[0]])
            for i, j in zip(position[index[0]], position[index[1]]):
                location.append(int((i+j)/2))

            location[0] = location[0] - int((bias_list[0] - bias_list[1])/2)
        else:
            bit = 0
    return bit, new_bbox, location




if __name__ == '__main__':
    capture = cv2.VideoCapture(0)
    while True:
        ret, frame = capture.read()
        img_ori = pre_handle(frame)
        _, img_b = cv2.threshold(img_ori, 230, 255, cv2.THRESH_BINARY)

        best_countour, centre, is_circle = detect_circle_2(img_b, debug=True)
        print(centre)
        if best_countour != []:
            cv2.drawContours(img_ori, [best_countour], 0, (0, 0, 255), 3)
        cv2.imshow('lala',img_b)
        cv2.imshow('origin',img_ori)
        print(is_circle)
        cv2.waitKey(1)
    cv2.destroyAllWindows()








