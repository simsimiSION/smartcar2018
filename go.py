#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/7/18 12:40
# @File    : go.py
# @Software: PyCharm

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
NUMBER_L = 210
BARRIER_U_D_H = 150
BARRIER_U_D_L = 230
BARRIER_L_R_H = 190
BARRIER_L_R_L = 200



def operate(direct, location, path, initial, limit=30, limit_up=40, limit_low=25, limit_small=10, bias=0):
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

def get_operate_speed(location, limit=[150,150]):
        x = limit[0] - location[0]
        y = limit[1] - location[1]
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

def number_detect(number, location, direct, img_show, img_origin, status, button_status, dis, angel, path, optim, bd, map, barrier_dir):

    if status == WAIT:
        if button_status == DOWN:
            optim.num_path = []
            optim.path = []
            _path, num_path = optim.get_path(map,
                                            optim.get_pos(optim.initial),
                                            optim.get_pos(dis))
            path.extend(num_path)
            status = RUNNING
            button_status = UP

    if status == PRE_BACKING:
        optim.num_path = []
        optim.path = []
        _path, num_path = optim.get_path(map,
                                        optim.get_pos(optim.initial),
                                        optim.get_pos(57))

        path.extend(num_path)
        status = BACKING

    if status == RUNNING or status == BACKING:
        target = path[0]
        # 数字确认
        number = optim.get_possibility(number)
        # 小车移动的方向
        if len(path) == 1 and status == RUNNING:
            direct = optim.get_direct(path, target, location, angel, limit=[150, 200])
        else:
            direct = optim.get_direct(path, target, location, angel)

        if number == optim.num_map[target[0], target[1]]:
            if len(path) > 1 and operate(direct, location):
                path = path[1:]
                optim.pop_numpath()
                optim.initial = optim.num_map[target[0], target[1]]
            elif len(path) == 1 and ((abs(location[0] - 150) < 5 and abs(location[1] - 200) < 10 and status == RUNNING)\
                                or (abs(location[0] - 150) < 5 and abs(location[1] - 150) < 10 and status == BACKING)):

                # 新加入的内容==========================================
                if barrier_dir == 'none':
                    path = []

                    if status == RUNNING:
                        status = PRE_BACKING
                    elif status == BACKING:
                        status = WAIT
                else:
                    direct, centre, bbox = bd.direct(img_show, barrier_dir, angel)
                    # 绘制边界
                    if bbox != None:
                        cv2.drawContours(img_origin, [bbox], 0, (0, 0, 255), 3)
                    if abs(centre[0] - 150) < 30 and abs(centre[1] - 150) < 30:
                        path = []
                        barrier_dir == 'none'

                        if status == RUNNING:
                            status = PRE_BACKING

    return status, button_status, path, optim, barrier_dir, direct

