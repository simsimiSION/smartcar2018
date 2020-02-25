#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/7/4 14:46
# @File    : kmeans.py
# @Software: PyCharm

import numpy as np
import time


# 获得距离参数
def dist_vec(vec_a, vec_b):
    return np.sqrt(sum(np.power(vec_a - vec_b, 2)))

def dist(vec_a, vec_b):
    return ((vec_a-vec_b)**2)**0.5

def centre(param, k=2):
    centre_list = []
    param_len = len(param)

    if param_len < k:
        raise NameError('输入的内容大小有误')

    for i in range(k):
        centre_list.append(param[i])

    return centre_list


def kmeans(param, k=2, debug=False):
    centre_list = centre(param, k=k)
    centre_list_count = np.zeros((k), dtype=np.int)
    centre_list_last = centre_list.copy()
    count = 0

    while True:
        count += 1
        if count >= 101:
            break

        map = []
        for par in param:
            temp = []
            for i in range(k):
                temp.append(dist(par, centre_list[i]))
            map.append(temp.index(min(temp)))

        for i in range(k):
            temp_list = []
            for index, temp in enumerate(map):
                if i == temp:
                    temp_list.append(param[index])

            if len(temp_list) != 0:
                centre_list[i] = sum(temp_list) / len(temp_list)
            else:
                centre_list[i] = 0
            centre_list_count[i] = len(temp_list)

        bias = 0.0
        for i in range(k):
            bias += abs(centre_list[i] - centre_list_last[i])
        if bias < 1e-4:
            break

        centre_list_last = centre_list.copy()

    if debug:
        print('中心为:')
        print(centre_list)
        print('对应中心点的数目为:')
        print(centre_list_count)

    centre_list = list(centre_list)
    centre_list_count = list(centre_list_count)
    return centre_list[centre_list_count.index(max(centre_list_count))]




if __name__ == '__main__':
    start = time.time()
    print(kmeans([86.09950625761812, 1.1457628381751022, 1.9414863909143776, 88.36342295838328, 90.0, 12.680383491819825, 90.0]))
    print(time.time()-start)