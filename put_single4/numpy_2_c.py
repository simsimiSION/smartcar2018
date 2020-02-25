#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/8/19 23:48
# @File    : numpy_2_c.py
# @Software: PyCharm

import numpy as np
from ctypes import *


def Convert1DToCArray(TYPE, ary):
    arow = TYPE(*ary.tolist())
    return arow

def Convert2DToCArray(ary):
    ROW = c_int * len(ary[0])
    rows = []
    for i in range(len(ary)):
        rows.append(Convert1DToCArray(ROW, ary[i]))
    MATRIX = ROW * len(ary)
    return MATRIX(*rows)


a = np.array([[1, 2, 2], [1, 3, 4]])
caa = Convert2DToCArray(a)


def ShowCArrayArray(caa):
    for row in caa:
        for col in row:
            print(col)


print(type(caa))
ShowCArrayArray(caa)