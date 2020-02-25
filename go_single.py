
from handle2 import *
from handle import *
from copy import deepcopy as dc

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


CIRCLE_H = 150
CIRCLE_L = 215
NUMBER_H = 135
NUMBER_L = 225
BARRIER_U_D_H = 150
BARRIER_U_D_L = 230
BARRIER_L_R_H = 150
BARRIER_L_R_L = 180



def operate(direct, location, path, initial, limit=15, limit_up=30, limit_low=15, limit_small=10, bias=10):
    # direct 0 qianhou
    if len(path) >= 2:
        direct_pre = path[1]
        direct_now = path[0]
        direct_pass = initial

        # 直线行驶
        if (direct_pre[0] - direct_now[0]) == (direct_now[0] - direct_pass[0]) or (direct_pre[1] - direct_now[1]) == (direct_now[1] - direct_pass[1]):
            if direct_now[0] == direct_pre[0]:
                if abs(location[0] - 150) < limit_up and abs(location[1] - 150) < limit:
                    return 1
            elif direct_now[1] == direct_pre[1]:
                if abs(location[0] - 150) < limit and abs(location[1] - 150) < limit_up:
                    return 1
            else:
                if abs(location[0] - 150) < limit and abs(location[1] - 150) < limit:
                    return 1
        # 转弯
        else:
            if abs(direct_now[0] - direct_pass[0]) == 1.0:
                index = direct_now[0] - direct_pass[0]
                if abs(location[0] - 150) < limit_low and abs(location[1] - 150 - index*bias) < limit_small:
                    return 1
            elif abs(direct_now[1] - direct_pass[1]) == 1.0:
                index = direct_now[1] - direct_pass[1]
                if abs(location[0] - 150 - index*bias) < limit_small and abs(location[1] - 150) < limit_low:
                    return 1
            else:
                if abs(location[0] - 150) < limit_low and abs(location[1] - 150) < limit_low:
                    return 1

    else:
         if abs(location[0] - 150) < limit_low and abs(location[1] - 150) < limit_low:
            return 1

    return 0

def operate2(direct, location, path, limit=35, limit_up=40, limit_low=25):

    if len(path) >= 2:
        direct_pre = path[1]
        direct_now = path[0]

        if direct_now[0] == direct_pre[0]:
            if abs(location[0] - 150) < limit_up and abs(location[1] - 150) < limit:
                return 1
        elif direct_now[1] == direct_pre[1]:
            if abs(location[0] - 150) < limit and abs(location[1] - 150) < limit_up:
                return 1
        else:
            if abs(location[0] - 150) < limit and abs(location[1] - 150) < limit:
                return 1

    else:
         if abs(location[0] - 150) < limit_low and abs(location[1] - 150) < limit_low:
            return 1

    return 0

def get_operate_speed(location):
        x = 150 - location[0]
        y = 150 - location[1]
        base = float((x**2+y**2)**0.5)
        if base != 0.0:
            x = float(x) / base
            y = float(y) / base
            if x < 0.7 and x > 0:
                x = 0.7
            if x > -0.7 and x < 0:
                x = -0.7
            if y < 0.7 and y > 0:
                y = 0.7
            if y > -0.7 and y < 0:
                y = -0.7
            y = round(y,1)
            x = round(-x,1)
            return [y,x, 0.0]
        else:
            return [0.0, 0.0, 0.0]


