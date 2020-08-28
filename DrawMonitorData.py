# -*- coding:utf-8 -*-
import os
import time
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas as pd
from tkinter.filedialog import askdirectory
from watchdog.observers import Observer
from tkinter import messagebox
from watchdog.events import *
import tkutils as tku
import math
import threading
import win32com.client
import Register

def watchFile(datapath):
    print("线程开始")
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, datapath, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(10)#影响了实时传输的数据是否能正常显示
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def encrypt(key, content):  # key:密钥,content:明文
    EncryptedData = win32com.client.Dispatch('CAPICOM.EncryptedData')
    EncryptedData.Algorithm.KeyLength = 5
    EncryptedData.Algorithm.Name = 2
    EncryptedData.SetSecret(key)
    EncryptedData.Content = content
    return EncryptedData.Encrypt()
def decrypt(key, content):  # key:密钥,content:密文
    EncryptedData = win32com.client.Dispatch('CAPICOM.EncryptedData')
    EncryptedData.Algorithm.KeyLength = 5
    EncryptedData.Algorithm.Name = 2
    EncryptedData.SetSecret(key)
    EncryptedData.Decrypt(content)
    str = EncryptedData.Content
    return str
def get_license():
    f = open("./conf.ini")
    code = f.read()
    # print (code)


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("%dx%d" % (800, 600))   # 窗体尺寸
        tku.center_window(self.root)               # 将窗体移动到屏幕中央
        self.root.iconbitmap("logo.ico")# 窗体图标
        self.root.title("位移监测数据可视化 copyright：Mining514_02483689193")
        self.root.resizable(True, True)            # 设置窗体不可改变大小
        self.no_title = False
        self.dataPath=os.path.dirname(__file__)
        self.filePath=""
        self.modifyTheata=tk.StringVar(value='110')
        # code = "BFEBFBFF00030678"
        # self.mainboardCode = tk.StringVar(value=code)
        self.fileList=[]
        self.ShowAllData = tk.IntVar(value=0)
        self.currentFilename=''
        self.show_title()
        self.body()


    def body(self):
        #上部工具条
        self.frame_topBar = tk.Frame(self.root,height=80, bg="white", bd=2)
        self.frame_topBar.pack(side=tk.TOP,  fill=tk.X)
        #数据路径按钮
        self.dataPathBt = tk.Button(self.frame_topBar, text="请选择路径", command=self.dataPathSelection)
        self.dataPathBt.pack(side=tk.LEFT,padx=10)
        #设备选择--隐藏未开发
        # self.deviceSelect = ttk.Combobox(self.frame_topBar,values=['device-a','device-b','device-c'])
        # self.deviceSelect.current(0)
        #
        # self.deviceSelect.pack(side=tk.LEFT,padx=10)
        #数据显示模式-20200730隐藏-----------------------
        # self.compareMode = tk.Checkbutton(self.frame_topBar,text='数据对比模式',onvalue=1,offvalue=0)
        # self.compareMode.pack(side=tk.LEFT,padx=10)
        #
        # self.realtimeUpdate = tk.Checkbutton(self.frame_topBar, text='实时更新', onvalue=1, offvalue=0)
        # self.realtimeUpdate.pack(side=tk.LEFT, padx=10)
        #----------------------------------------------
        tk.Label(self.frame_topBar,text="矫正角").pack(side=tk.LEFT,padx=10)
        self.theataEntry = tk.Entry(self.frame_topBar,width=10,textvariable=str(self.modifyTheata))
        self.theataEntry.pack(side=tk.LEFT,padx=10)
        tk.Button(self.frame_topBar,text='应用',command=self.applyModifyTheata).pack(side=tk.LEFT,padx=5)
        # self.machineCode = tk.Entry(self.frame_topBar, width=20,textvariable=self.mainboardCode)
        self.showAllHistoryDataToggle = tk.Checkbutton(self.frame_topBar,text="全部历史数据",variable=self.ShowAllData,command=self.updateListBox)
        self.showAllHistoryDataToggle.pack(side=tk.LEFT, padx=10)
        self.filePathLable= tk.Label(self.root,text=self.dataPath)
        self.filePathLable.pack(side=tk.TOP,ipadx=5,fill=tk.X)
        #左侧列表
        self.frame_leftList = tk.Frame(self.root,bg='yellow',bd=2,width=200)
        self.frame_leftList.pack(side=tk.LEFT, fill=tk.Y)

        self.scrollbar = tk.Scrollbar(self.frame_leftList)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listBox = tk.Listbox(self.frame_leftList,yscrollcommand=self.scrollbar.set,height=50,width=30)#height对应的是列表显示行数，默认为10，调整后即可自适应Y变化
        self.file_listBox.pack(side=tk.TOP, fill=tk.Y)
        self.file_listBox.bind("<Double-1>",self.listboxSelcClick)

        #绘图区域
        self.f = Figure(figsize=(3, 3), dpi=100)#为了适应小屏幕的分辨率将尺寸缩小
        self.a = self.f.add_subplot(111)  # 添加子图:1行1列第1个

        # 将绘制的图形显示到tkinter:创建属于root的canvas画布,并将图f置于画布上
        self.canvas = FigureCanvasTkAgg(self.f, master=self.root)
        self.canvas.draw_idle()  # 注意show方法已经过时了,这里改用draw
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)  # 随窗口大小调整而调整

        # matplotlib的导航工具栏显示上来(默认是不会显示它的)
        toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        toolbar.update()
        self.canvas._tkcanvas.pack(expand=1)

    def show_title(self, *args):
        self.root.overrideredirect(self.no_title)
        self.no_title = not self.no_title
    def dataPathSelection(self):
        authorizedStatus = Register.CheckAuthorized()
        localMachineCode = Register.DesEncrypt(Register.getCVolumeSerialNumber())
        # print(localMachineCode)
        # print(authorizedStatus)
        if str(authorizedStatus) == str(localMachineCode):
            print("机器码识别准确")
            # 选择数据路径
            self.dataPath = askdirectory()
            self.updateListBox()
            watchThreading = threading.Thread(target=watchFile, name="watchthreading", args=((self.dataPath,)))
            watchThreading.setDaemon(True)
            watchThreading.start()
        else:
            messagebox.showwarning("注册检验", "机器码不正确，请联系管理员，024-83689193")
            self.root.quit()


    def selectListBox(self,filepath):

        self.a.cla()#clear plot
        data = pd.read_csv(filepath, sep=',', header=None,
                           names=['Theata', 'Radius', 'Quality'])
        dataTheata = data['Theata'].values.tolist()
        dataRadius = data['Radius'].values.tolist()
        x = []
        y = []
        try:
            delta = float(self.theataEntry.get()) # 矫正值
        except:
            delta=0
        #记录是否有异常
        errorID=0
        #规避数据重复异常
        deltaTheata=0
        loopTimes=0
        for i in range(len(dataTheata)-1):
            if float(dataTheata[i])>=0 and float(dataTheata[i+1])>=0:
                deltaTheata=float(dataTheata[i+1])-float(dataTheata[i])
                break
        if deltaTheata>0:
            loopTimes=int(360/deltaTheata)+1
        print ("旋转角度%s°,应有数据量%s个" % (deltaTheata,loopTimes))
        #
        try:
            if loopTimes>0:
                for id in range(loopTimes):
                    if not float(dataRadius[id]) < 0:
                        if not float(dataRadius[id]) > 10000:#暂时限制不大于10m的范围
                            if not float(dataTheata[id]) < 0:
                                # cmath是复数运算
                                try:
                                    x.append(
                                        float(dataRadius[id]) * math.cos(
                                            math.radians(float(dataTheata[id]) + float(delta))))
                                    y.append(
                                        float(dataRadius[id]) * math.sin(
                                            math.radians(float(dataTheata[id]) + float(delta))))
                                except:
                                    errorID += 1
                print("忽略异常点%s个。" % errorID)
                # 闭合曲线
                x.append(x[0])
                y.append(y[0])
                # 绘图区域
                self.a.set_title(filepath.split('/')[-1])
                self.a.scatter(x, y, color='red')
                self.a.plot(x, y, color='blue')
                self.canvas.draw_idle()
            else:
                self.a.set_title("数据异常")
        except:
            self.a.set_title("数据异常")


    def listboxSelcClick(self,event):
        # print(self.file_listBox.curselection())
        self.currentFilename= self.fileList[self.file_listBox.curselection()[0]]
        # print(self.currentFilename)
        self.filePath=self.dataPath+"/"+self.currentFilename
        # print(self.filePath)
        self.selectListBox(self.filePath)

    def applyModifyTheata(self):
        self.selectListBox(self.filePath)

    def updateListBox(self):
        # print("文件被修改了 %s" % event.src_path)
        del self.fileList[:]  # 清空数据
        self.file_listBox.delete(0, tk.END)
        self.filePathLable["text"] = "监测文件夹：" + self.dataPath
        # print self.dataPath
        dir = os.listdir(self.dataPath)
        f_num = len(dir)
        f_Name = []
        for f in dir:
            if f[-4:] != ".csv":
                f_num = f_num - 1
            else:
                f_Name.append(f)
                # self.file_listBox.insert(tk.END, f)

        f_Name.reverse()
        self.fileList = f_Name
        # print(self.ShowAllData)
        if int(self.ShowAllData.get()) == 0:  # 仅显示最新的15条数据
            for item in f_Name[:15]:
                self.file_listBox.insert(tk.END, item)
        else:
            for item in f_Name:
                self.file_listBox.insert(tk.END, item)
        # app.file_listBox.insert(tk.END, str(event.src_path).split('\\')[-1])



class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        app.updateListBox()
        app.selectListBox(event.src_path)
        app.filePath = event.src_path
    def on_created(self, event):
        app.updateListBox()
        app.selectListBox(event.src_path)
        app.filePath = event.src_path



if __name__ == "__main__":
    app = App()
    app.root.mainloop()





