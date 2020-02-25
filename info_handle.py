#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/6/6 14:28
# @File    : info_handle.py
# @Software: PyCharm

import numpy as np
import queue
import time


OUT      = 0
BOUNDARY = 1
IN       = 2

class number_confirm():
    def __init__(self, initial):
        self.state = OUT
        self.initial = initial
        self.boundary_list = []
        self.path = []
        self.num_path = []
        self.num_map = np.zeros((8,8), dtype=np.int)
        self.map = np.zeros((17, 17), dtype=np.int)
        self.move_ops = move_optim()

        #创建地图数字表
        for i in range(8):
            for j in range(8):
                self.num_map[i,j] = i*8 + j + 1

        # 创建边界表
        for i in range(8):
            self.boundary_list.append(self.num_map[7,i])
            self.boundary_list.append(self.num_map[0,i])
        for i in range(6):
            self.boundary_list.append(self.num_map[i+1,0])
            self.boundary_list.append(self.num_map[i+1,7])

    #设置地图
    def set_map(self, map):
        self.map = map

    #通过数字获得数字地图上的坐标
    def get_num_pos(self, number):
        for i in range(8):
            for j in range(8):
                if self.num_map[i,j] == number:
                    return [i,j]

    #通过数字获得地图上的坐标
    def get_pos(self, number):
        number_pos = self.get_num_pos(number)
        return [number_pos[0]*2+1, number_pos[1]*2+1]

    #获得与数字相邻的9个数字
    def get_near(self, number):
        number_list = []
        position = self.get_num_pos(number)

        number_list.append(self.num_map[max(position[0] - 1, 0), max(position[1] - 1, 0)])
        number_list.append(self.num_map[max(position[0]    , 0), max(position[1] - 1, 0)])
        number_list.append(self.num_map[min(position[0] + 1, 7), max(position[1] - 1, 0)])
        number_list.append(self.num_map[max(position[0] - 1, 0), max(position[1]    , 0)])
        number_list.append(self.num_map[max(position[0]    , 0), max(position[1]    , 0)])
        number_list.append(self.num_map[min(position[0] + 1, 7), max(position[1]    , 0)])
        number_list.append(self.num_map[max(position[0] - 1, 0), min(position[1] + 1, 7)])
        number_list.append(self.num_map[max(position[0]    , 0), min(position[1] + 1, 7)])
        number_list.append(self.num_map[min(position[0] + 1, 7), min(position[1] + 1, 7)])

        return number_list

    def get_direct(self, path, direct, location, angel, limit = [150, 150]):
        x0, y0 = self.get_num_pos(self.initial)
        x = y = 0.0
        direct_flag = 0

        speed = 3.0
        if len(path) >= 2:
            direct_flag = 1
            direct2 = path[1]
            if (direct2[0] - direct[0]) == (direct[0] - x0) and \
                (direct2[1] - direct[1]) == (direct[1] - y0):
                speed = 5.0

        if direct[0] != x0:
            x = -speed * (direct[0] - x0) / abs(direct[0] - x0)
        if direct[1] != y0:
            y = speed * (direct[1] - y0) / abs(direct[1] - y0)
        if direct[0] == x0 and direct[1] == y0:
            angel = angel / 1.0
            if location[1] != limit[1]:
                x = -1.0*(location[1] - limit[1]) / abs(location[1] - limit[1])
            else:
                x = 0.0
            # if direct_flag == 1:
            #     if direct2[1] == direct[1]:
            #         x = round(0.5* -(location[1] - limit[1]) / abs(location[1] - limit[1]), 1)


            if location[0] != limit[0]:
                y = 1.0*(location[0] - limit[0]) / abs(location[0] - limit[0])
            else:
                y = 0.0
            # if direct_flag == 1:
            #     if direct2[0] == direct[0]:
            #         y = round(0.5 *  (location[0] - limit[0]) / abs(location[0] - limit[0]))

        if abs(x) == 3.0 and abs(y) == 3.0:
            print(x0,y0)
        return [x, y, angel]



    def get_possibility(self, number):
        real_number = self.initial

        # if self.state == BOUNDARY:
        #     if number in self.get_near(self.initial) and number != self.initial:
        #         real_number = number
        #         self.initial = real_number
        #         #改变状态 IN
        #         self.state = IN
        #
        # if self.state == OUT or self.state == BOUNDARY:
        #     if number in self.boundary_list:
        #         self.initial = number
        #         #改变状态 BOUNDARY
        #         self.state = IN #BOUNDARY
        #
        # elif self.state == IN:
        if number == self.num_map[self.num_path[0][0], self.num_path[0][1]]:
            real_number = number
            self.initial = real_number
        else:
            real_number = self.initial

        return real_number

    #通过坐标获得地图路径
    def get_path(self, map, origin, direct):
        self.set_map(map)
        self.move_ops.set_map(self.map)

        if origin[0] == direct[0] and origin[1] == direct[1]:
            if direct[0] % 2 == 1 and direct[1] % 2 == 1:
                self.num_path.append([direct[0]//2, direct[1]//2])
            return [direct], self.num_path

        path = self.move_ops.get_pathlist(origin, direct)

        self.path.extend(path)

        for temp in self.path:
            if temp[0] % 2 == 1 and temp[1] % 2 == 1:
                self.num_path.append([temp[0]//2, temp[1]//2])
        return self.path, self.num_path

    #将地图路径转化为数字路径
    def path_to_numpath(self):
        num_path = []

        for temp in self.num_path:
            num_path.append(self.num_map[temp[0], temp[1]])
        return num_path


    def get_state(self):
        return self.state

    def pop_numpath(self):
        self.num_path = self.num_path[1:]
        return self.num_path




class move_optim():
    def __init__(self):
        self.map = np.zeros((17, 17), dtype=np.int)

        for i in range(17):
            for j in range(17):
                if i%2 == 0 and j%2 == 0:
                    self.map[i,j] = 1
        # 地图为空
        self.EMPTY = 0
        # 路径列表
        self.pathlist = []


    def set_map(self, map):
        self.map = map

    # 获得路径
    def get_pathlist(self, origin, dist):
        # 队列
        que = queue.Queue(100)
        # 路径信息
        path = []
        # 访问的关联性
        visit = {}
        # 起始点坐标
        sx, sy = origin[0], origin[1]
        # 终点坐标
        gx, gy = dist[0], dist[1]
        # 距离矩阵
        d = np.zeros((17, 17), dtype=np.int)
        # 移动方向
        dx = [1, 0, -1, 0]
        dy = [0, 1, 0, -1]
        INF = 9999

        #寻找路径函数
        def bfs():
            for i in range(17):
                for j in range(17):
                    d[i, j] = INF

            que.put([sx, sy])
            d[sx, sy] = 0

            while (que.qsize()):
                p = que.get()
                if p[0] == gx and p[1] == gy:
                    break

                for i in range(4):
                    nx = p[0] + dx[i]
                    ny = p[1] + dy[i]

                    if 0 <= nx and 0 <= ny and nx < 17 and ny < 17 and \
                            self.map[nx, ny] == self.EMPTY and d[nx, ny] == INF:
                        que.put([nx, ny])
                        visit[str([nx, ny])] = p
                        d[nx, ny] = d[p[0], p[1]] + 1

            #添加路径信息
            path.append([gx, gy])
            father = visit[str([gx, gy])]
            while True:
                if father[0] == sx and father[1] == sy:
                    break

                path.append(father)
                father = visit[str(father)]
            path.reverse()

        bfs()
        return path





if __name__ == '__main__':
    la = number_confirm(0)
    la.num_path = [[0,2],[0,2],[1,2]]
    xi = la.get_possibility(1)
    xi = la.get_possibility(2)
    xi = la.get_possibility(2)
    xi = la.get_possibility(2)

    xi = la.get_possibility(3)
    xi = la.get_possibility(63)
    xi = la.get_possibility(64)
    xi = la.get_possibility(64)
    xi = la.get_possibility(20)
    xi = la.get_possibility(10)
    xi = la.get_possibility(56)

    # wa = move_optim([1,1],[1,1])
    # path = wa.get_pathlist([1,1],[15,15])
    # print(path)
    # path = wa.get_pathlist([5, 1], [15, 7])
    # print(path)

    # map = np.zeros((17, 17), dtype=np.int)
    #
    # for i in range(17):
    #     for j in range(17):
    #         if i % 2 == 0 and j % 2 == 0:
    #             map[i, j] = 1
    #
    # la = number_confirm(10)
    # _, ha = la.get_path(map, la.get_pos_by_num(1), la.get_pos_by_num(8))
    # num_path = la.path_to_numpath()
    # la.get_pos_by_num(1)
    # print(la.path)
    # print(num_path)
    # print(ha)
