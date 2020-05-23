# -*- coding:utf-8 -*-
import csv
import os
import numpy as np
import pandas as pd
import pymysql
import time
import shutil
from pymysql import connect


class CsvToMysql(object):
    def __init__(self, hostname, port, user, passwd, db):
        self.dbname = db
        self.conn = connect(host=hostname, port=port, user=user, passwd=passwd, db=db)
        self.cursor = self.conn.cursor()


    def read_csv(self, fileName):
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

    def make_table_sql(self, df):
        # 将csv中的字段类型转换成mysql中的字段类型
        columns = df.columns.tolist()
        types = df.ftypes
        make_table = []
        make_field = []

        count = 0
        for item in columns:
            # 替换前两行id1,id2 为 device_id
            if count == 0:
                item1 = 'device_id'
                char = item1
                make_table.append(char)
                make_field.append(item1)
                count += 1
                continue
            elif count == 1 :
                count += 1
                continue
            item1 = '`' + item.replace(' ', '_').replace(':', '') + '`'
            if 'int' in types[item]:
                char = item1 + ' INT'
            elif 'float' in types[item]:
                char = item1 + ' FLOAT'
            elif 'object' in types[item]:
                char = item1 + ' VARCHAR(255)'
            elif 'datetime' in types[item]:
                char = item1 + ' DATETIME'
            else:
                char = item1 + ' VARCHAR(255)'
            # char = item1 + ' VARCHAR(255)'
            make_table.append(char)
            make_field.append(item1)
            count += 1
        return ','.join(make_table), ','.join(make_field)

    def csv2mysql(self, db_name, table_name, df, type):
        field1,field2 = self.make_table_sql(df)
        values = df.values.tolist()
        values = self.getDeviceId(values)
        self.insertAlarmInfo(type=type,values=values)
        # 如果type=5，执行位移模块的插入函数，位移模块和其余模块的表结构不同，所以需要单独一个函数处理
        if type == 4:
            self.insertDis(values)
        else:
            s = ','.join(['%s' for _ in range(len(df.columns) - 1)])
            try:
                self.cursor.executemany('insert into {}({}) values ({})'.format(table_name, field2, s), values)
            except Exception as e:
                print(e)
            finally:
                self.conn.commit()

    # 通过add获取device_id
    def getDeviceId(self,values):
        # 网络位置add = id1 - id2
        count = 0
        # 将id1 id2 替换为 device_id的值
        for value in values:
            add = str(value[0]) + '-' + str(value[1])
            self.cursor.execute('SELECT id FROM yzn_monitor_collection WHERE '+'`add`="'+add+'"')
            result = self.cursor.fetchall()
            # 如果add值数据库中不存在对应的传感器，则添加到noadd表中，并且删除此行数据
            if len(result) == 0:
                localtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                # self.cursor.execute('insert into yzn_noadd values("%s,%s")'%(add,localtime))
                #TODO change the sql sentence
                sql_insert = '''INSERT INTO yzn_noadd (`add`,`time`) VALUES('{0}', '{1}')'''. \
                    format(add,localtime)
                self.cursor.execute(sql_insert)
                del(values[count])
                continue

            del(values[count][0])
            values[count][0] = result[0][0]
            count += 1
        return values

    # 位移模块的数据插入
    def insertDis(self,values):
        table_name1 = 'yzn_displacement_data'
        field1 = 'device_id,`time`'
        s1 = ','.join(['%s' for _ in range(2)])
        values1 = []
        values1.append(values[0][:])
        table_name2 = 'yzn_displacement_time'
        field2 = 'd_id,`angle`,`length`'
        s2 = ','.join(['%s' for _ in range(3)])
        values2 = []
        del(values1[0][2])
        del(values1[0][2])
        try:
            self.cursor.executemany('insert into {}({}) values ({})'.format(table_name1, field1, s1), values1)
            lastid = self.cursor.lastrowid
            for value in values:
                del (value[0])
                values2.append(value[:])
            for i in range(len(values2)):
                values2[i][0] = lastid
            self.cursor.executemany('insert into {}({}) values ({})'.format(table_name2, field2, s2), values2)
            print(1)

        except Exception as e:
            print(e)
        finally:
            self.conn.commit()
        return

    #预警模块-获取预警值
    def getAlarm(self,id):
        self.cursor.execute('SELECT * FROM yzn_alarm_value WHERE `id`='+str(id))
        result = self.cursor.fetchall()
        if len(result) == 0:
            exit('The alarminfos of this mine is not assigned')
        list = {"temp" : result[0][1],
                "hum" : result[0][2],
                "wind" : result[0][3],
                "watertemp" : result[0][4],
                "waterpres" : result[0][5],
                "watervol" : result[0][6],
                "support" : result[0][7],
                "displace" : result[0][8],
                }
        return list

    #判断并插入预警信息
    def insertAlarmInfo(self,type,values):
        for value in values:
            deviceId = value[0]
            self.cursor.execute('SELECT mine_id FROM yzn_monitor_collection WHERE `id`='+str(deviceId))
            result = self.cursor.fetchall()
            mineId = result[0][0]
            self.alarm = self.getAlarm(mineId)
            t = value[1]
            if type==0:
                if value[2] >= self.alarm['temp']:
                    sql_insert = '''INSERT INTO yzn_alarm_info(time,mine_id,type,device_id,alarm_info)
                                     VALUES('{0}', {1}, '{2}', {3}, '{4}')'''. \
                        format(t,mineId,'温湿度',deviceId,'温度预警'+str(value[2]))
                    self.cursor.execute(sql_insert)
                if value[3] >= self.alarm['hum']:
                    sql_insert = '''INSERT INTO yzn_alarm_info(time,mine_id,type,device_id,alarm_info)
                                                         VALUES('{0}', {1}, '{2}', {3}, '{4}')'''. \
                        format(t, mineId, '温湿度', deviceId, '湿度预警' + str(value[3]))
                    self.cursor.execute(sql_insert)
            if type == 1:
                if value[2] >= self.alarm['wind']:
                    sql_insert = '''INSERT INTO yzn_alarm_info(time,mine_id,type,device_id,alarm_info)
                                                         VALUES('{0}', {1}, '{2}', {3}, '{4}')'''. \
                        format(t, mineId, '风速', deviceId, '风速预警' + str(value[2]))
                    self.cursor.execute(sql_insert)
            if type == 2:
                if value[2] >= self.alarm['support']:
                    sql_insert = '''INSERT INTO yzn_alarm_info(time,mine_id,type,device_id,alarm_info)
                                                         VALUES('{0}', {1}, '{2}', {3}, '{4}')'''. \
                        format(t, mineId, '支护应力', deviceId, '支护应力预警' + str(value[2]))
                    self.cursor.execute(sql_insert)
            if type == 3:
                if value[2] >= self.alarm['watertemp']:
                    sql_insert = '''INSERT INTO yzn_alarm_info(time,mine_id,type,device_id,alarm_info)
                                     VALUES('{0}', {1}, '{2}', {3}, '{4}')'''. \
                        format(t,mineId,'地下水',deviceId,'水温预警'+str(value[2]))
                    self.cursor.execute(sql_insert)
                if value[3] >= self.alarm['waterpres']:
                    sql_insert = '''INSERT INTO yzn_alarm_info(time,mine_id,type,device_id,alarm_info)
                                                         VALUES('{0}', {1}, '{2}', {3}, '{4}')'''. \
                        format(t, mineId, '地下水', deviceId, '水压预警' + str(value[3]))
                    self.cursor.execute(sql_insert)
                if value[4] >= self.alarm['watervol']:
                    sql_insert = '''INSERT INTO yzn_alarm_info(time,mine_id,type,device_id,alarm_info)
                                                         VALUES('{0}', {1}, '{2}', {3}, '{4}')'''. \
                        format(t, mineId, '地下水', deviceId, '水量预警' + str(value[4]))
                    self.cursor.execute(sql_insert)

    #插入成功后，移动文件
    def moveFile(self,fileName):
        # 数据移动：1-检测是否有对应文件夹，无则新建，然后转移
        dir = os.path.dirname(fileName.split('/')[-1])  # 获取父文件夹
        # print dir
        movedFolder = dir + "\\Moved"
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

if __name__ == "__main__":
    hostname = '47.93.14.103'
    port = 3306
    user = 'root'
    passwd = 'Mining514'
    db = 'yzncms'
    M = CsvToMysql(hostname=hostname, port=port, user=user, passwd=passwd, db=db)

    #获取预警值
    # csv文件目录
    dir = 'D:\data'
    type = 0
    file_list = os.listdir(dir)
    for i in range(len(file_list)):
        file_path = os.path.join(dir, file_list[i])
        if os.path.isfile(file_path):
            M.read_csv(file_path,type)
            M.moveFile(file_path,'./move/')