def queue_move_single(queen_out, queen_count, chess_list, number, location, direct, img_show, img_origin, status, button_status, dis, mode, arm_mode, angel, path, optim, map, last_position):
    is_circle = 0
    if mode == 2:
        if status == WAIT:
            if button_status == DOWN:
                optim.path = []
                optim.num_path = []
                _path, num_path = optim.get_path(map,
                                                optim.get_pos(optim.initial),
                                                optim.get_pos(dis))
                path.extend(num_path)
                arm_mode = 2
                status = RUNNING

        elif status == RUNNING:
            target = path[0]
            # 数字确认
            if len(path) > 1:
                number = optim.get_possibility(number)
            # 小车移动的方向
            if len(path) > 1:
                direct = optim.get_direct(path, target, location, angel)
            else:
                direct = optim.get_direct(path, target, [150, 180], 0.0)


            # 数字标定
            if len(path) >= 2:
                # 棋子的位置
                if optim.num_map[target[0], target[1]] in chess_list:
                    if queen_count == 0:
                        _, circle_list, is_circle = detect_circle_2(img_show)
                    if is_circle:
                        direct = get_operate_speed(circle_list)
                        if operate(direct, circle_list, path, last_position):
                            queen_count = 1
                            last_position = path[0]
                            path = path[1:]
                            optim.pop_numpath()
                            optim.initial = optim.num_map[target[0], target[1]]
                # 数字的位置
                else:
                    if number == optim.num_map[target[0], target[1]]:
                        if operate(direct, location, path, last_position):
                            last_position = path[0]
                            path = path[1:]
                            optim.pop_numpath()
                            optim.initial = optim.num_map[target[0], target[1]]

            elif len(path) == 1 and status == RUNNING:
                if queen_count == 0:
                    _, circle_list, is_circle = detect_circle_2(img_show)

                #给定速度
                if is_circle:
                    direct[2] = 0.0
                    if abs(circle_list[0] - CIRCLE_H) != 0.0:
                        direct[1] = round(0.8*(circle_list[0] - CIRCLE_H)/abs(circle_list[0] - CIRCLE_H),1)
                    if abs(circle_list[1] - CIRCLE_L) != 0.0:
                        direct[0] = round(-0.8*(circle_list[1] - CIRCLE_L)/abs(circle_list[1] - CIRCLE_L), 1)
                else:
                    direct[2] = 0.0
                    if direct[0] != 0.0:
                        direct[0] = round(2.5 * direct[0] / abs(direct[0]), 1)
                    if direct[1] != 0.0:
                        direct[1] = round(2.5 * direct[1] / abs(direct[1]), 1)


                if is_circle == 1 and abs(circle_list[0] - CIRCLE_H) < 10 \
                                    and abs(circle_list[1] - CIRCLE_L) < 10:
                    print(circle_list)
                    queen_count = 1
                    if status == RUNNING:
                        status = ARMING

        elif len(path) == 1 and status == ARMING:
            target = path[0]
            direct = get_operate_speed(location)
            if number == optim.num_map[target[0], target[1]]:
                if operate2(direct, location, path):
                    chess_list.remove(dis)
                    path = []
                    optim.initial = dis
                    status = FINISH

    elif mode == 1:
        if status == WAIT:
            if button_status == DOWN:
                optim.path = []
                optim.num_path = []
                # make sure that the path willnot cover the chess
                temp_map = dc(map)
                if max(optim.get_pos(optim.initial)[0]-2, 1) != optim.get_pos(dis)[0] and optim.get_pos(optim.initial)[1] != optim.get_pos(dis)[1]:
                    temp_map[max(optim.get_pos(optim.initial)[0]-2, 1), optim.get_pos(optim.initial)[1]] = 1
                _path, num_path = optim.get_path(temp_map,
                                                optim.get_pos(optim.initial),
                                                optim.get_pos(dis))
                path.extend(num_path)
                arm_mode = 1
                status = RUNNING
        elif status == RUNNING:
            target = path[0]
            # 数字确认
            if len(path) >= 2 or (len(path) == 1 and status == RUNNING):
                number = optim.get_possibility(number)
            # 小车移动的方向
            if len(path) == 1:
                direct = optim.get_direct(path, target, location, angel, limit=[NUMBER_H, NUMBER_L])
                if number == optim.num_map[target[0], target[1]]:
                    if direct[0] != 0.0:
                        direct[0] = round(0.8 * direct[0] / abs(direct[0]), 1)
                    if direct[1] != 0.0:
                        direct[1] = round(0.8 * direct[1] / abs(direct[1]), 1)
                    direct[2] = 0.0
                else:
                    if direct[0] != 0.0:
                        direct[0] = round(2.5 * direct[0] / abs(direct[0]), 1)
                    if direct[1] != 0.0:
                        direct[1] = round(2.5 * direct[1] / abs(direct[1]), 1)

            else:
                direct = optim.get_direct(path, target, location, angel)

            # 棋子的位置
            if optim.num_map[target[0], target[1]] in chess_list:
                if queen_count == 0:
                    _, circle_list, is_circle = detect_circle_2(img_show)
                if is_circle:
                    direct = get_operate_speed(circle_list)
                    if operate(direct, circle_list, path, last_position):
                        queen_count = 1
                        last_position = path[0]
                        path = path[1:]
                        optim.pop_numpath()
                        optim.initial = optim.num_map[target[0], target[1]]
            # 数字的位置
            else:
                if number == optim.num_map[target[0], target[1]]:
                    if len(path) > 1:
                        if operate(direct, location, path, last_position):
                            last_position = path[0]
                            path = path[1:]
                            optim.pop_numpath()
                            optim.initial = optim.num_map[target[0], target[1]]
                    elif len(path) == 1 and (abs(location[0] - NUMBER_H) < 10 and abs(location[1] - NUMBER_L) < 10) and status == RUNNING:
                        status = ARMING

        elif len(path) == 1 and status == ARMING:
            if queen_count == 0:
                _, circle_list, is_circle = detect_circle_2(img_show)
            if is_circle:
                direct = get_operate_speed(circle_list)
                if operate2(direct, circle_list, path):
                    queen_count = 1
                    chess_list.append(dis)
                    path = []
                    optim.initial = dis
                    status = FINISH

    elif mode == 3:
        if status == WAIT:
            optim.num_path = []
            optim.path = []
            _path, num_path = optim.get_path(map,
                                         optim.get_pos(optim.initial),
                                         optim.get_pos(dis))

            path.extend(num_path)
            status = RUNNING

        elif status == RUNNING:
            target = path[0]
            # 数字确认
            number = optim.get_possibility(number)
            # 小车移动的方向
            direct = optim.get_direct(path, target, location, angel)

            if optim.num_map[target[0], target[1]] in chess_list:
                if queen_count == 0:
                    _, circle_list, is_circle = detect_circle_2(img_show)
                if len(path) > 2:
                    if is_circle:
                        if operate(direct, circle_list, path, last_position):
                            queen_count = 1
                            last_position = path[0]
                            path = path[1:]
                            optim.pop_numpath()
                            optim.initial = optim.num_map[target[0], target[1]]
                elif len(path) == 1:
                    if is_circle:
                        if abs(circle_list[0] - 150) < 30 and abs(circle_list[1] - 150) < 30:
                            path = []
                            status = RUNNING_GO
                    if queen_out:
                        path = []
                        status = RUNNING_GO

            else:
                if number == optim.num_map[target[0], target[1]]:
                    if len(path) > 1:
                        if operate(direct, location, path, last_position):
                            last_position = path[0]
                            path = path[1:]
                            optim.pop_numpath()
                            optim.initial = optim.num_map[target[0], target[1]]
                    elif len(path) == 1:
                        if queen_count == 0:
                            _, circle_list, is_circle = detect_circle_2(img_show)
                            if is_circle:
                                if abs(circle_list[0] - 150) < 30 and abs(circle_list[1] - 150) < 30:
                                    path = []
                                    status = RUNNING_GO
                            else:
                                if abs(location[0] - 150) < 30 and abs(location[1] - 150) < 30:
                                    path = []
                                    status = RUNNING_GO
    return queen_count, chess_list, status, button_status, path, optim, arm_mode, direct, last_position



def get_movepath(dis_list):
    pass

def get_chess_list(dis_list):
    chess_list = []
    if len(dis_list) % 2 == 1:
        print( ' error !!!')
    else:
        temp_list = dis_list[1:-1]
        for i, temp in enumerate(temp_list):
            if i % 2 == 0:
                chess_list.append(temp)

    return  chess_list


