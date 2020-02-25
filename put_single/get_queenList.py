#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/8/14 1:57
# @File    : get_queenList.py
# @Software: PyCharm



def get_num(pos):
    return pos[0] * 8 + pos[1] + 1

def queenFormat(queen):
    """

    :param queen:
    :return:
    """
    array = []
    for i in range(len(queen)):
        array.append([i, queen[i]])
    return array

def conflict(state, col):
    """

    :param state:
    :param col:
    :return:
    """
    # 冲突函数，row为行，col为列
    row = len(state)
    for i in range(row):
        if abs(state[i] - col) in (0, row - i):  # 重要语句
            return True
    return False

def queens(num=8, state=()):
    """

    :param num:
    :param state:
    :return:
    """
    # 生成器函数
    for pos in range(num):
        if not conflict(state, pos):
            if len(state) == num - 1:
                yield (pos,)
            else:
                for result in queens(num, state + (pos,)):
                    yield (pos,) + result


"""获得八皇后的可行解"""
def get_queen(num):
    queen_list = []
    queen_list_ori = list(queens(8))
    for inner in queen_list_ori:
        queen_format_list = []
        queen_format = queenFormat(inner)
        for inner2 in queen_format:
            queen_format_list.append(get_num(inner2))
        queen_list.append(queen_format_list)
    return queen_list


if __name__ == '__main__':
    print(get_queen(8))