def circle_detect(number, location, direct, img_show, img_origin, status, button_status, dis, angel, path, optim, bd, map, barrier_dir):

    if status == WAIT:
        if button_status == DOWN:
            optim.path = []
            optim.num_path = []
            _path, num_path = optim.get_path(map,
                                            optim.get_pos(optim.initial),
                                            optim.get_pos(dis))
            path.extend(num_path)
            status = RUNNING
            button_status = UP

    if status == PRE_BACKING:
        optim.num_path = []
        optim.path = []
        _path, num_path = optim.get_path(map,
                                        optim.get_pos(optim.initial),
                                        optim.get_pos(57))

        path.extend(num_path)
        status = BACKING

    if status == BACKING:
        target = path[0]
        # 数字确认
        number = optim.get_possibility(number)
        # 小车移动的方向
        if len(path) == 1 and status == RUNNING:
            direct = optim.get_direct(path, target, location, angel, limit=[150, 180])
        else:
            direct = optim.get_direct(path, target, location, angel)

        if number == optim.num_map[target[0], target[1]] and operate(direct, location):

            if len(path) > 1:
                path = path[1:]
                optim.pop_numpath()
                optim.initial = optim.num_map[target[0], target[1]]
            elif len(path) == 1 and abs(location[0] - 150) < 5 and abs(location[1] - 150) < 10:

                # 新加入的内容==========================================
                if barrier_dir == 'none':
                    path = []

                    if status == RUNNING:
                        status = PRE_BACKING
                    elif status == BACKING:
                        status = WAIT
                else:
                    direct, centre, bbox = bd.direct(img_show, barrier_dir, angel)
                    # 绘制边界
                    if bbox != None:
                        cv2.drawContours(img_origin, [bbox], 0, (0, 0, 255), 3)
                    if abs(centre[0] - 150) < 10 and abs(centre[1] - 150) < 10:
                        path = []
                        barrier_dir == 'none'

                        if status == RUNNING:
                            status = PRE_BACKING

    if status == RUNNING:
        target = path[0]
        # 数字确认
        if len(path) > 1:
            number = optim.get_possibility(number)

        # 小车移动的方向
        if len(path) > 1:
            direct = optim.get_direct(path, target, location, angel)
        else:
            direct = optim.get_direct(path, target, [150, 150], 0.0)


        # 数字标定
        if len(path) > 2:
            if number == optim.num_map[target[0], target[1]] and operate(direct, location):
                path = path[1:]
                optim.pop_numpath()
                optim.initial = optim.num_map[target[0], target[1]]
        # 数字标定
        elif len(path) == 2:
            if number == optim.num_map[target[0], target[1]] and operate(direct, location):
                path = path[1:]
                optim.pop_numpath()
                optim.initial = optim.num_map[target[0], target[1]]

        elif len(path) == 1:
            _, circle_list, is_circle = detect_circle_2(img_show)

            #给定速度
            if is_circle:
                direct[2] = angel
                if abs(circle_list[0] - 150) != 0.0:
                    direct[1] = 0.5*(circle_list[0] - 150)/abs(circle_list[0] - 150)
                if abs(circle_list[1] - 180) != 0.0:
                    direct[0] = -0.5*(circle_list[1] - 180)/abs(circle_list[1] - 180)
            else:
                direct[2] = 0.0
                if direct[0] != 0.0:
                    direct[0] = 2.0 * direct[0] / abs(direct[0])
                if direct[1] != 0.0:
                    direct[1] = 2.0 * direct[1] / abs(direct[1])


            if is_circle == 1 and abs(circle_list[0] - 150) < 5 \
                                and abs(circle_list[1] - 180) < 5:

                path = []
                optim.initial = dis
                if status == RUNNING:
                    status = PRE_BACKING

    return status, button_status, path, optim, barrier_dir, direct

