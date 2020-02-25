import serial
from handle2 import *
import cv2
from kmeans import *



def get_rotate_angel_2(img):
    angel = 0
    angel_n = []
    angel_p = []

    edges = cv2.Canny(img, 50, 200)

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 30, minLineLength=50, maxLineGap=10)

    if lines is None:
        return 0,img

    lines1 = lines[:, 0, :]  # 提取为二维

    print('='*30)
    for x1, y1, x2, y2 in lines1[:]:
        if x2 != x1:
            temp = math.atan((y2 - y1) / (x2 - x1)) * 360 / 2 / math.pi
            print(temp)
            if temp < 30.0 and temp > 0.0:
                angel_n.append(temp)
            if temp < -30.0:
                angel_n.append(temp+90.0)
            if temp > -30.0 and temp < 0.0:
                angel_p.append(temp)
            if temp > 30.0:
                angel_p.append(temp-90.0)


        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 0), 2)

    if angel_n != [] and angel_p == []:
        angel = sum(angel_n) / len(angel_n)
    if angel_p != [] and angel_n == []:
        angel = sum(angel_p) / len(angel_p)

    angel = float(int(angel))

    return angel, img

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

        cv2.line(img_g, (x1, y1), (x2, y2), (0, 0, 0), 2)

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

from uart import uart
import matplotlib.pyplot as ply
if __name__ == '__main__':
    Uart = uart()
    data = []
    capture = cv2.VideoCapture(0)
    while True:
        ret, frame = capture.read()
        cv2.imshow('origin', frame)
        img = pre_handle(frame)
        angel,img = get_rotate_angel_3(img)

        Uart.send_all([0.0,0.0, angel], 0)

        # data.append(angel)
        # x = np.arange(0, len(list(data)))
        # plt.plot(x, data)
        # plt.pause(0.0001)


        cv2.imshow('lala', img)
        cv2.waitKey(1)
        print(angel)

# import matplotlib.pyplot as plt
# if __name__ == '__main__':
#     data = np.load('data.npy')
#     x = np.arange(0, len(list(data)))
#     plt.plot(x, data)
#     plt.show()





