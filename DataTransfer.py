# -*- coding:utf-8 -*-
import tkinter as tk
import os
import shutil
import socket
import threading
import time as T
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askdirectory
import tkutils as tku
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

window = tk.Tk()
window.title('Data Transfer Tool for Server and Client')
window.geometry('500x300')
#切断socket的变量
stop_socket = False
hostname = socket.gethostname()
ip_str = socket.gethostbyname(hostname)
port_str = 8105
var_path = tk.StringVar()
var_path.set("C:/Users/123/Desktop/DisplacementMon/Liang")
var_Script_type = tk.StringVar()
var_comment_text = tk.StringVar()
var_comment_text.set("请选择需要启动的脚本。")
var_mess_text = tk.StringVar()
var_mess_text.set("传输监测信息")
var_delta_time_text = tk.StringVar()
var_ip = tk.StringVar()
var_ip.set(ip_str)
var_port = tk.StringVar()
var_port.set(port_str)
var_runtimes_text = tk.StringVar()
var_runtimes_text.set("socket循环信息")

#socket server module
def StartSocketServer():
    s_server = socket.socket()
    print("Starting to create socket server")
    host = ''
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
    while not stop_socket:
        server_runtimes += 1
        path = var_path.get()
        dir = os.listdir(path)
        f_num = len(dir)
        for f in dir:
            if f[-4:] != ".csv":
                f_num = f_num - 1
        to_client.send(str(f_num))
        to_client.recv(8)
        # server move ; client move
        for file in dir:
            if not stop_socket:
                if file[-4:] == ".csv":
                    file_size = os.path.getsize(path + '/' + file)
                    # print('正在传输文件：%s' % file)
                    var_mess_text.set('正在传输文件：' + file + '\n本次已传输'+str(file_num)+'个文件。')
                    file_num += 1
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
                    T.sleep(5)
                    if not os.path.isdir(path + '/server-move'):
                        os.makedirs(path + '/server-move')
                    try:
                        shutil.move(path + '/' + file, path + '/server-move/' + '/')
                    except:
                        messagebox.showwarning('转移失败','文件转移失败，请手动转移%s文件，以免重复上传' % file)
                else:
                    print ("非csv文件不传输")
            else:
                break
        # print("program exit normally:-> close socket")
        if stop_socket:
            print ("program exit normally:-> close socket")
        else:
            T.sleep(60)#固定为60s监测一次
            print("server run %s times" % server_runtimes)
            var_runtimes_text.set("暂无数据传输，服务器已经监测文件夹%s次。" % str(server_runtimes))
    print("stoped by stop_socket variable")
#end of server module
#socket client module
def StartSocketClient():
    s = socket.socket()  # 创建 socket 对象
    host = socket.gethostname()  # 获取本地主机名
    s.connect((ip_str, int(port_str)))
    s.send("\xAA\x96\xAC\x00\x01\x00\x01\x69")
    path = var_path.get()+"/clientFiles/"
    while not stop_socket:  # 进入循环，不断接受客户端的链接请求
        file_num = s.recv(1024)
        # print(file_num)
        s.send(file_num)
        if not file_num == "":
            file_num = int(file_num)
            for file_end in range(0, file_num):
                file_info = s.recv(80)
                # print(file_info)
                filename, filesize = str(file_info).split('|')
                s.send(filesize)
                # print(filesize)
                filesize = int(filesize)
                if not os.path.isdir(path):
                    os.makedirs(path)
                f_pic = open(path + filename, "ab")
                has_receive = 0
                # file_type = s.recv(80)
                while has_receive < filesize:
                    picture_date = s.recv(1)
                    f_pic.write(picture_date)
                    has_receive += len(picture_date)
                # time.sleep(2)
                f_pic.close()
                # csvToSQL("./client/" + filename)
                var_comment_text.set("成功接收%s文件，正在持续接收中..." % filename)
            else:
                print("无数据，等待下次监听")
    s.close()
#end of client module
#thread
server_thread = threading.Thread(target=StartSocketServer)
server_thread.setDaemon(True)#关闭主线程之后也关闭子线程
client_thread = threading.Thread(target=StartSocketClient)
client_thread.setDaemon(True)#关闭主线程之后也关闭子线程
def StartBt():
    # print("start bt down")
    # print (comboxlist.get())#获得Combobox选定项
    # print(var_delta_time_text.get() == "")
    # print(var_path.get()=="")
    #输入数字的检测
    # try:
    #     int(delta_time_entry.get())
    # except:
    #
    #     messagebox.showwarning('整型判断','输入的不是整型数字，请输入整型秒数。')
    global stop_socket
    stop_socket = False
    #时间间隔、path、脚本选择均完成
    if var_path.get() != "" and comboxlist.get() != "请选择":
        if len(str(ip.get()).split('.'))!=4:
            messagebox.showwarning('IP检测','IP地址不正确，请检查IP地址格式后重试。')
        else:
            # print(stop_socket)
            global ip_str,port_str
            ip_str=ip.get()
            port_str=port.get()
            if var_Script_type.get() == "server":
                server_thread.start()
            elif var_Script_type.get() == "client":
                client_thread.start()
            elif var_Script_type.get() == "both server and client":
                server_thread.start()
                client_thread.start()
            else:
                print("default print for script type test")
            # runTask(runForUploaded,second=int(var_delta_time_text.get()))

    else:
        messagebox.showwarning('信息不全','请完善信息后重试')
    #测试socket启停