def chess_move(number, location, direct, img_show, img_origin, status, button_status, dis, dis2, arm_mode, angel, path, optim, map):
    if status == WAIT:
        if button_status == DOWN:
            optim.path = []
            optim.num_path = []
            _path, num_path = optim.get_path(map,
                                            optim.get_pos(optim.initial),
                                            optim.get_pos(dis))
            path.extend(num_path)
            arm_mode = 2
            button_status = UP
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
            direct = optim.get_direct(path, target, [150, 150], 0.0)

        # 数字标定
        if len(path) >= 2:
            if number == optim.num_map[target[0], target[1]] and operate(direct, location):
                path = path[1:]
                optim.pop_numpath()
                optim.initial = optim.num_map[target[0], target[1]]

        elif len(path) == 1:
            _, circle_list, is_circle = detect_circle_2(img_show)

            #给定速度
            if is_circle:
                direct[2] = 0.0
                if abs(circle_list[0] - 150) != 0.0:
                    direct[1] = round(0.8*(circle_list[0] - 150)/abs(circle_list[0] - 150),1)
                if abs(circle_list[1] - 190) != 0.0:
                    direct[0] = round(-0.8*(circle_list[1] - 190)/abs(circle_list[1] - 190), 1)
            else:
                direct[2] = 0.0
                if direct[0] != 0.0:
                    direct[0] = 2.0 * direct[0] / abs(direct[0])
                if direct[1] != 0.0:
                    direct[1] = 2.0 * direct[1] / abs(direct[1])


            if is_circle == 1 and abs(circle_list[0] - 150) < 10 \
                                and abs(circle_list[1] - 190) < 10:

                path = []
                optim.initial = dis
                if status == RUNNING:
                    status = PRE_RUNNING

    elif status == PRE_RUNNING:
        optim.num_path = []
        optim.path = []
        _path, num_path = optim.get_path(map,
                                        optim.get_pos(optim.initial),
                                        optim.get_pos(dis2))

        path.extend(num_path)
        arm_mode = 1
        status = RUNNING_GO

    elif status == RUNNING_GO:
        target = path[0]
        # 数字确认
        number = optim.get_possibility(number)
        # 小车移动的方向
        if len(path) == 1:
            direct = optim.get_direct(path, target, location, angel, limit=[150, 200])
            if direct[0] != 0.0:
                direct[0] = round(1.5 * direct[0] / abs(direct[0]), 1)
            if direct[1] != 0.0:
                direct[1] = round(1.5 * direct[1] / abs(direct[1]), 1)

        else:
            direct = optim.get_direct(path, target, location, angel)

        if number == optim.num_map[target[0], target[1]]:
            if len(path) > 1 and operate(direct, location):
                path = path[1:]
                optim.pop_numpath()
                optim.initial = optim.num_map[target[0], target[1]]
            elif len(path) == 1 and (abs(location[0] - 150) < 5 and abs(location[1] - 200) < 10):
                path = []
                status = PRE_BACKING

    elif status == PRE_BACKING:
        optim.num_path = []
        optim.path = []
        _path, num_path = optim.get_path(map,
                                         optim.get_pos(optim.initial),
                                         optim.get_pos(57))

        path.extend(num_path)
        status = BACKING
    
    elif status == BACKING:
        target = path[0]
        # 数字确认
        number = optim.get_possibility(number)
        # 小车移动的方向
        direct = optim.get_direct(path, target, location, angel)

        if number == optim.num_map[target[0], target[1]] and operate(direct, location):
            if len(path) > 1:
                path = path[1:]
                optim.pop_numpath()
                optim.initial = optim.num_map[target[0], target[1]]
            elif len(path) == 1 and abs(location[0] - 150) < 5 and abs(location[1] - 150) < 10:
                path = []
                status = WAIT

    return status, button_status, path, optim, arm_mode, direct

def queue_move(number, location, direct, img_show, img_origin, status, button_status, dis, mode, arm_mode, angel, path, optim, map, last_position):
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
                if number == optim.num_map[target[0], target[1]]:
                    #direct[2] = 0.0
                    #direct[0], direct[1] = get_operate_speed(location)
                    # print('LR:'+str(direct[1])+ '  FB:' +str(direct[0]))
                    # print('locatoion: '+ str(location))

                    if operate(direct, location, path, last_position):
                        #=============================================
                        print(str(number) + ': ' + str(location))
                        #=============================================
                        last_position = path[0]
                        path = path[1:]
                        optim.pop_numpath()
                        optim.initial = optim.num_map[target[0], target[1]]

            elif len(path) == 1 and status == RUNNING:
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
                    if status == RUNNING:
                        status = ARMING

        elif len(path) == 1 and status == ARMING:
            target = path[0]
            direct = get_operate_speed(location)
            if number == optim.num_map[target[0], target[1]]:
                if operate2(direct, location, path):
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
            _, circle_list, is_circle = detect_circle_2(img_show)
            if is_circle:
                direct = get_operate_speed(circle_list)
                if operate2(direct, circle_list, path):
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

            if number == optim.num_map[target[0], target[1]]:
                if len(path) > 1:
                    if operate(direct, location, path, last_position):
                        last_position = path[0]
                        path = path[1:]
                        optim.pop_numpath()
                        optim.initial = optim.num_map[target[0], target[1]]
                # elif len(path) == 1 and abs(location[0] - 150) < 30 and abs(location[1] - 150) < 30:
                #     path = []
                #     status = RUNNING_GO
                elif len(path) == 1:
                    _, circle_list, is_circle = detect_circle_2(img_show)
                    if is_circle:
                        if abs(circle_list[0] - 150) < 30 and abs(circle_list[1] - 150) < 30:
                            path = []
                            status = RUNNING_GO
                    else:
                        if abs(location[0] - 150) < 30 and abs(location[1] - 150) < 30:
                            path = []
                            status = RUNNING_GO
    return status, button_status, path, optim, arm_mode, direct, last_position

