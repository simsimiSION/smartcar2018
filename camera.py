#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/5/27 20:43
# @File    : camera.py
# @Software: PyCharm

import cv2
import numpy as np
import time


path = 'image/'
index = 3

cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FPS, 30)
# cap.set(cv2.CAP_PROP_BRIGHTNESS, -1)
# cap.set(cv2.CAP_PROP_CONTRAST, 40)
# cap.set(cv2.CAP_PROP_SATURATION, 50)
# cap.set(cv2.CAP_PROP_HUE, 50)
# cap.set(cv2.CAP_PROP_EXPOSURE, -1)

# cap.set(3, 320)
# print(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# cap.set(cv2.CAP_PROP_FPS,30)
while(1):
    # print('exposure: ' + str(cap.get(cv2.CAP_PROP_EXPOSURE)))
    # fps = cap.get(cv2.CAP_PROP_FPS)
    # print(fps)
    start = time.time()
    # get a frame
    ret, frame = cap.read()
    #print(frame.shape)
    # show a frame
    cv2.imshow("capture", frame)

    if cv2.waitKey(1) & 0xFF == ord('a'):
        cv2.imwrite(path+'%d.jpg' %index, frame)
        index += 1
    print('fps: {}'.format(int(1/(time.time() - start))))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