def StopBtDown():
    global stop_socket
    stop_socket = True
    messagebox.showwarning('强制停止','强制停止程序后，如果需要再次启动程序，需要将本程序关闭，并在此开启后方可正常运行。')
    var_mess_text.set("传输暂停，请重启程序以继续进行。")
def PathBT():
    path_ = askdirectory()
    var_path.set(path_)
def ComboxChange(*args):
    print (comboxlist.get())
    if comboxlist.get() == "client":
        var_comment_text.set("等待接收文件...")
        var_runtimes_text.set("Client端，正在接收文件。")
    elif comboxlist.get() == "server":
        var_comment_text.set("本电脑作为server启动。")
    elif comboxlist.get() == "both server and client":
        var_comment_text.set("本电脑同时运行server和client脚本。")
    else:
        var_comment_text.set("请选择需要启动的脚本。")

#components
# delta_time_title = tk.Label(window,text="时间间隔",font=('黑体',12))
# delta_time_title.place(x = 10, y = 10, width=75, height=25)
# delta_time_entry = tk.Entry(window,font=('黑体',12),textvariable=var_delta_time_text)
# delta_time_entry.place(x=85,y=10,width=150,height=25)
# delta_time_unit = tk.Label(window,text="S",font=('黑体',12))
# delta_time_unit.place(x=235,y=10,width=25,height=25)
tku.center_window(window)               # 将窗体移动到屏幕中央
window.iconbitmap("logo.ico")# 窗体图标
window.title("位移监测数据传输工具 Mining514_02483689193")
data_path = tk.Label(window,text="路径",font=('黑体',12))
data_path.place(x = 10, y = 35, width=75, height=25)
data_path_entry = tk.Entry(window,textvariable=var_path)
data_path_entry.place(x=85,y=35,width=350,height=25)
path_button = tk.Button(window,text="...",font=('黑体',12),command=PathBT)
path_button.place(x=440,y=35,width=25,height=25)
#server client选择按钮
combox_label = tk.Label(window,text="启动脚本",font=('黑体',12))
combox_label.place(x=10,y=60,width=75,height=25)
# comvalue=ttk.StringVar()#窗体自带的文本，新建一个值
comboxlist=ttk.Combobox(window,textvariable=var_Script_type) #初始化
comboxlist["values"]=("请选择","server","client","both server and client")
comboxlist.current(0)
comboxlist.place(x=85,y=60,width=150,height=25)
comboxlist.bind("<<ComboboxSelected>>",ComboxChange)
#IP and Port
ip_label = tk.Label(window,text="IP",font=('黑体',12))
ip_label.place(x=240,y=60,width=20,height=25)
ip = tk.Entry(window,textvariable=var_ip,font=('黑体',12))
ip.place(x=260,y=60,width=130,height=25)
port_label = tk.Label(window,text="Port",font=('黑体',12))
port_label.place(x=400,y=60,width=40,height=25)
port = tk.Entry(window,textvariable=var_port,font=('黑体',12))
port.place(x=440,y=60,width=50,height=25)
hide_items = [ip_label,ip,port_label,port]
#
Comment = tk.Label(window,textvariable=var_comment_text,bg="Grey",fg="red",font=('黑体',12))
Comment.place(x=10,y=90,width=480,height=50)
#messageField
messageField = tk.Label(window,textvariable=var_mess_text,bg="Orange",fg="white",font=('黑体',12))
messageField.place(x=10,y=150,width=480,height=50)
#runtimemessField
runtimes = tk.Label(window,textvariable=var_runtimes_text,bg="Black",fg="white",font=('黑体',12))
runtimes.place(x=10,y=210,width=480,height=50)
#开始-结束按钮
Start_Btn = tk.Button(window,text="运行",font=('黑体',12),command=StartBt)
Start_Btn.place(x=175,y=275,width=50,height=25)
End_Btn = tk.Button(window,text="停止",font=('黑体',12),command=StopBtDown)
End_Btn.place(x=300,y=275,width=50,height=25)



window.mainloop()