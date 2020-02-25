import random
import numpy as np
import time
from copy import deepcopy as dp

def conflict(state, col):
    # 冲突函数，row为行，col为列
    row = len(state)
    for i in range(row):
        if abs(state[i] - col) in (0, row - i):  # 重要语句
            return True
    return False


def queens(num=8, state=()):
    # 生成器函数
    for pos in range(num):
        if not conflict(state, pos):
            if len(state) == num - 1:
                yield (pos,)
            else:
                for result in queens(num, state + (pos,)):
                    yield (pos,) + result


def queenprint(solution):
    # 打印函数
    def line(pos, length=len(solution)):
        return '. ' * (pos) + 'X ' + '. ' * (length - pos - 1)

    for pos in solution:
        print(line(pos))

def queenprint2(solution):
    for i in range(8):
        str = ''
        for j in range(8):
            if [i,j] in solution:
                str += 'X '
            else:
                str += '. '
        print(str)

def getMatrix(queen_list):
    """将八皇后问题求解的列表转化成对相应的数组形式
    """
    size = len(queen_list)
    matrix = np.zeros((size, size), dtype=np.int)

    for i in range(size):
        matrix[queen_list[i][0]][queen_list[i][1]] = 1

    return matrix

def getList(queen_format):

    """将八皇后问题求解的形式转化成对相应的列表
    """
    size = len(queen_format)
    result = np.zeros(size, dtype=np.int)

    for pos in queen_format:
        result[pos[0]] = pos[1]

    return result


def getMinDistance(queen_matrix, origin_matrix):
    """
    """
    queen_matrix = np.array(queen_matrix)
    origin_matrix = np.array(origin_matrix)

    assert queen_matrix.shape == origin_matrix.shape and \
           queen_matrix.shape[0] == queen_matrix.shape[1] and \
           origin_matrix.shape[0] == origin_matrix.shape[1]
    size = queen_matrix.shape[0]

    """获得两点间距离
    """
    def getDis(queen_pos, origin_pos):
        return abs(queen_pos[0] - origin_pos[0]) + abs(queen_pos[1] - origin_pos[1])

    """获得距离矩阵
    """
    def getMatrixDis(queen, origin):
        matrix = np.zeros((size,size), dtype=np.float)
        for i in range(size):
            for j in range(size):
                matrix[i][j] = getDis(queen[j], origin[i])
        return matrix

    """获得位置点信息
    """
    def getPosInfo(matrix):
        result_list = []
        index = 0
        for i in range(size):
            for j in range(size):
                if matrix[i][j] == 1:
                    temp = [i,j]
                    result_list.append(temp)
                    index += 1
        return result_list

    """判断是否冲突
    """
    def isConfilct(num, state):
        if num in state:
            return True
        return False

    """获得距离的list
    """
    def getDisList(state = ()):
        for pos in range(size):
            if not isConfilct(pos, state):
                if len(state) == size - 1:
                    yield (pos,)
                else:
                    for result in getDisList(state + (pos,)):
                        yield (pos,) + result

    """基于list获得距离
    """
    def getDisDueList(dis_list):
        distance = 0.0
        for i in range(size):
            #distance += dis_matrix[dis_list[i]][i]
            distance += dis_matrix[i][dis_list[i]]
        return distance

    #获得八皇后的位置点信息
    queen_list = getPosInfo(queen_matrix)

    #获得原图像的位置点信息
    origin_list = getPosInfo(origin_matrix)

    #获得距离矩阵
    dis_matrix = getMatrixDis(queen_list, origin_list)
    #获得距离list及对应距离
    distance = []
    dis_list = list(getDisList())
    dis_value = list(map(getDisDueList, dis_list))

    for dis, list_temp in zip(dis_value, dis_list):
        dis_dict = {}
        dis_dict['dis'] = dis
        dis_dict['list'] = list_temp
        distance.append(dis_dict)

    #排序
    distance = sorted(distance, key=lambda dis:dis['dis'])

    #返回最小的
    essential_origin = origin_list
    essential_queen = []
    for i in range(size):
        essential_queen.append(queen_list[distance[0]['list'][i]])

    return distance[0], essential_origin, essential_queen

def queenFormat(queen):
    array = []
    for i in range(len(queen)):
        array.append([i, queen[i]])
    return array


def outputFormat(distance, origin, queen):
    chess, path, in_dis = get_path_optim(origin, queen)

    print()
    print('原来点      目标点')
    for i in range(len(origin)):
        print(str(origin[i]), '-->', str(queen[i]))
    print('最小距离为 ' , str(distance))

    return chess, path

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

def get_path_optim(origin, queen):
    def get_num(a):
        return a[0] * 8 + a[1] + 1

    def get_dis(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def getLeast(a, b_list):
        best = []
        best_dis = 999

        for b in b_list:
            dis = get_dis(a,b)
            if dis < best_dis:
                best = b
                best_dis = dis

        return best, best_dis

    def make_dict(q_list):
        d = {}
        for i,q in enumerate(q_list):
            d[str(q)] = i

        return d

    ori = dp(origin)
    que = dp(queen)
    que_dict = make_dict(origin)

    best_dis = 0
    index_list = []
    index = 0
    index_list.append(index)
    ori.remove(ori[index])

    # 获得次序
    while len(index_list) != 8:
        temp, dis = getLeast(queen[index], ori)
        best_dis += dis
        index = que_dict[str(temp)]
        index_list.append(index)
        if ori != []:
            ori.remove(origin[index])

    # 获得数组集
    pair = []
    for i in index_list:
        pair.append(get_num(origin[i]))
        pair.append(get_num(queen[i]))

    # 优化数组集
    length = len(pair)
    i = 0
    optim_path = []
    chess = []
    index = []

    while True:
        if pair[i] == pair[i+1]:
            index.append(i)
            index.append(i+1)
            chess.append(pair[i])
        i += 1
        if i == length - 2:
            break

    for i, temp in enumerate(pair):
        if i not in index:
            optim_path.append(temp)

    start = optim_path[0]
    final = optim_path[-1]

    start_from = get_barr(start)
    final_to = get_barr(final)

    final = []
    final.append(start_from)
    final.extend(optim_path)
    final.append(final_to)

    return chess, final, best_dis




def inputFormat(queen_list):
    def getPos(num):
        for i in range(8):
            for j in range(8):
                if i*8+j+1 == num:
                    return [i,j]

    out = []
    for temp in queen_list:
        out.append(getPos(temp))

    return out

#=============================================
#      实现部分
#=============================================
def essentialFunc(ori_list):
    min_distance = 10000.0
    ori_essential = []
    que_essential = []

    queen_list_essential = list(queens(8))
    list_size = len(queen_list_essential)
    index = 0

    for solution in list(queen_list_essential):
        index += 1
        dis, ori, que = getMinDistance(getMatrix(queenFormat(solution)), getMatrix(ori_list))
        chess, path, in_dis = get_path_optim(ori, que)
        if min_distance > dis['dis'] + in_dis:
            min_distance = dis['dis'] + in_dis
            ori_essential = ori
            que_essential = que


        print( "the process is %.2f percent" %float(index * 100 / list_size))

    chess, path = outputFormat(min_distance, ori_essential, que_essential)
    print("转花前的效果")
    queenprint2(ori_essential)
    print("转化后的效果")
    queenprint2(que_essential)


    print('chess:')
    print(chess)
    print('path:')
    print(path)

    return path, chess







if __name__ == '__main__':
    start = time.time()
    essentialFunc(inputFormat([1,7,11, 23, 34, 32,35,56]))
    print('time consuming: ' + str(time.time() - start))









