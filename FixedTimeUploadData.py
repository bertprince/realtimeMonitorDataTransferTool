# -*- coding:utf-8 -*-
import Tkinter as tk
import os
import shutil
import socket
import threading
import time as T
import tkMessageBox
import ttk
from datetime import datetime, timedelta
from tkFileDialog import askdirectory
import pandas as pd
import pymysql
import numpy as np
import time as T

window = tk.Tk()
window.title('Fixedtime Upload Data Tool')
window.geometry('500x300')
#切断socket的变量
stop_monitor = False
var_path = tk.StringVar()
var_path.set("C:/Users/123/Desktop/DisplacementMon/Liang")
var_upload_text = tk.StringVar()
var_upload_text.set("数据上传显示区域。")
var_mess_text = tk.StringVar()
var_mess_text.set("监测状态：停止！")
var_delta_time_text = tk.StringVar()
var_delta_time_text.set(2)
var_filesmonitor_text = tk.StringVar()
var_filesmonitor_text.set("")
fileNum = 0
#定时程序
def runTask(func, day=0, hour=0, min=0, second=0):
    # Init time
    now = datetime.now()
    strnow = now.strftime('%Y-%m-%d %H-%M-%S')
    print
    "now:", strnow
    # First next run time
    period = timedelta(days=day, hours=hour, minutes=min, seconds=second)
    next_time = now + period
    strnext_time = next_time.strftime('%Y-%m-%d %H-%M-%S')
    print
    "next run:", strnext_time
    while True:
        # Get system current time
        iter_now = datetime.now()
        iter_now_time = iter_now.strftime('%Y-%m-%d %H-%M-%S')
        if str(iter_now_time) == str(strnext_time):
            # Get every start work time
            print
            "start work: %s" % iter_now_time
            # Call task func
            func()
            print
            "task done."
            # Get next iteration time
            iter_time = iter_now + period
            strnext_time = iter_time.strftime('%Y-%m-%d %H-%M-%S')
            print
            "next_iter: %s" % strnext_time
            # Continue next iteration
            continue
#csvToMySQL
def csvToSQL(fileName):
    # hostname = '47.93.14.103'
    # port = 3306
    # user = 'root'
    # passwd = 'Mining514'
    # db = 'yzncms'
    # M = CsvToMysql(hostname=hostname, port=port, user=user, passwd=passwd, db=db)
    # M.read_csv(fileName)
    # M.moveFile(fileName)
    # print ("finish uploaded data")
    data = pd.read_csv(fileName, encoding='utf-8', header=-1)  # 忽略表头,dataFrame格式。data.values即array格式
    dataDate = fileName.split("/")[-1][0:19]
    # print (data)
    device_id = 31  # 后续设置为可键入,mineID=11,monitor_type=3,add:1-100
    # 数据处理
    # 数据上传
    cnx = pymysql.connect("47.93.14.103", "root", "Mining514", "yzncms")
    cursor = cnx.cursor()
    # 如果时间点和设备ID冲突，删除数据库原有数据，上传新数据
    sql_select = "select id from yzn_displacement_data where device_id = %s and time = %s"
    para_select = (device_id, dataDate)
    cursor.execute(sql_select, para_select)
    cnx.commit()
    exitID = cursor.fetchone()
    if not exitID == None:
        exitid = np.array(exitID, dtype=int)
    else:
        exitid = [0]
    # print exitid[0]
    if exitid[0] == 0:
        # 导入数据
        sql_insert = "insert into yzn_displacement_data(device_id,time) VALUES (%s,%s)"
        par_date = (device_id, dataDate)
        cursor.execute(sql_insert, par_date)
        dateid = cursor.lastrowid  # d_id 从数据库获取
        cnx.commit()
    else:
        # 删除原有数据
        sql_deleteOriginalData = "DELETE FROM yzn_displacement_time WHERE d_id = %s"
        para_delete = (int(exitid[0]))
        cursor.execute(sql_deleteOriginalData, para_delete)
        cnx.commit()
        dateid = int(exitid[0])
        print("替换了一组数据。")
    for item in data.values:
        if 0 <= item[0] <= 360:
            _angle = item[0]
        else:
            continue
        if item[1] >= 0:
            _length = item[1] / 1000
        else:
            _length = 0
        sql_insertDisdata = "insert into yzn_displacement_time(d_id,angle,length) VALUES(%s,%s,%s)"
        # print item[0]
        par_dis = (dateid, float(_angle), float(_length))
        cursor.execute(sql_insertDisdata, par_dis)
        cnx.commit()
    global fileNum
    fileNum += 1
    var_upload_text.set('已上传%s 条数据' % str(fileNum))
    # 数据移动：1-检测是否有对应文件夹，无则新建，然后转移
    # dir = os.path.dirname(fileName.split('/')[-1])  # 获取父文件夹
    # print dir
    movedFolder = var_path.get() + "/Moved"
    # print os.path.exists(movedFolder)
    if os.path.exists(movedFolder):
        try:
            shutil.copy2(fileName, movedFolder)
            os.remove(fileName)  # 先复制在删除，防止因目的地存在数据冲突而报错
            # shutil.move(fileName,movedFolder)
        except OSError as mess:
            print mess
    else:
        os.mkdir(movedFolder)
        try:
            shutil.copy2(fileName, movedFolder)
            os.remove(fileName)
            # shutil.move(fileName, movedFolder)
        except OSError as mess:
            print mess
