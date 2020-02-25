#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/5/28 21:22
# @File    : map.py
# @Software: PyCharm

import numpy as np

class Map():
    def __init__(self):
        self.map_w = 8
        self.map_h = 8
        self.map = np.zeros((8, 8), dtype=np.int)
        self.boundary_w = 9
        self.boundary_h = 9
        self.boundary = np.zeros((9, 9), dtype=np.int)

        temp = 1
        for i in range(8):
            for j in range(8):
                self.map[i,j] = temp
                temp += 1


    def get_map_pos(self, num):
        for i in range(self.map_h):
            for j in range(self.map_w):
                if self.map[i,j] == num:
                    return (i,j)
        return None

    def get_dir(self, ori_num, ori_pos, dis_num, size=[300,300]):
        if ori_num != dis_num:
            ori_position = self.get_map_pos(ori_num)
            dis_position = self.get_map_pos(dis_num)

            dir = [dis_position[0] - ori_position[0], dis_position[1] - ori_position[1]]
            dir = [dir[0]* size[0], dir[1]*size[1]]
        else:
            dir = [size[0]/2-ori_pos[0], size[1]/2-ori_pos[1]]

        return dir





#mapo = Map()
#print(mapo.get_dir(64, [100,100],64))