def move_in(number, location, direct, img_show, img_origin, status, button_status, dis, mode, arm_mode, angel, path, optim, map, last_position):
    finish = False

    if button_status == DOWN:
        if dis == 1 or dis == 9 or dis == 17 or dis == 25 or dis == 33 or dis == 41 or dis == 49:
            direct = [0.0, 4.0, 0.0]
        elif dis == 57 or dis == 58 or dis == 59 or dis == 60 or dis == 61 or dis == 62 or dis == 63 or dis == 64:
            direct = [4.0, 0.0, 0.0]
        elif dis == 8 or dis == 16 or dis == 24 or dis == 32 or dis == 40 or dis == 48 or dis == 56:
            direct = [0.0, -4.0, 0.0]
        elif dis == 2 or dis == 3 or dis == 4 or dis == 5 or dis == 6 or dis == 7:
            direct = [-4.0, 0.0, 0.0]

        _, circle_list, is_circle = detect_circle_2(img_show)

        if is_circle == 1 or number == dis:
            optim.initial = dis
            finish = True

    return finish, button_status, path, optim, arm_mode, direct, last_position

def move_out(number, location, direct, img_show, img_origin, status, button_status, dis, mode, arm_mode, angel, path, optim, map, last_position):
    time_out = 35
    if button_status == DOWN:
        if dis == 1 or dis == 9 or dis == 17 or dis == 25 or dis == 33 or dis == 41 or dis == 49:
            direct = [0.0, -5.0, 0.0]
            time_out = 24
        elif dis == 57 or dis == 58 or dis == 59 or dis == 60 or dis == 61 or dis == 62 or dis == 63 or dis == 64:
            direct = [-9.0, 0.0, 0.0]
            time_out = 5
        elif dis == 8 or dis == 16 or dis == 24 or dis == 32 or dis == 40 or dis == 48 or dis == 56:
            direct = [0.0, 5.0, 0.0]
            time_out = 24
        elif dis == 2 or dis == 3 or dis == 4 or dis == 5 or dis == 6 or dis == 7:
            direct = [9.0, 0.0, 0.0]
            time_out = 35

    return time_out, status, button_status, path, optim, arm_mode, direct, last_position

