#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/6/15 13:32
# @File    : gui.py
# @Software: PyCharm

import sys, random
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import time
from info_handle import number_confirm
from handle2 import *
from handle import *
from go import *
from graphics import  Graphics
from barrier_handle import barrier_detect
from knn import knn
from uart import uart
import cv2
import time
import math
import datetime


WAIT = 0
RUNNING = 1
PRE_BACKING = 2
BACKING = 3
PRE_RUNNING = 4
RUNNING_GO = 5
FINISH = 6
ARMING = 7

UP = 0
DOWN = 1

PUT = 1
TAKE = 2

QUEEN = 1
BARRIER = 2
CHESS_MOVE = 3
TASK3 = 4

GO_WAIT = 0
GO_UP = 1
GO_DOWN = 2
GO_LEFT = 3
GO_RIGHT = 4
GO_ROTATE_P = 5
GO_ROTATE_N = 6

MAIN_WAIT = 0
MAIN_IN   = 1
MAIN_RUN  = 2
MAIN_OUT  = 3

last_direct = []


class Map_gui(QWidget):
    def __init__(self):
        self.temp = 0
        self.data = []
        # *************************#
        self.main_status = MAIN_WAIT
        self.main_status_count = 0
        self.go = True
        self.go_status = GO_WAIT
        self.model = knn()
        self.optim = number_confirm(57)
        self.bd = barrier_detect()
        self.uart = uart()
        self.graph = Graphics()
        self.img = '加入视频提取的图像'
        self.status = WAIT
        self.last_status = WAIT
        self.button_status = UP
        self.dis = 25     # 目标数字
        self.dis_list = [self.dis]
        self.barrier_list = ['up']
        self.last_angel = 0
        self.last_position = [7,0]  # 行进中上一次的位置
        self.barrier_dir = 'none'
        self.arm_status = 0
        self.arm_count = 0
        self.system_mode = QUEEN
        self.mode = 0    #1:put 2:take
        self.queen_mode = TAKE
        self.press = False
        self.barrier_flag = 0
        # *************************#
        self.debug = False
        self.capture = cv2.VideoCapture(0)
        # *************************#
        # 数字上次的位置坐标
        self.last_location = [150,150]
        # 小车的位置 [数字坐标,x,y]
        self.pos = [64, 150, 150]
        # 障碍 [type, i ,j]
        self.bundary_list = []#[, [3,2,2]]
        # 棋子 [number]
        self.chess_list = []#[15]
        # 棋盘
        self.map = np.zeros((17, 17), dtype=np.int)
        # 路径
        self.path = []
        # *************************#
        super(Map_gui, self).__init__()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.interrupt)
        self.timer.start(25)
        self.init_ui()

    def init_ui(self):
        self.setGeometry(500,100,1000,820)
        self.setWindowTitle('map')

        # 提示框
        self.label = QLabel(self)
        self.label.setText('请输入目标点数字或障碍')
        self.label.move(850, 20)
        self.label.resize(100, 30)
        # create textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(850, 55)
        self.textbox.resize(40, 30)
        # button
        self.button = QPushButton('确认', self)
        self.button.move(850, 90)
        self.button.resize(80, 30)
        self.button.clicked.connect(self.on_click)
        # combobox
        self.combox = QComboBox(self)
        self.combox.addItem('queen')
        self.combox.addItem('barrier')
        self.combox.addItem('chess_move')
        self.combox.move(900, 55)
        self.combox.resize(40, 30)
        self.combox.activated[str].connect(self.combox_click)

        # button saveimage
        self.button_save_image = QPushButton('保存图像', self)
        self.button_save_image.move(850,  120)
        self.button_save_image.resize(80, 30)
        self.button_save_image.clicked.connect(self.save_image)

        # button reset
        self.button_reset = QPushButton('重置', self)
        self.button_reset.move(850,  150)
        self.button_reset.resize(80, 30)
        self.button_reset.clicked.connect(self.reset)

        # button add barrier
        self.button_add_barrier = QPushButton('加障碍', self)
        self.button_add_barrier.move(850,  180)
        self.button_add_barrier.resize(40, 30)
        self.button_add_barrier.clicked.connect(self.add_barrier)

        # button delete barrier
        self.button_del_barrier = QPushButton('删障碍', self)
        self.button_del_barrier.move(890,  180)
        self.button_del_barrier.resize(40, 30)
        self.button_del_barrier.clicked.connect(self.del_barrier)

        # button add chess
        self.button_add_chess = QPushButton('加棋子', self)
        self.button_add_chess.move(850,  210)
        self.button_add_chess.resize(40, 30)
        self.button_add_chess.clicked.connect(self.add_chess)

        # button delete chess
        self.button_del_chess = QPushButton('删棋子', self)
        self.button_del_chess.move(890,  210)
        self.button_del_chess.resize(40, 30)
        self.button_del_chess.clicked.connect(self.del_chess)

        # press enable
        self.press_enable = QPushButton('触屏使能', self)
        self.press_enable.move(850,  240)
        self.press_enable.resize(40, 30)
        self.press_enable.clicked.connect(self.press_able)

        # press revoke
        self.press_revoke = QPushButton('触屏关闭', self)
        self.press_revoke.move(890,  240)
        self.press_revoke.resize(40, 30)
        self.press_revoke.clicked.connect(self.press_revo)

        # log
        self.log = QLabel(self)
        self.log.setText('日志信息')
        self.log.move(850, 390)
        self.log.resize(100, 150)
        # img
        self.imageview_ori = QLabel(self)
        self.imageview_ori.move(850, 570)
        self.imageview_ori.resize(100, 100)

        self.imageview_bin = QLabel(self)
        self.imageview_bin.move(850, 700)
        self.imageview_bin.resize(100, 100)


        self.show()

    @pyqtSlot()
    def save_image(self):
        ret, frame = self.capture.read()
        img = pre_handle(frame)
        cv2.imwrite('./'+time.strftime('%H%M%S',time.localtime(time.time()))+'.jpg', img)

    @pyqtSlot()
    def on_click(self):
        self.go = True
        self.main_status = MAIN_IN

        if self.system_mode == QUEEN:
            if self.press == False:
                val = []
                textboxValue = self.textbox.text()
                try:
                    textboxValue = textboxValue.split('|')
                    for text in textboxValue:
                        text = int(text)
                        if text < 1 or text > 64:
                            reply = QMessageBox.information(self, "警告", "格式错误", QMessageBox.Yes | QMessageBox.No)
                        else:
                            val.append(text)
                    self.dis_list = val
                    self.button_status = DOWN
                except:
                    reply = QMessageBox.information(self, "警告", "格式错误", QMessageBox.Yes | QMessageBox.No)
            else:
                self.dis_list = self.graph.data_to_num()
                self.button_status = DOWN

        elif self.system_mode == BARRIER:
            val_num = []
            val_dir = []
            textboxValue = self.textbox.text()
            try:
                textboxValue = textboxValue.split('|')
                for text in textboxValue:
                    num, dir = text.split('-')
                    num = int(num)
                    if num < 1 or num > 64 or (not (dir == 'up' or dir == 'down' or dir == 'left' or dir == 'right')):
                        reply = QMessageBox.information(self, "警告", "格式错误", QMessageBox.Yes | QMessageBox.N)
                    else:
                        val_num.append(num)
                        val_dir.append(dir)
                self.dis_list = val_num
                self.barrier_list = val_dir
                for n, d in zip(self.dis_list, self.barrier_list):
                    self.to_boundary_list(n, d)

                self.button_status = DOWN
            except:
                reply = QMessageBox.information(self, "警告", "格式错误", QMessageBox.Yes | QMessageBox.No)
        elif self.system_mode == CHESS_MOVE:
            if self.press == False:
                val = []
                textboxValue = self.textbox.text()
                try:
                    textboxValue = textboxValue.split('|')
                    for text in textboxValue:
                        text = int(text)
                        if text < 1 or text > 64:
                            reply = QMessageBox.information(self, "警告", "格式错误", QMessageBox.Yes | QMessageBox.No)
                        else:
                            val.append(text)
                    self.dis_list = val
                    self.button_status = DOWN
                except:
                    reply = QMessageBox.information(self, "警告", "格式错误", QMessageBox.Yes | QMessageBox.No)
            else:
                self.dis_list = self.graph.data_to_num()
                self.button_status = DOWN

    @pyqtSlot()
    def reset(self):
        self.main_status = MAIN_WAIT
        self.main_status_count = 0
        self.go = True
        self.last_position = [7,0]
        self.dis_list = []
        self.press = False
        self.graph.data = []
        self.path = []
        self.barrier_list = []
        self.button_status = UP
        self.button_status = UP
        self.status = WAIT
        self.optim.initial = 57
        self.optim.num_path = []
        self.optim.path = []
        self.barrier_dir = 'none'
        self.arm_status = 0
        self.arm_count = 0
        self.mode = 0
        self.queen_mode = TAKE

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Z:
            if self.go == True:
                self.go = False
                print(' human control !!!')
            else:
                self.go = True
                print(' computer control !!!')
        if e.key() == Qt.Key_A:
            self.go_status = GO_LEFT
        if e.key() == Qt.Key_D:
            self.go_status = GO_RIGHT
        if e.key() == Qt.Key_W:
            self.go_status = GO_UP
        if e.key() == Qt.Key_S:
            self.go_status = GO_DOWN
        if e.key() == Qt.Key_Q:
            self.go_status = GO_ROTATE_N
        if e.key() == Qt.Key_E:
            self.go_status = GO_ROTATE_P

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_A:
            self.go_status = GO_WAIT
        if e.key() == Qt.Key_D:
            self.go_status = GO_WAIT
        if e.key() == Qt.Key_W:
            self.go_status = GO_WAIT
        if e.key() == Qt.Key_S:
            self.go_status = GO_WAIT
        if e.key() == Qt.Key_Q:
            self.go_status = GO_WAIT
        if e.key() == Qt.Key_E:
            self.go_status = GO_WAIT

    def mousePressEvent(self, event):
        if self.press:
            if event.button() == Qt.LeftButton:
                self.graph.chess_list(event.x(), event.y())
                self.update()

    @pyqtSlot()
    def add_barrier(self):
        value, ok = QInputDialog.getText(self, "添加障碍", "格式:数字|方向\n eg: 23|up", QLineEdit.Normal, '23|up')
        if ok:
            try:
                num, dir = value.split('|')
                num = int(num)

                if num < 1 or num > 64:
                    reply = QMessageBox.information(self, "警告", "格式错误", QMessageBox.Yes | QMessageBox.No)
                elif dir == 'up' or dir == 'down' or dir == 'left' or dir == 'right':
                    position = self.optim.get_num_pos(num)

                    type = -1
                    bias = 0
                    if dir == 'up' or dir == 'down':
                        type = 2
                        if dir == 'down':
                            bias = 1
                        barrier = [type, position[1], position[0]+bias]
                    elif dir == 'left' or dir == 'right':
                        type = 3
                        if dir == 'right':
                            bias = 1
                        barrier = [type, position[1]+bias, position[0]]

                    if barrier not in self.bundary_list:
                        self.bundary_list.append(barrier)
                    else:
                        reply = QMessageBox.information(self,
                                                        "警告",
                                                        "重复添加了障碍",
                                                        QMessageBox.Yes | QMessageBox.No)

                else:
                    reply = QMessageBox.information(self,"警告","格式错误",QMessageBox.Yes | QMessageBox.No)

            except:
                reply = QMessageBox.information(self, "警告", "格式错误", QMessageBox.Yes | QMessageBox.No)
        self.update()

    @pyqtSlot()
    def del_barrier(self):
        value, ok = QInputDialog.getText(self, "删除障碍", "格式:数字|方向\n eg: 23|up", QLineEdit.Normal, '23|up')
        if ok:
            try:
                num, dir = value.split('|')
                num = int(num)

                if num < 1 or num > 64:
                    reply = QMessageBox.information(self, "警告", "格式错误", QMessageBox.Yes | QMessageBox.No)
                elif dir == 'up' or dir == 'down' or dir == 'left' or dir == 'right':
                    position = self.optim.get_num_pos(num)

                    type = -1
                    bias = 0
                    if dir == 'up' or dir == 'down':
                        type = 2
                        if dir == 'down':
                            bias = 1
                        barrier = [type, position[1], position[0]+bias]
                    elif dir == 'left' or dir == 'right':
                        type = 3
                        if dir == 'right':
                            bias = 1
                        barrier = [type, position[1]+bias, position[0]]

                    if barrier in self.bundary_list:
                        self.bundary_list.remove(barrier)
                    else:
                        reply = QMessageBox.information(self,
                                                        "警告",
                                                        "没有这个障碍",
                                                        QMessageBox.Yes | QMessageBox.No)

                else:
                    reply = QMessageBox.information(self, "警告", "格式错误", QMessageBox.Yes | QMessageBox.No)

            except:
                reply = QMessageBox.information(self, "警告", "格式错误", QMessageBox.Yes | QMessageBox.No)
        self.update()

    @pyqtSlot()
    def add_chess(self):
        value, ok = QInputDialog.getInt(self, "添加棋子", "格式:数字\n eg: 23", 23, 1, 64, 1)
        if ok:
            if value not in self.chess_list:
                self.chess_list.append(value)
            else:
                reply = QMessageBox.information(self, "警告", "已经有该棋子", QMessageBox.Yes | QMessageBox.No)
        self.update()

    @pyqtSlot()
    def del_chess(self):
        value, ok = QInputDialog.getInt(self, "删除棋子", "格式:数字\n eg: 23", 23, 1, 64, 1)
        if ok:
            if value in self.chess_list:
                self.chess_list.remove(value)
            else:
                reply = QMessageBox.information(self, "警告", "没有该棋子", QMessageBox.Yes | QMessageBox.No)
        self.update()

    @pyqtSlot()
    def press_able(self):
        if self.press == False:
            self.press = True
            reply = QMessageBox.information(self, "警告", "使能触屏", QMessageBox.Yes | QMessageBox.No)
        elif self.press == True:
            self.press = False
            reply = QMessageBox.information(self, "警告", "关闭触屏", QMessageBox.Yes | QMessageBox.No)

    @pyqtSlot()
    def press_revo(self):
        self.graph.pop_list()

    def to_boundary_list(self, num, dir):
        position = self.optim.get_num_pos(num)
        barrier = []
        type = -1
        bias = 0

        if dir == 'up' or dir == 'down':
            type = 2
            if dir == 'down':
                bias = 1
            barrier = [type, position[1], position[0]]
        elif dir == 'left' or dir == 'right':
            type = 3
            if dir == 'right':
                bias = 1
            barrier = [type, position[1]+bias, max(position[0]-1, 0)]

        if barrier not in self.bundary_list and barrier != []:
            self.bundary_list.append(barrier)

    def combox_click(self, text):
        if text == 'queen':
            self.system_mode = QUEEN
        elif text == 'barrier':
            self.system_mode = BARRIER
        elif text == 'chess_move':
            self.system_mode = CHESS_MOVE

    def get_rect_param(self, position, type):
        a = b = c = d = 0

        if type == 1:    # 棋格
            a = position[0] * 100 + 0 + 20
            b = position[1] * 100 + 0 + 20
            c = 80
            d = 80

        elif type == 2:  # 障碍(横)
            a = position[0] * 100 + 0 + 20
            b = position[1] * 100 + 0
            c = 80
            d = 20
        elif type == 3:  # 障碍(竖)
            a = position[0] * 100 + 0
            b = position[1] * 100 + 0 + 20
            c = 20
            d = 80
        else:
            pass

        return a, b, c, d

    def get_pos(self):
        x = y = 0
        for i in range(8):
            for j in range(8):
                if i*8+j+1 == self.pos[0]:
                    x = j
                    y = i
                    break

        a = max(x * 100 + 0 + 20 + int(self.pos[1]*80/300) - 10, 0)
        b = max(y * 100 + 0 + 20 + int(self.pos[2]*80/300) - 10, 0)
        c = 20
        d = 20
        return a, b, c, d

    def set_pos(self, position):
        self.pos = position
        self.update()

    def interrupt(self):
        # 小车方向给定==================================================================#
        # ============================================================================#
        #读取图像中的图片数字
        start = time.time()
        ret, frame = self.capture.read()
        img = pre_handle(frame)	
        angel, img_angel = get_rotate_angel_3(img)
        self.last_angel = float(int(angel * 1.0 + self.last_angel * 0.0))

        number ,location, img_origin, img_show = getNumber(img, self.model)

        direct = []

        if location != []:
            self.last_location = location
        if location == []:
            location = self.last_location

        # DETECT ============================================================================
        to_map = self.to_map()
        if len(self.dis_list) != 0:
            self.dis = self.dis_list[0]
        else:
            self.dis = 57

        if self.system_mode == BARRIER and self.barrier_list != []:
            self.barrier_dir = self.barrier_list[0]


        if self.main_status == MAIN_IN:
             move_in_status, self.button_status, self.path, self.optim, self.mode, direct, self.last_position = move_in(
                 number, location, direct, img_show, img_origin, self.status, self.button_status, self.dis, self.queen_mode, self.mode, self.last_angel, self.path, self.optim, to_map, self.last_position)
             if move_in_status:
                 self.dis_list = self.dis_list[1:]
                 self.main_status = MAIN_RUN

        elif self.main_status == MAIN_RUN:

            if self.arm_count < 3:
                if self.system_mode == QUEEN:
                    self.status, self.button_status, self.path, self.optim, self.mode, direct, self.last_position = queue_move(
                       number, location, direct, img_show, img_origin, self.status, self.button_status, self.dis, self.queen_mode, self.mode, self.last_angel, self.path, self.optim, to_map, self.last_position)
                elif self.system_mode == BARRIER:
                    if self.queen_mode != 3:
                        self.status, self.button_status, self.path, self.optim, self.mode, direct, self.bd, self.barrier_dir, self.barrier_flag = barrier(
                            number, location, direct, img_show, img_origin, self.status, self.button_status, self.dis, self.queen_mode, self.mode, self.last_angel, self.path, self.optim, to_map, self.bd, self.barrier_dir, self.barrier_flag)
                    else:
                         self.status, self.button_status, self.path, self.optim, self.mode, direct, self.last_position = queue_move(
                       number, location, direct, img_show, img_origin, self.status, self.button_status, self.dis, self.queen_mode, self.mode, self.last_angel, self.path, self.optim, to_map, self.last_position)
                elif self.system_mode == CHESS_MOVE:
                     self.status, self.button_status, self.path, self.optim, self.mode, direct, self.last_position = queue_move(
                       number, location, direct, img_show, img_origin, self.status, self.button_status, self.dis, self.queen_mode, self.mode, self.last_angel, self.path, self.optim, to_map, self.last_position)
            if self.status == RUNNING_GO or self.status == BACKING:
                self.main_status = MAIN_OUT
        elif self.main_status == MAIN_OUT:
            self.status, self.button_status, self.path, self.optim, self.mode, direct, self.last_position = move_out(
                 number, location, direct, img_show, img_origin, self.status, self.button_status, self.dis, self.queen_mode, self.mode, self.last_angel, self.path, self.optim, to_map, self.last_position)
            self.main_status_count += 1
            if self.main_status_count == 35:
                self.main_status_count = 0
                self.main_status = MAIN_WAIT
        elif self.main_status == MAIN_WAIT:
            self.optim.state = 1

        # arm handle ===========================
        if self.status == ARMING and self.last_status != ARMING:
            self.arm_status = self.mode
            self.arm_count += 1
        if self.arm_count != 0:
            self.arm_count += 1
        if self.arm_count > 20:
            self.arm_status = 0
        if self.arm_count > 70:  # 3second
            self.arm_count = 0

        if self.system_mode == QUEEN:
            if self.status == FINISH:
                if len(self.dis_list) == 2:
                    self.queen_mode = 3
                    self.dis_list = self.dis_list[1:]
                    self.status = WAIT

                if len(self.dis_list) > 2:
                    self.dis_list = self.dis_list[1:]
                    self.status = WAIT

                if len(self.dis_list) <= 5 and self.queen_mode != 3:
                    self.queen_mode = PUT
            elif self.status == RUNNING_GO:
                self.queen_mode = 3
                self.status = WAIT

        elif self.system_mode == BARRIER:
            if self.status == BACKING:
                if len(self.dis_list) == 2:
                    self.queen_mode = 3
                    self.dis_list = self.dis_list[1:]
                    self.status = WAIT

                if len(self.dis_list) > 2:
                    self.dis_list = self.dis_list[1:]
                    self.barrier_list = self.barier_list[1:]
                    self.status = WAIT

        elif self.system_mode == CHESS_MOVE:
            if self.status == FINISH:
                if len(self.dis_list) == 3:
                    self.dis_list = self.dis_list[1:]
                    self.status = WAIT
                    self.queen_mode = PUT
                elif len(self.dis_list) == 2:
                    self.queen_mode = 3
                    self.dis_list = self.dis_list[1:]
                    self.status = WAIT
            if self.status == RUNNING_GO:
                if len(self.dis_list) == 1:
                    self.queen_mode = 3
                    self.status = WAIT

        # ========================================
        # uart direct

        if self.go:
            if self.main_status == MAIN_WAIT:
                self.uart.send_all([0.0, 0.0, 0.0], self.arm_status)
            elif self.main_status == MAIN_RUN:
                if self.status == WAIT or self.status == PRE_BACKING or self.arm_count != 0:
                    self.uart.send_all([0.0, 0.0, 0.0], self.arm_status)

                if direct != [] and (self.status == RUNNING or self.status == ARMING) and self.arm_count == 0:
                    self.uart.send_all(direct, self.arm_status)

            elif self.main_status == MAIN_IN or self.main_status == MAIN_OUT:
                    self.uart.send_all(direct, self.arm_status)

        else:
            if self.go_status == GO_WAIT:
                self.uart.send_all([0.0, 0.0, 0.0], self.arm_status)
            elif self.go_status == GO_DOWN:
                self.uart.send_all([-3.0, 0.0, 0.0], self.arm_status)
            elif self.go_status == GO_UP:
                self.uart.send_all([3.0, 0.0, 0.0], self.arm_status)
            elif self.go_status == GO_LEFT:
                self.uart.send_all([0.0, -3.0, 0.0], self.arm_status)
            elif self.go_status == GO_RIGHT:
                self.uart.send_all([0.0, 3.0, 0.0], self.arm_status)
            elif self.go_status == GO_ROTATE_P:
                self.uart.send_all([0.0, 0.0, 20.0], self.arm_status)
            elif self.go_status == GO_ROTATE_N:
                self.uart.send_all([0.0, 0.0, -15.0], self.arm_status)

        #
        # if self.status == RUNNING or self.status == PRE_BACKING or self.status == FINISH:
        #     print(direct)
        # # 图片============================================================================#
        #   原始图像显示
        img_origin = cv2.resize(img_origin, (100, 100), interpolation=cv2.INTER_AREA)
        image = QImage(img_origin[:], img_origin.shape[1], img_origin.shape[0], img_origin.shape[1], QImage.Format_Grayscale8)
        self.imageview_ori.setPixmap(QPixmap.fromImage(image))
        #   二值化图像显示
        img_show = cv2.resize(img_show, (100, 100), interpolation=cv2.INTER_AREA)
        image = QImage(img_show[:], img_show.shape[1], img_show.shape[0], img_show.shape[1], QImage.Format_Grayscale8)
        self.imageview_bin.setPixmap(QPixmap.fromImage(image))

        # 设置小车位置
        car_pos = self.optim.get_num_pos(self.optim.initial)
        car_pos[0] += 1 if car_pos[0] < 7 else 0
        self.set_pos([self.optim.num_map[car_pos[0], car_pos[1]], 300 - location[0], 300 - location[1]])

        # 日志============================================================================#
        LOG_DATA = '日志:({} fps)\n\n'.format(str(int(1/(time.time()-start))))
        LOG_DATA += '当前为: ' + str(self.optim.initial) + '\n'
        LOG_DATA += '目标位: ' + str(self.dis) + '\n'
        LOG_DATA += 'path: '+ str(self.path) + '\n'
        LOG_DATA += 'direct: ' + str(direct) + '\n'
        if self.status == WAIT:
            LOG_DATA += '当前状态: wait'
        elif self.status == RUNNING:
            LOG_DATA += '当前状态: running'
        elif self.status == PRE_BACKING:
            LOG_DATA += '当前状态: pre_backing'
        elif self.status == BACKING:
            LOG_DATA += '当前状态: backing'
        elif self.status == PRE_RUNNING:
            LOG_DATA += '当前状态: pre_running'
        elif self.status == FINISH:
            LOG_DATA += '当前状态: finish'
        elif self.status == RUNNING_GO:
            LOG_DATA += '当前状态: running_go'
        elif self.status == ARMING:
            LOG_DATA += '当前状态: arming'
        self.log.setText(LOG_DATA)

        if self.status != self.last_status:
            self.last_status = self.status

    def paintEvent(self, e):
        qp = QPainter()

        qp.begin(self)
        self.drawMap(qp)
        self.drawPath(qp)
        self.drawPoint(qp)
        self.drawChess(qp)
        self.drawBunary(qp)
        self.drawBarrier(qp)

        if self.press:
            self.graph.draw(qp)
        qp.end()

    def drawMap(self, qp):
        col = QColor(0, 0, 0)
        col.setNamedColor('#d4d4d4')
        qp.setPen(col)

        for i in range(8):
            for j in range(8):
                a, b, c, d = self.get_rect_param([i, j], 1)
                qp.setBrush(QColor(0, 0, 255))
                qp.drawRect(a, b, c, d)
                qp.setPen(QColor(255, 255, 255))
                qp.setFont(QFont("Decorative", 30))
                qp.drawText(QRect(a,b,c,d), Qt.AlignCenter, str(i+8*j+1))

        for i in range(8):
            for j in range(9):
                a, b, c, d = self.get_rect_param([i, j], 2)
                qp.setBrush(QColor(255, 255, 255))
                qp.drawRect(a, b, c, d)

        for i in range(9):
            for j in range(8):
                a, b, c, d = self.get_rect_param([i, j], 3)
                qp.setBrush(QColor(255, 255, 255))
                qp.drawRect(a, b, c, d)

    def drawPoint(self, qp):
        qp.setBrush(QColor(0, 0, 0))
        a, b, c, d = self.get_pos()
        qp.drawRect(a, b, c, d)

    def drawChess(self, qp):
        if self.chess_list == None:
            pass
        else:
            for chess in self.chess_list:
                x = y = 0
                for i in range(8):
                    for j in range(8):
                        if i * 8 + j + 1 == chess:
                            x = j
                            y = i
                            break
                a, b, c, d = self.get_rect_param([x, y], 1)

                qp.setBrush(QColor(255, 255, 255))
                qp.drawEllipse(QRect(a+10, b+10, c-20, d-20))

    def drawBunary(self, qp):
        if self.bundary_list == []:
            pass
        else:
            for bundary in self.bundary_list:
                a, b, c, d = self.get_rect_param([bundary[1], bundary[2]], bundary[0])
                qp.setBrush(QColor(255, 0, 0))
                qp.drawRect(a, b, c, d)

    def drawPath(self, qp):
        for temp in self.path:
            a, b, c, d = self.get_rect_param([temp[1], temp[0]], 1)
            qp.setBrush(QColor(255, 0, 0))
            qp.drawRect(a, b, c, d)

    def drawBarrier(self, qp):
        if self.status == RUNNING:
            position = self.optim.get_num_pos(self.dis)
            if self.barrier_dir == 'up':
                a, b, c, d = self.get_rect_param([position[1], position[0]], 2)
                qp.setBrush(QColor(255, 0, 0))
                qp.drawRect(a, b, c, d)
            elif self.barrier_dir == 'down':
                a, b, c, d = self.get_rect_param([position[1], position[0]+1], 2)
                qp.setBrush(QColor(255, 0, 0))
                qp.drawRect(a, b, c, d)
            elif self.barrier_dir == 'left':
                a, b, c, d = self.get_rect_param([position[1], position[0]], 3)
                qp.setBrush(QColor(255, 0, 0))
                qp.drawRect(a, b, c, d)
            elif self.barrier_dir == 'right':
                a, b, c, d = self.get_rect_param([position[1]+1, position[0]], 3)
                qp.setBrush(QColor(255, 0, 0))
                qp.drawRect(a, b, c, d)

    def to_map(self):
        CHESS = 2
        BUNDARY = 1

        #没有用到的点
        for i in range(17):
            for j in range(17):
                if i % 2 == 0 and j % 2 == 0:
                    self.map[i,j] = BUNDARY

        # 检测棋子
        if self.chess_list == None:
            pass
        else:
            for chess in self.chess_list:
                x = y = 0
                for i in range(8):
                    for j in range(8):
                        if i * 8 + j + 1 == chess:
                            x = i
                            y = j
                            break
                self.map[2*x+1, 2*y+1] = CHESS

        # 检测障碍
        if self.chess_list == None:
            pass
        else:
            for bundary in self.bundary_list:
                if bundary[0] == 2:
                    self.map[bundary[2]*2, bundary[1]*2+1] = BUNDARY
                elif bundary[0] == 3:
                    self.map[bundary[2]*2+1, bundary[1]*2] = BUNDARY

        return self.map





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map_gui()
    sys.exit(app.exec_())


