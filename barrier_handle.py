#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/7/1 8:04
# @File    : barrier_handle.py
# @Software: PyCharm

import cv2
from handle2 import *
import matplotlib.pyplot as plt
import numpy as np
import time

font = cv2.FONT_HERSHEY_SIMPLEX

class barrier_detect():
    def __init__(self):
        pass

    def detect_barrary(self, imgs, dir, limit=3.0, size=3000, show=False):
        image = imgs.copy()
        image, contours, hier = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []

        for c in contours:

            x, y, w, h = cv2.boundingRect(c)

            box = np.array([[x, y + h], [x, y], [x + w, y], [x + w, y + h]])

            # 横向
            if float(w / h) > limit and w * h > size and dir == 1:
                boxes.append(box)

            # 纵向
            if float(h / w) > limit and w * h > size and dir == 2:
                boxes.append(box)

        return boxes, imgs



    def get_split(self, imgs):
        WHITE = 255
        WIDTH = 25
        LENGTH_LIMIT = 180
        img_split = np.array(imgs.copy())

        w, h = imgs.shape

        la = np.ones((300, 1), dtype=np.float) * 1 / 180
        ha = (img_split * la).astype(np.int)
        #zong
        h_count = np.sum(ha, axis=1)
        w_count = np.sum(ha, axis=0)

        W_1 = np.sum(ha[110:140,:], axis=0)
        W_2 = np.sum(ha[160:190,:], axis=0)
        H_1 = np.sum(ha[:,110:140], axis=1)
        H_2 = np.sum(ha[:,160:190], axis=1)


        h_count = h_count + H_1 + H_2
        w_count = w_count + W_1 + W_2
        # first
        w_start = w_stop = 0
        for i in range(w):
            if w_count[i] > LENGTH_LIMIT:
                w_start = i
                break

        for i in range(min(w, w_start+2), min(w-1, w_start+40)):
            if w_count[i] < LENGTH_LIMIT:
                w_stop = i - 1
                break
            if i == (w_start+40-1):
                w_stop = i
            if i == (w-1):
                w_stop = w-1

        h_start = h_stop = 0
        for i in range(h):
            if h_count[i] > LENGTH_LIMIT:
                h_start = i
                break

        for i in range(min(h, h_start+2), min(h-1, h_start+40)):
            if h_count[i] < LENGTH_LIMIT:
                h_stop = i - 1
                break
            if i == h_start+40-1:
                h_start = i
            if i == (h-1):
                h_stop = h-1

        if (h_start != 0 or h_stop != 0) and (w_start != 0 or w_stop != 0):
            h_start = max(h_start - 25, 0)
            h_stop = min(h_stop + 25, h - 1)
            w_start = max(w_start - 20, 0)
            w_stop = min(w_stop + 20, w - 1)

        # 给小黑快赋值
        img_split[h_start:h_stop, w_start:w_stop] = 0

        # second
        w_start = w_stop = 0
        for i in range(w-1,-1,-1):
            if w_count[i] > LENGTH_LIMIT:
                w_stop = i
                break

        for i in range(max(0, w_stop-2), max(-1, w_stop-40), -1):
            if w_count[i] < LENGTH_LIMIT:
                w_start = i + 1
                break
            if i == (w_stop-40+1):
                w_start = i
            if i == 0:
                w_start= 0


        h_start = h_stop = 0
        for i in range(h):
            if h_count[i] > LENGTH_LIMIT:
                h_start = i
                break

        for i in range(min(h, h_start+2), min(h-1, h_start+40)):
            if h_count[i] < LENGTH_LIMIT:
                h_stop = i - 1
                break
            if i == h_start+40-1:
                h_stop = i
            if i == (h-1):
                i = h-1

        if (h_start != 0 or h_stop != 0) and (w_start != 0 or w_stop != 0):
            h_start = max(h_start - 25, 0)
            h_stop = min(h_stop + 25, h - 1)
            w_start = max(w_start - 20, 0)
            w_stop = min(w_stop + 20, w - 1)

        # 给小黑快赋值
        img_split[h_start:h_stop, w_start:w_stop] = 0

        # third
        w_start = w_stop = 0
        for i in range(w):
            if w_count[i] > LENGTH_LIMIT:
                w_start = i
                break

        for i in range(min(w, w_start+2), min(w-1, w_start+40)):
            if w_count[i] < LENGTH_LIMIT:
                w_stop = i - 1
                break
            if i == (w_start+40-1):
                w_stop = i
            if i == (w-1):
                w_stop = w-1

        h_start = h_stop = 0
        for i in range(h-1, -1, -1):
            if h_count[i] > LENGTH_LIMIT:
                h_stop = i
                break

        for i in range(max(0, h_stop-2), max(-1, h_stop-40), -1):
            if h_count[i] < LENGTH_LIMIT:
                h_start = i + 1
                break
            if i == (h_stop-40+1):
                h_start = i
            if i == 0:
                h_start = 0

        if (h_start != 0 or h_stop != 0) and (w_start != 0 or w_stop != 0):
            h_start = max(h_start - 25, 0)
            h_stop = min(h_stop + 25, h - 1)
            w_start = max(w_start - 20, 0)
            w_stop = min(w_stop + 20, w - 1)

        # 给小黑快赋值
        img_split[h_start:h_stop, w_start:w_stop] = 0

        return img_split

    def draw_barrier(self,imgs, box):
        cv2.drawContours(imgs, [box], 0, (0, 0, 255), 3)


    def get_centre_dir(self, box, size=300):
        centre_x = int((box[1][0] + box[3][0]) / 2)
        centre_y = int((box[1][1] + box[3][1]) / 2)

        x = centre_x - size / 2
        y = centre_y - size / 2

        norm = (x**2 + y**2)**0.5
        if norm != 0.0:
            x = float(x / norm)
            y = float(y / norm)
        else:
            x = 0.0
            y = 0.0

        return [centre_x, centre_y], [x,y]

    def get_size(self, box):
        return (box[2][0] - box[0][0]) * (box[0][1] - box[1][1])

    def direct(self, imgs, dir, angel, size=300, limit=10, limit2=100, pos_limit=230, pos_limit_lr_s = 200, pos_limit_lr=190):
        direct_list = []

        BLACK = 0
        # 分割图像
        img_detect_ori = self.get_split(imgs)

        img_detect = np.array(img_detect_ori.copy())

        if dir == 'up' or dir == 'down':
            img_detect[:,0:20] = BLACK
            img_detect[:,280:300] = BLACK

        if dir == 'left' or dir == 'right':
            img_detect[0:20, :] = BLACK
            img_detect[280:300,:] = BLACK
        # 识别
        if dir == 'up' or dir == 'down':
            boxes, img_detect = self.detect_barrary(img_detect, 1)
        elif dir == 'left' or dir == 'right':
            boxes, img_detect = self.detect_barrary(img_detect, 2)

        for box in boxes:
            centre, centre_dir = self.get_centre_dir(box)

            # 太靠边的不要
            if dir == 'up' or dir == 'down':
                if  abs(centre[0]-size/2) < limit2:
                    direct_list.append(box)
            elif dir == 'left' or dir == 'right':
                if (centre[1]-size/2) < limit2:
                    direct_list.append(box)
        # 获得最可能的一个障碍，最大的就是最可能的啦
        if len(direct_list) > 1:
            temp_dict = {}
            for dl in direct_list:
                temp_dict[self.get_size(dl)] = dl
            temp_dict = sorted(temp_dict.items(), key=lambda x:x[0], reverse=True)
            direct_list = temp_dict[0][1]
        elif len(direct_list) == 1:
            direct_list = direct_list[0]
        elif len(direct_list) == 0:
            if dir == 'up':
                direct = [1.0, 0.0, angel]
                centre = [150, 0]
            elif dir == 'down':
                direct = [-1.0, 0.0, angel]
                centre = [150, 300]
            elif dir == 'left':
                direct = [0.0, -1.0, angel]
                centre = [0, 150]
            elif dir == 'right':
                direct = [0.0, 1.0, angel]
                centre = [300, 150]
            return direct, centre, None
        # centre 0:zuoyou
        centre, centre_dir = self.get_centre_dir(direct_list)
        b_speed = 0.8
        if dir == 'up':
            #如果靠左或右先调整一下
            if centre[0] - size/2 > limit:
                direct = [0.0,  b_speed, angel]
            elif centre[0] - size/2 < -limit:
                direct = [0.0, -b_speed, angel]
            else:
                if abs(centre[1] - pos_limit) > 5:
                    if centre[1] > pos_limit:
                        direct = [-b_speed, 0.0, angel]
                    else:
                        direct = [b_speed, 0.0, angel]
                else:
                    direct = [0.0, 0.0, angel]

        elif dir == 'down':
            if centre[0] - size/2 > limit:
                direct = [0.0,  b_speed, angel]
            elif centre[0] - size/2 < -limit:
                direct = [0.0, -b_speed, angel]
            else:
                if abs(centre[1] - pos_limit) > 5:
                    if centre[1] > pos_limit:
                        direct = [-b_speed, 0.0, angel]
                    else:
                        direct = [b_speed, 0.0, angel]
                else:
                    direct = [0.0, 0.0, angel]

        elif dir == 'left':
            if centre[1] - pos_limit_lr_s > limit:
                direct = [-b_speed,  0.0, angel]
            elif centre[1] - pos_limit_lr_s < -limit:
                direct = [b_speed, 0.0, angel]
            else:
                if abs(centre[0] - pos_limit_lr) > 5:
                    if centre[0] > pos_limit_lr:
                        direct = [0.0, b_speed, angel]
                    else:
                        direct = [0.0, -b_speed, angel]
                else:
                    direct = [0.0, 0.0, angel]

        elif dir == 'right':
            if centre[1] - pos_limit_lr_s > limit:
                direct = [-b_speed,  0.0, angel]
            elif centre[1] - pos_limit_lr_s < -limit:
                direct = [b_speed, 0.0, angel]
            else:
                if abs(centre[0] - pos_limit_lr) > 5:
                    if centre[0] > pos_limit_lr:
                        direct = [0.0, b_speed, angel]
                    else:
                        direct = [0.0, -b_speed, angel]
                else:
                    direct = [0.0, 0.0, angel]

        return direct, centre, np.array(direct_list)





if __name__ == '__main__':
    capture = cv2.VideoCapture(0)
    while True:
        ret, frame = capture.read()
        img = pre_handle(frame)
        _, img_b = cv2.threshold(img, 230, 255, cv2.THRESH_BINARY)

        bd = barrier_detect()
        direct, centre, bbox = bd.direct(img_b, 'right', 0)

        if isinstance(bbox, np.ndarray):
            cv2.drawContours(img, [bbox], 0, (0, 0, 255), 3)
        print('=' * 40)
        print('centre: ' + str(centre))
        print('direct: ' + str(direct))

        if isinstance(bbox, np.ndarray):
            cv2.drawContours(img, [bbox], 0, (0, 0, 255), 3)
        cv2.imshow('lala',img_b)
        cv2.imshow('origin',img)
        cv2.waitKey(1)
    cv2.destroyAllWindows()





