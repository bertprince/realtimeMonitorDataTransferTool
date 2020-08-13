# -*- coding: utf-8 -*-
import os
import shutil
import threading
import time
import socket
from watchdog.observers import Observer
from watchdog.events import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
class App:
    def __init__(self):
        self.monitorPath=r"C:\Users\123\Desktop\MonitorData\motor20200109"
        self.dataPath = ''


class MyHandler(FileSystemEventHandler):
    def on_deleted(self, event):
        print("文件被删除了")
    def on_modified(self, event):
        print("文件被修改了")

    def on_created(self, event):
        print("文件被创建了 %s" % event.src_path)
        app.dataPath= event.src_path
        # data = pd.read_csv(event.src_path, sep=',', header=None,
        #                    names=['Theata', 'Radius', 'Quality'])
        # dataTheata = data['Theata'].values.tolist()
        # dataRadius = data['Radius'].values.tolist()
        # x = []
        # y = []
        #
        # try:
        #     delta = 170  # 矫正值
        # except:
        #     delta = 0
        # for id in range(len(dataTheata)):
        #     if not dataRadius[id] < 0:
        #         x.append(dataRadius[id] * cmath.cos(math.radians(dataTheata[id] + delta)))
        #         y.append(dataRadius[id] * cmath.sin(math.radians(dataTheata[id] + delta)))
        # x.append(x[0])
        # y.append(y[0])
        # plt.scatter(x,y,color='red')
        # plt.plot(x,y,color='green')
        # plt.show()

#socket server module
def StartSocketServer():
    s_server = socket.socket()
    print("Starting to create socket server")
    host = '192.168.30.1'
    port = 8105
    addr = (host, port)
    s_server.bind(addr) # 绑定端口
    s_server.listen(5)  # 开始监听TCP传入连接，backlog指定在拒绝链接前，操作系统可以挂起的最大连接数，该值最少为1，大部分应用程序设为5就够用了
    server_runtimes = 0
    file_num = 0
    to_client, addr = s_server.accept()
    # 注意：accept()函数会返回一个元组
    # 元素1为客户端的socket对象，元素2为客户端的地址(ip地址，端口号)
    print ('...connected from :', addr)
    rev_str = to_client.recv(1024)
    while True:
        server_runtimes += 1
        path = app.dataPath#文件地址
        print(path)
        if path == '':
            print("无数据传输。等待下次监听。")
            time.sleep(10)
        else:
            f_num = len(path)
            if path[-4:] == ".csv":
                to_client.send(str(f_num))
                to_client.recv(8)
                file_size = os.path.getsize(path)
                # print('正在传输文件：%s' % file)
                print('正在传输文件：' + path)
                file_info = '%s|%s' % (path, file_size)
                print(type(file_info))
                to_client.send(file_info)
                to_client.recv(6)
                fout = open(path, "rb")
                has_send = 0
                # to_client.send(d)
                while has_send < file_size:
                    frame_data = fout.read(1)
                    to_client.send(frame_data)
                    has_send += len(frame_data)
                fout.close()
                time.sleep(2)
                if not os.path.isdir(app.monitorPath + '/server-move'):
                    os.makedirs(app.monitorPath + '/server-move')
                try:
                    shutil.move(path, app.monitorPath + '/server-move/' + '/')
                except:
                    print('转移失败', '文件转移失败，请手动转移%s文件，以免重复上传' % path)
            # print("program exit normally:-> close socket")
            print("server run %s times" % server_runtimes)
            time.sleep(2)
            app.dataPath=''
#end of server module

if __name__ == "__main__":
    app= App()
    server_thread = threading.Thread(target=StartSocketServer)
    server_thread.setDaemon(True)  # 关闭主线程之后也关闭子线程
    server_thread.start()
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, app.monitorPath, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()
    observer.join()


