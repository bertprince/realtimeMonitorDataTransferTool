# -*- coding: utf-8 -*-
import cmath
import os
import math
import time
import pandas as pd
import matplotlib.pyplot as plt
from watchdog.observers import Observer
from watchdog.events import *
dataPath=r"C:\Users\123\Desktop\DisplacementMon\Test"
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print("文件被修改了 %s" % event.src_path)

    def on_created(self, event):
        print("文件被创建了 %s" % event.src_path)
        data = pd.read_csv(event.src_path, sep=',', header=None,
                           names=['Theata', 'Radius', 'Quality'])
        dataTheata = data['Theata'].values.tolist()
        dataRadius = data['Radius'].values.tolist()
        x = []
        y = []

        try:
            delta = 170  # 矫正值
        except:
            delta = 0
        for id in range(len(dataTheata)):
            if not dataRadius[id] < 0:
                x.append(dataRadius[id] * cmath.cos(math.radians(dataTheata[id] + delta)))
                y.append(dataRadius[id] * cmath.sin(math.radians(dataTheata[id] + delta)))
        x.append(x[0])
        y.append(y[0])
        plt.scatter(x,y,color='red')
        plt.plot(x,y,color='green')
        plt.show()




def watchFile(path):
    print("线程开始")
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, dataPath, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()
    observer.join()





