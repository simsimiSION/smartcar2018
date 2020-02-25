#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/7/22 16:41
# @File    : least_dis.py
# @Software: PyCharm

from put_single.GA import GA
from put_single.get_queenList import get_queen
import numpy as np

def queen_print(path):
    def get_num_pos(num):
        for i in range(8):
            for j in range(8):
                if i * 8 + j + 1 == num:
                    return [i,j]

    queen_map = np.zeros((8, 8), dtype=np.int)
    for inner in path:
        inner = get_num_pos(inner)
        queen_map[inner[0], inner[1]] = 1

    for i in range(8):
        for j in range(8):
            if queen_map[i,j] == 1:
                print('X ' ,end='')
            else:
                print('. ', end='')
        print()


def get_barr(num):
    pos = []
    for i in range(8):
        for j in range(8):
            if i*8+j+1 == num:
                pos = [i, j]
                break

    up = down = left = right = 0
    if pos != []:
        # 上部分
        if pos[0] <= 4:
            # 左部分
            if pos[1] <= 4:
                if pos[0] < pos[1]:
                    up = 1
                else:
                    left = 1
            else:
                if pos[0] < 7-pos[1]:
                    up = 1
                else:
                    right = 1
        # 下部分
        else:
            # 左部分
            if pos[1] <= 4:
                if 7-pos[0] < pos[1]:
                    down = 1
                else:
                    left = 1
            else:
                if 7-pos[0] < 7 - pos[1]:
                    down = 1
                else:
                    right = 1

        if up == 1:
            return pos[1] + 1
        elif down == 1:
            return pos[1] + 57
        elif left == 1:
            return pos[0] * 8 + 1
        elif right == 1:
            return pos[0] * 8+ 8

    return []




class TSP(object):
    def __init__(self, number, aLifeCount=100 ):
        self.number = number
        self.initcitys()
        self.lifeCount = aLifeCount
        self.ga = GA(aCrossRate=0.65,
                     aMutationRate=0.1,
                     aLifeCount=self.lifeCount,
                     aGeneLength=len(self.citys),
                     aMatchFun=self.matchFun())

    def get_pos(self, num):
        for i in range(8):
            for j in range(8):
                if i * 8 + j + 1 == num:
                    return [i,j]

    def initcitys(self):
        self.citys = []
        num_pos = []
        label = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']

        for num in self.number:
            num_pos.append(self.get_pos(num))
        for pos, la in zip(num_pos, label):
            self.citys.append((float(pos[0]), float(pos[1]), la))

    def distance(self, order):
        distance = 0.0
        index1 = index2 = index3 = 0

        for i in range(0, int(len(self.citys)/2)-1):
            index1, index2 = order[i], order[i + 1]
            index3= order[i + int(len(self.citys) / 2)]

            city1, city2 = self.citys[index1], self.citys[index2]
            city3 = self.citys[index3]

            distance += abs(city1[0] - city3[0])  + abs(city1[1] - city3[1])
            distance += abs(city2[0] - city3[0])  + abs(city2[1] - city3[1])

        index1, index2 = order[int(len(self.citys)/2)-1], order[len(self.citys)-1]
        city1, city2 = self.citys[index1], self.citys[index2]
        distance += abs(city1[0] - city3[0])  + abs(city1[1] - city3[1])

        return distance

    def matchFun(self):
        return lambda life: 1.0 / self.distance(life.gene)

    def run(self,iter=0):
        temp_out = []
        out = []
        self.total = iter
        last_distance = 0.0
        count = 0

        while iter > 0:
            self.ga.next()
            distance = self.distance(self.ga.best.gene)

            if distance != last_distance:
                last_distance = distance
                count = 0
            else:
                count += 1
            if count > 300:
                break

            iter -= 1
            if iter % 50 == 0:
                print(' |--- 完成了 {:.2f}%'.format(float((self.total-iter)/self.total)*100))

        out.extend(self.ga.best.gene)
        return out

    def print(self):
        number = []
        for ge in self.ga.best.gene:
            number.append(self.number[ge])

        return number




def main():
    tsp = TSP([1,2,3,4,9,10,11,12, 8, 7,6,5,4,3,2,1])
    path = tsp.run(iter=5000)
    haha = tsp.print()
    print('最短的路径为: {}'.format(path))
    print(haha)



