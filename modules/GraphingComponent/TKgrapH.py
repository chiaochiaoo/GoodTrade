import matplotlib

import numpy as np
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from tkinter import *

class mclass:
    def __init__(self,  window):
        self.window = window
        self.box = Entry(window)
        self.button = Button (window, text="check", command=self.plot)
        self.box.pack ()
        self.button.pack()

    def animate(self,i):
        #ser.reset_input_buffer()
        #data = ser.readline().decode("utf-8")
        #data_array = data.split(',')
        #yvalue = float(data_array[1])
        #self.a.clear()
        self.x.append(self.x[-1]+1)
        self.v.append(self.v[-1]+1)
        #self.a.scatter(self.v,self.x,color='red')
        self.line.set_data(self.v, self.x)
        self.line2.set_data(i,[0,1])
        #self.a.set_ylim(0, self.v)
        #self.a.set_xlim(0,self.p[-1]+1)
        self.ac.set_ylim(0, self.v[-1])
        print(i)
        print(self.line2.get_data())

    def plot (self):
        self.x=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.v= [16,16.31925,17.6394,16.003,17.2861,17.3131,19.1259,18.9694,22.0003,22.81226]
        self.p= [16.23697,     17.31653,     17.22094,     17.68631,     17.73641 ,    18.6368,
            19.32125,     19.31756 ,    21.20247  ,   22.41444   ,  22.11718  ,   22.12453]

        fig = Figure(figsize=(6,6))
        self.ac = fig.add_subplot(111)
        #self.a.scatter(self.v,self.x,color='red')
        self.line,=self.ac.plot(self.v,self.x,color='blue')

        self.ac.set_ylim(0, self.v[-1])

        self.line2 = self.ac.axvline(x=1,color="r")

        # self.a.invert_yaxis()

        # self.a.set_title ("Estimation Grid", fontsize=16)
        # self.a.set_ylabel("Y", fontsize=14)
        # self.a.set_xlabel("X", fontsize=14)

        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.get_tk_widget().pack()
        ani = animation.FuncAnimation(fig, self.animate, interval=1000, blit=False)
        canvas.draw()

window= Tk()
start= mclass (window)
window.mainloop()