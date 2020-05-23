# !/usr/bin/python2
# -*- coding: UTF-8 -*-
import sys
import socket
import time
import os
import shutil
from datetime import datetime, timedelta

s_server = socket.socket()
print("Starting to create socket server")
host = ''
port = 8105
addr = (host, port)
s_server.bind(addr)  # 绑定端口

s_server.listen(5)#开始监听TCP传入连接，backlog指定在拒绝链接前，操作系统可以挂起的最大连接数，该值最少为1，大部分应用程序设为5就够用了

to_client, addr = s_server.accept()
#注意：accept()函数会返回一个元组
#元素1为客户端的socket对象，元素2为客户端的地址(ip地址，端口号)
print ('...connected from :', addr)

rev_str = to_client.recv(1024)

while True:
    path = "./server/"
    dir = os.listdir(path)
    to_client.send(str(len(dir)))
    to_client.recv(8)

    # server move ; client move
    for file in dir:
        file_size = os.path.getsize(path+ '/' + file)
        print('The length of the file is : %d ' % file_size)
        file_info = '%s|%s' % (file, file_size)
        # print(type(file_info))
        to_client.send(file_info)
        to_client.recv(6)
        fout = open(path + '/' + file, "rb")
        has_send = 0
        # to_client.send(d)
        while has_send < file_size:
            frame_data = fout.read(1)
            to_client.send(frame_data)
            has_send += len(frame_data)
        fout.close()
        time.sleep(2)
        try:
            shutil.move(path+ '/' + file, './server-move/'+ '/')
        except:
            print('already exists')
            os.remove(path + '/' + file)

    print("program exit normally:-> close socket")