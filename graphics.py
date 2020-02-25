#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/7/29 9:31
# @File    : graphics.py
# @Software: PyCharm

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Graphics():
    def __init__(self):
        self.data = []


    def chess_list(self, x, y):
        type_data = 0 # 1棋格 2障碍(横) 3障碍(竖)
        x_int, y_int = x // 100, y // 100
        x_remind, y_remind = x % 100, y % 100

        if x_remind>=20 and x_remind<=100 and y_remind>=20 and y_remind<=100:
            type_data = 1

        if type_data == 1:
            data = [x_int, y_int]
 #           if data not in self.data:
            self.data.append(data)

        if x_remind >=0 and x_remind < 20 and y_remind>=20 and y_remind<=100:
            type_data = 3
            self.data.append([type_data, x_int, y_int])
        if x_remind>=20 and x_remind<=100 and y_remind>=0 and y_remind< 20:
            type_data = 2
            self.data.append([type_data, x_int, y_int])


    def pop_list(self):
        if len(self.data) >= 2:
            self.data = self.data[:-1]
        else:
            self.data = []

    def data_to_num(self):
        num = []
        for data in self.data:
            if len(data) == 2:
                num.append(data[0]+data[1]*8+1)
            elif len(data) == 3:
                num.append(data)
        return num

    def get_rect_param(self, position):
        a = position[0] * 100 + 0 + 20
        b = position[1] * 100 + 0 + 20
        c = 80
        d = 80

        return a, b, c, d

    def get_barrier_param(self, position):
        if position[0] == 2:
            a = position[1] * 100 + 0 + 20
            b = position[2] * 100 + 0
            c = 80
            d = 20
        elif position[0] == 3:
            a = position[1] * 100 + 0
            b = position[2] * 100 + 0 + 20
            c = 20
            d = 80

        return a, b, c, d

    def get_pos(self, num):
        for i in range(8):
            for j in range(8):
                if i*8+j+1 == num:
                    return [j, i]

    def draw(self, qp):
        for i in range(1,65,1):
            string = ''
            for index, data in enumerate(self.data):
                if data == self.get_pos(i) and len(data) == 2:
                    string += str(index+1) + ' '
            if string != '':
                a, b, c ,d = self.get_rect_param(self.get_pos(i))
                qp.setBrush(QColor(0, 255, 255))
                qp.drawRect(a, b, c, d)
                qp.setPen(QColor(255, 255,0))
                qp.setFont(QFont("Decorative", 15))
                qp.drawText(QRect(a, b, c, d), Qt.AlignCenter, string)

        for data in self.data:
            if len(data) == 3:
                a, b, c, d = self.get_barrier_param(data)
                qp.setBrush(QColor(0, 255, 255))
                qp.drawRect(a, b, c, d)

    def format_barrier(self, dis, data):
        dir = ''
        number = 0

        x_dis, y_dis = self.get_pos(dis)
        y = data[2]
        x = data[1]
        if dis == 2 or dis == 3 or dis == 4 or dis == 5 or dis == 6 or dis == 7:
            if data[0] == 2:
                dis = 'down'
                number = max(y-1,0)*8+x+1
            elif data[0] == 3:
                if x_dis < x:
                    dis = 'right'
                    number = y*8+max(x-1,0)+1
                else:
                    dis = 'left'
                    number = y*8+x+1
        elif dis == 57 or dis == 58 or dis == 59 or dis == 60 or dis == 61 or dis == 62 or dis == 63 or dis == 64:
            if data[0] == 2:
                dis = 'up'
                number = y*8+x+1
            elif data[0] == 3:
                if x_dis < x:
                    dis = 'right'
                    number = y*8+max(x-1,0)+1
                else:
                    dis = 'left'
                    number = y*8+x+1
        elif dis == 8 or dis == 16 or dis == 24 or dis == 32 or dis == 40 or dis == 48 or dis == 56:
            if data[0] == 2:
                if y_dis < y:
                    dis = 'down'
                    number = max(y-1,0)*8+x+1
                else:
                    dis = 'up'
                    number = y*8+x+1
            elif data[0] == 3:
                dis = 'left'
                number = y*8+x+1
        elif dis == 1 or dis == 9 or dis == 17 or dis == 25 or dis == 33 or dis == 41 or dis == 49:
            if data[0] == 2:
                if y_dis < y:
                    dis = 'down'
                    number = max(y-1,0)*8+x+1
                else:
                    dis = 'up'
                    number = y*8+x+1
            elif data[0] == 3:
                dis = 'right'
                number = y*8+x

        return dis, number


if __name__ == '__main__':
    graph = Graphics()
    graph.chess_list(220, 220)
    graph.chess_list(220, 220)
    graph.chess_list(320, 220)
    graph.chess_list(220, 320)
    print(graph.data)
