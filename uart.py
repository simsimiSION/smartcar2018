#! anaconda
# -*- coding: utf-8 -*-
# @Author  : Aries
# @Time    : 2018/6/23 16:18
# @File    : uart.py
# @Software: PyCharm

# try:
#     import serial
# except:
#     print('import serial error !!!!')
# import time
#
#
# class uart():
#     def __init__(self):
#         self.ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, stopbits=1, bytesize=8, parity=serial.PARITY_NONE)
#
#     def write_direct(self, direct):
#         self.ser.write(bytes(str(0x40),'utf8'))
#         self.ser.write(bytes(str(0x23), 'utf8'))
#         self.ser.write(bytes(str(direct[0]), 'utf8'))
#         self.ser.write(bytes(str(direct[1]), 'utf8'))
#         self.ser.write(bytes(str(direct[2]), 'utf8'))
#         self.ser.write(bytes(str(0x23), 'utf8'))
#         self.ser.write(bytes(str(0x40), 'utf8'))
#
#     def send_all(self, direct, is_working):
#
#         self.ser.write(str(0x40).encode())
#         self.ser.write(str(0x23).encode())
#         self.ser.write(str(is_working).encode())
#         self.ser.write(str(direct[0]).encode())
#         self.ser.write(str(direct[1]).encode())
#         self.ser.write(str(direct[2]).encode())
#         self.ser.write(str(0x23).encode())
#         self.ser.write(str(0x40).encode())
#
#
#
#
# if __name__ == '__main__':
#     Uart = uart()
#     i = 0
#
# #    Uart.send_all([0.0, 0.0, 360.0],q0)
#     while True:
#         print(round(0.7999999,1))
#         time.sleep(0.025)
#
#         Uart.send_all([0.0, 0.0, -8.0],0)
#