#定时检测需要上传的数据
# NofileLoop = 0
def runForUploaded():
    files = os.listdir(var_path.get())
    file_num = len(files)
    for file in files:
        if file[-4:] != ".csv":
            file_num -= 1
    if file_num > 0:
        global NofileLoop
        NofileLoop = 0
        for file in files:
            if file[-4:] == ".csv":
                file_num -= 1
                var_filesmonitor_text.set("有%s个文件等待上传" % str(file_num))
                csvToSQL(var_path.get() + '/' + file)
        runForUploaded()
    else:
        global NofileLoop
        NofileLoop += 1
        sleeptime = int(var_delta_time_text.get()) * NofileLoop
        if sleeptime > 600:
            sleeptime = 600
        var_filesmonitor_text.set("程序休眠%s秒后运行" % str(sleeptime))
        T.sleep(sleeptime)
        runForUploaded()


#end
monitor_thread = threading.Thread(target=runForUploaded)
monitor_thread.setDaemon(True)#关闭主线程之后也关闭子线程
def StartBt():
    #输入数字的检测
    try:
        int(delta_time_entry.get())
    except:
        tkMessageBox.showwarning('整型判断','输入的不是整型数字，请输入整型秒数。')
    global stop_monitor
    stop_monitor = False
    #时间间隔、path、脚本选择均完成
    if var_delta_time_text.get() != "" and var_path.get() != "":
        monitor_thread.start()
        var_mess_text.set("监测状态：开始！")
    else:
        tkMessageBox.showwarning('信息不全','请完善信息后重试')
    #测试socket启停

def StopBtDown():
    window.destroy()
def PathBT():
    path_ = askdirectory()
    var_path.set(path_)
#components
delta_time_title = tk.Label(window,text="时间间隔",font=('黑体',12))
delta_time_title.place(x = 10, y = 10, width=75, height=25)
delta_time_entry = tk.Entry(window,font=('黑体',12),textvariable=var_delta_time_text)
delta_time_entry.place(x=85,y=10,width=150,height=25)
delta_time_unit = tk.Label(window,text="S",font=('黑体',12))
delta_time_unit.place(x=235,y=10,width=25,height=25)
data_path = tk.Label(window,text="路径",font=('黑体',12))
data_path.place(x = 10, y = 35, width=75, height=25)
data_path_entry = tk.Entry(window,textvariable=var_path)
data_path_entry.place(x=85,y=35,width=350,height=25)
path_button = tk.Button(window,text="...",font=('黑体',12),command=PathBT)
path_button.place(x=440,y=35,width=25,height=25)
Comment = tk.Label(window,textvariable=var_upload_text,bg="Grey",fg="red",font=('黑体',12))
Comment.place(x=10,y=90,width=480,height=50)
#messageField
messageField = tk.Label(window,textvariable=var_mess_text,bg="Orange",fg="white",font=('黑体',12))
messageField.place(x=10,y=150,width=480,height=50)
#runtimemessField
filesMonitor = tk.Label(window,textvariable=var_filesmonitor_text,bg="Black",fg="white",font=('黑体',12))
filesMonitor.place(x=10,y=210,width=480,height=50)
#开始-结束按钮
Start_Btn = tk.Button(window,text="运行",font=('黑体',12),command=StartBt)
Start_Btn.place(x=175,y=275,width=50,height=25)
End_Btn = tk.Button(window,text="停止",font=('黑体',12),command=StopBtDown)
End_Btn.place(x=300,y=275,width=50,height=25)



window.mainloop()