def handle():
    chess = [1 , 2, 3, 4, 5, 6 ,7 ,8]
    queen_list = get_queen(8)
    queen_list_len = len(queen_list)

    best_distance = 9999
    best_path = []

    for i, inner_queen in enumerate(queen_list):
        temp = []
        temp.extend(chess)
        temp.extend(inner_queen)

        tsp = TSP(temp)
        tsp.run(iter=3000)
        path = tsp.print()
        dis = tsp.distance(tsp.ga.best.gene)
        if dis < best_distance:
            best_distance = dis
            best_path = path
        if i % 5 == 0:
            print('完成了 {}%'.format(float((i)/queen_list_len)*100))


    print('\n最短的路径信息为: {}'.format(best_path))
    print('最短的路径长度为: {}'.format(best_distance))
    queen_print(best_path[1:])


def get_path():
    #====================================================
    chess = [27,28,29,35,36,37,44,45]
    #================================================
    queen_list = get_queen(8)
    queen_list_len = len(queen_list)

    best_distance = 9999
    best_path = []

    final_path = []
    for i, inner_queen in enumerate(queen_list):
        temp = []
        temp.extend(chess)
        temp.extend(inner_queen)

        tsp = TSP(temp)
        tsp.run(iter=5000)
        path = tsp.print()
        dis = tsp.distance(tsp.ga.best.gene)
        if dis < best_distance:
            best_distance = dis
            best_path = path

        print('完成了 {}%'.format(float((i) / queen_list_len) * 100))
        if i % 5 == 0:
            break

    # 最佳路径格式设置
    length = len(best_path)
    inner_1 = []
    inner_2 = []
    for index, inner in enumerate(best_path):
        if index < int(length/2):
            inner_1.append(inner)
        else:
            inner_2.append(inner)
    for temp, temp2 in zip(inner_1, inner_2):
        final_path.append(temp)
        final_path.append(temp2)

    optim_path = []
    out_chess = []
    out_index = []
    index = []
    i = 0
    while True:
        if final_path[i] == final_path[i+1]:
            out_index.append(i)
            index.append(i)
            index.append(i+1)
        i += 1

        if i == length - 2:
            break


    for i, temp in enumerate(final_path):
        if i not in index:
            optim_path.append(temp)
        if i in out_index:
            out_chess.append(temp)

    start = optim_path[0]
    final = optim_path[-1]

    start_from = get_barr(start)
    final_to = get_barr(final)

    final = []
    final.append(start_from)
    final.extend(optim_path)
    final.append(final_to)

    return final, out_chess


def get_path_input(chess_input):
    #====================================================
    chess = chess_input
    #================================================
    queen_list = get_queen(8)
    queen_list_len = len(queen_list)

    best_distance = 9999
    best_path = []

    final_path = []
    for i, inner_queen in enumerate(queen_list):
        temp = []
        temp.extend(chess)
        temp.extend(inner_queen)

        tsp = TSP(temp)
        tsp.run(iter=5000)
        path = tsp.print()
        dis = tsp.distance(tsp.ga.best.gene)
        if dis < best_distance:
            best_distance = dis
            best_path = path

        print('完成了 {}%'.format(float((i) / queen_list_len) * 100))
        if i % 5 == 0:
            break

    # 最佳路径格式设置
    length = len(best_path)
    inner_1 = []
    inner_2 = []
    for index, inner in enumerate(best_path):
        if index < int(length/2):
            inner_1.append(inner)
        else:
            inner_2.append(inner)
    for temp, temp2 in zip(inner_1, inner_2):
        final_path.append(temp)
        final_path.append(temp2)

    optim_path = []
    out_chess = []
    out_index = []
    index = []
    i = 0
    while True:
        if final_path[i] == final_path[i+1]:
            out_index.append(i)
            index.append(i)
            index.append(i+1)
        i += 1

        if i == length - 2:
            break


    for i, temp in enumerate(final_path):
        if i not in index:
            optim_path.append(temp)
        if i in out_index:
            out_chess.append(temp)

    start = optim_path[0]
    final = optim_path[-1]

    start_from = get_barr(start)
    final_to = get_barr(final)

    final = []
    final.append(start_from)
    final.extend(optim_path)
    final.append(final_to)

    return final, out_chess

if __name__ == '__main__':
    #main()
    #handle()
    path, chess = get_path()
    print('path')
    print(path)
    print('chess')
    print(chess)
