#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 文件名：client.py

import socket  # 导入 socket 模块
import os

s = socket.socket()  # 创建 socket 对象
host = socket.gethostname()  # 获取本地主机名
port = 8105  # 设置端口号

s.connect(("192.168.1.153", port))

s.send("\xAA\x96\xAC\x00\x01\x00\x01\x69")
while True:#进入循环，不断接受客户端的链接请求
    file_num = s.recv(1024)
    # print(file_num)
    s.send(file_num)
    if not file_num == "":
        file_num = int(file_num)

        for file_end in range(0, file_num):
            file_info = s.recv(80)
            print(file_info)
            filename, filesize = str(file_info).split('|')
            s.send(filesize)
            print(filesize)
            filesize = int(filesize)
            f_pic = open("./client/"+"/" + filename, "ab")
            has_receive = 0
            #file_type = s.recv(80)
            while has_receive < filesize:
                picture_date = s.recv(1)
                f_pic.write(picture_date)
                has_receive += len(picture_date)
            # time.sleep(2)
            f_pic.close()
        else:
            print("无数据，等待下次监听")
print ("停止本次监听")
s.close()