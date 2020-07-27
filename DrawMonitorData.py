# -*- coding:utf-8 -*-

import sys
import matplotlib
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from Tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
import cmath
import math
reload(sys)
sys.setdefaultencoding('utf8')


root = Tk()
root.title('位移实时监测')
f = Figure(figsize=(5, 4), dpi=100)
a = f.add_subplot(111)  # 添加子图:1行1列第1个
# 数据
data = pd.read_csv('C:/Users/123/Desktop/motor20200109/2020-07-08 18-59-52ldat.csv', sep=',', header=None,
                       names=['Theata', 'Radius', 'Quality'])
dataTheata = data['Theata'].values.tolist()
dataRadius = data['Radius'].values.tolist()
x = []
y = []
delta = 170  # 矫正值
for id in range(len(dataTheata)):
    if not dataRadius[id] < 0:
        x.append(dataRadius[id] * cmath.cos(math.radians(dataTheata[id] + delta)))
        y.append(dataRadius[id] * cmath.sin(math.radians(dataTheata[id] + delta)))
a.scatter(x,y,color='red')
a.plot(x,y)

# 将绘制的图形显示到tkinter:创建属于root的canvas画布,并将图f置于画布上
canvas = FigureCanvasTkAgg(f, master=root)
canvas.draw()  # 注意show方法已经过时了,这里改用draw
canvas.get_tk_widget().pack(fill=BOTH,expand=1)  # 随窗口大小调整而调整

# matplotlib的导航工具栏显示上来(默认是不会显示它的)
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas._tkcanvas.pack(expand=1)

# 主循环
root.mainloop()




# #生成范例数据
# r = 2 * np.random.rand(100) #生成100个服从“0~1”均匀分布的随机样本值
# theta = 2 * np.pi * np.random.rand(100) #生成角度
# area = 100 * r**2 #面积
# colors = theta #颜色
# ax = plt.subplot(111, projection='polar')
# #projection为画图样式，除'polar'外还有'aitoff', 'hammer', 'lambert'等
# c = ax.scatter(theta, r, c=colors, s=area, cmap='cool', alpha=0.75)
# #ax.scatter为绘制散点图函数
# plt.show()