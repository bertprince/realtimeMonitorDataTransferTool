# -*- coding:utf-8 -*-
from datetime import date,time, datetime, timedelta
import pymysql
import random
import csv
import os
import pandas as pd
import shutil
import Tkinter
import numpy as np

#db_config={ 'user':'root','password':'mining514','host':'','database':'yzncms'}

def work():
    #create_csv(str(datetime.now()).replace(':','-'))
    path = r'C:\Users\123\Desktop\DisplacementMon\Liang'
    files = os.listdir(path)
    for file in files:
        if file[-4:] == ".csv":
            dir = path+'\\'+file
            filename = str.split(dir, '\\')[-1]
            # print(filename)
            DataProcessing(dir)
        # else:
        #     print(file[-4:])
def DataProcessing(fileName):
    data = pd.read_csv(fileName,encoding='utf-8',header=-1)#忽略表头,dataFrame格式。data.values即array格式
    dataDate = fileName.split("\\")[-1][0:19]
    # print (data)
    device_id = 31 #后续设置为可键入,mineID=11,monitor_type=3,add:1-100
    #数据处理

    #数据上传
    cnx = pymysql.connect("47.93.14.103", "root", "Mining514", "yzncms")
    cursor = cnx.cursor()
    #如果时间点和设备ID冲突，删除数据库原有数据，上传新数据
    sql_select = "select id from yzn_displacement_data where device_id = %s and time = %s"
    para_select = (device_id, dataDate)
    cursor.execute(sql_select, para_select)
    cnx.commit()
    exitID = cursor.fetchone()
    if not exitID==None:
        exitid = np.array(exitID,dtype=int)
    else:
        exitid = [0]
    #print exitid[0]
    if exitid[0]==0:
        #导入数据
        sql_insert = "insert into yzn_displacement_data(device_id,time) VALUES (%s,%s)"
        par_date = (device_id, dataDate)
        cursor.execute(sql_insert, par_date)
        dateid = cursor.lastrowid  # d_id 从数据库获取
        cnx.commit()
    else:
        #删除原有数据
        sql_deleteOriginalData = "DELETE FROM yzn_displacement_time WHERE d_id = %s"
        para_delete = (int(exitid[0]))
        cursor.execute(sql_deleteOriginalData,para_delete)
        cnx.commit()
        dateid = int(exitid[0])
        print("替换了一组数据。")
    for item in data.values:
        _angle = item[0]
        if item[1]>=0:
            _length = item[1]/1000
        else:
            _length = 0
        sql_insertDisdata = "insert into yzn_displacement_time(d_id,angle,length) VALUES(%s,%s,%s)"
        par_dis = (dateid, float(_angle), float(_length))
        cursor.execute(sql_insertDisdata, par_dis)
        cnx.commit()

    cursor.close()
    cnx.close()
    #数据移动：1-检测是否有对应文件夹，无则新建，然后转移
    dir = os.path.dirname(fileName)#获取父文件夹
    #print dir
    movedFolder = dir+"\\Moved"
    #print os.path.exists(movedFolder)
    if os.path.exists(movedFolder):
        try:
            shutil.copy2(fileName, movedFolder)
            os.remove(fileName)#先复制在删除，防止因目的地存在数据冲突而报错
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
    print ("finish uploaded data")
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
def create_csv(filename):
    path = filename+".csv"
    with open(path, 'wb') as f:
        csv_write = csv.writer(f)
        csv_head = ["good", "bad"]
        csv_write.writerow(csv_head)
# runTask(work, min=0.5)
# runTask(work, second=5)
work()

#init a window
#24小时自动休眠、清理、重置等
#end