def barrier(barrier_out, queen_count, chess_list, number, location, direct, img_show, img_origin, status, button_status, dis, mode, arm_mode, angel, path, optim, map, bd, barrier_dir, barrier_flag, last_position, dis_list):
    is_circle = 0
    circle_list = [150, 150]

    if status == WAIT:
        if button_status == DOWN:
            optim.num_path = []
            optim.path = []
            _path, num_path = optim.get_path(map,
                                            optim.get_pos(optim.initial),
                                            optim.get_pos(dis))
            path.extend(num_path)
            status = RUNNING


            arm_mode = 3

    elif status == RUNNING:
        target = path[0]
        # 数字确认
        number = optim.get_possibility(number)
        # 小车移动的方向
        direct = optim.get_direct(path, target, location, angel)


        if optim.num_map[target[0], target[1]] in chess_list:
            if queen_count == 0:
                _, circle_list, is_circle = detect_circle_2(img_show)

                if is_circle:
                    if len(path) > 1:
                        direct[0], direct[1], _ = get_operate_speed(circle_list)
                        if operate(direct, circle_list, path, last_position):
                            queen_count = 1
                            last_position = path[0]
                            path = path[1:]
                            optim.pop_numpath()
                            optim.initial = optim.num_map[target[0], target[1]]
                    elif len(path) == 1:
                        if barrier_dir == 'up':
                            direct = get_operate_speed( circle_list, limit=[150, 260])
                        if barrier_dir == 'down':
                            direct = get_operate_speed( circle_list, limit=[150, 40])
                        if barrier_dir == 'left':
                            direct = get_operate_speed( circle_list, limit=[260, 150])
                        if barrier_dir == 'right':
                            direct = get_operate_speed( circle_list, limit=[40, 150])

                        if (barrier_dir == 'left' and circle_list[0] > 180) or (barrier_dir == 'right' and circle_list[0] < 120) or \
                            (barrier_dir == 'up' and circle_list[1] > 180) or (barrier_dir == 'down' and circle_list[1] < 120):
                            queen_count = 1
                            barrier_flag = 1
        else:
            if number == optim.num_map[target[0], target[1]]:
                if len(path) > 1:
                    direct[0], direct[1], _ = get_operate_speed(location)
                    if operate(direct, location, path, last_position):
                        last_position = path[0]
                        path = path[1:]
                        optim.pop_numpath()
                        optim.initial = optim.num_map[target[0], target[1]]
                elif len(path) == 1:
                    if barrier_dir == 'up':
                        direct = optim.get_direct(path, target, location, angel, limit=[150, 260])
                    if barrier_dir == 'down':
                        direct = optim.get_direct(path, target, location, angel, limit=[150, 40])
                    if barrier_dir == 'left':
                        direct = optim.get_direct(path, target, location, angel, limit=[260, 150])
                    if barrier_dir == 'right':
                        direct = optim.get_direct(path, target, location, angel, limit=[40, 150])

                    if (barrier_dir == 'left' and location[0] > 180) or (barrier_dir == 'right' and location[0] < 120) or \
                        (barrier_dir == 'up' and location[1] > 180) or (barrier_dir == 'down' and location[1] < 120):
                        barrier_flag = 1

        if barrier_flag == 1:
            direct, centre, bbox = bd.direct(img_show, barrier_dir, angel)
            # 绘制边界
            if isinstance(bbox, np.ndarray):
                cv2.drawContours(img_origin, [bbox], 0, (0, 0, 255), 3)
            if (abs(centre[0] - BARRIER_U_D_H) < 20 and abs(centre[1] - BARRIER_U_D_L) < 5 and (barrier_dir == 'up' or barrier_dir == 'down')) or \
                (abs(centre[0] - BARRIER_L_R_H) < 5 and abs(centre[1] - BARRIER_L_R_L) < 30 and (barrier_dir == 'left' or barrier_dir == 'right')) :
                barrier_flag = 0
                status = ARMING
    elif status == ARMING:
        target = path[0]
        # 数字确认
        #number = optim.get_possibility(number)
        if optim.num_map[target[0], target[1]] in chess_list:
            if queen_count == 0:
                _, circle_list, is_circle = detect_circle_2(img_show)
                if is_circle:
                    barrier_out = 1
                    direct = get_operate_speed(circle_list)
                    if operate2(direct, circle_list, path):
                        optim.initial = optim.num_map[target[0], target[1]]
                        queen_count = 1
                        path = []
                        status = BACKING
                        barrier_dir == 'none'
                        barrier_out = 0

                elif barrier_out == 0:
                    if barrier_dir == 'up':
                        direct = [-2.0, 0.0, 0.0]
                    elif barrier_dir == 'down':
                        direct = [2.0, 0.0, 0.0]
                    elif barrier_dir == 'left':
                        direct = [-0.8, 2.0, 0.0]
                    elif barrier_dir == 'right':
                        direct = [-0.8, -2.0, 0.0]

        else:
            if number == optim.num_map[target[0], target[1]]:
                direct = optim.get_direct(path, target, location, angel)
                if operate2(direct, location, path):
                    path = []
                    status = BACKING
                    barrier_dir == 'none'
            else:
                if barrier_dir == 'up':
                    direct = [-2.0, 0.0, 0.0]
                elif barrier_dir == 'down':
                    direct = [2.0, 0.0, 0.0]
                elif barrier_dir == 'left':
                    direct = [-0.8, 2.0, 0.0]
                elif barrier_dir == 'right':
                    direct = [-0.8, -2.0, 0.0]

    return barrier_out, queen_count, chess_list, status, button_status, path, optim, arm_mode, direct, bd, barrier_dir, barrier_flag, last_position
