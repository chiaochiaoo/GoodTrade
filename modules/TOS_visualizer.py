import matplotlib
import matplotlib.pyplot as plt
import numpy as np
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
#import matplotlib.animation as animation
from tkinter import *
import time
import threading
import json
import csv


class mclass:
	def __init__(self,  window):
		self.window = window
		self.box = Entry(window)


		self.plot()
		self.button = Button (window, text="check", command=self.plot)
		self.box.pack ()
		self.button.pack()
		self.button2 = Button (window, text="Simulated", command=self.simulated_input)
		self.button2.pack()
		self.i = 0


	def set(self):

		# self.ac.set_xlim(min(self.v)-self.i, max(self.v)+self.i)
		# self.i+=1
		self.v.append(self.v[-1]+1)
		self.ac.cla()
		#self.ac.boxplot(self.v,vert=False)
		self.line.set_data(self.v)
		self.fig.canvas.draw()

	def simulated_input(self):
		c1={"tms":0,"v":0,"t":0,"ts":[],"vs":[]}
		c5={"tms":0,"v":0,"t":0,"ts":[],"vs":[]}
		c60={"tms":0,"v":0,"t":0,"ts":[],"vs":[]}

		d=[c1,c5,c60]


		with open('test.csv') as csvfile:

			reader = csv.DictReader(csvfile)
			field = reader.fieldnames

			for row in reader:
				t1,p,v=int(row['timestamp'])//1000,float(row['price']),int(row['size'])
				t5=t1//5
				t60=t1//60

				t=[t1,t5,t60]

				increment = False
				for i in range(3):
					timestamp = t[i]
					obj = d[i]

					if timestamp != obj["tms"]:
						obj["tms"]=timestamp
						obj["ts"].append(obj["t"])
						obj["vs"].append(obj["v"])


						increment = True
 #       self.ac.cla()
						self.vol[self.timeframe[i]].cla()
						self.trades[self.timeframe[i]].cla()

						self.vol[self.timeframe[i]].boxplot(obj["vs"],vert=False)
						self.vol[self.timeframe[i]].set_title(self.timeframe[i%3]+" "+self.types[0])
						self.trades[self.timeframe[i]].boxplot(obj["ts"],vert=False)
						self.trades[self.timeframe[i]].set_title(self.timeframe[i%3]+" "+self.types[1])

						#print(type(self.vol[self.timeframe[i]+"current"]))
						self.vol[self.timeframe[i]+"current"].set_data([-1,1],1)
						self.trades[self.timeframe[i]+"current"].set_data([-1,1],obj["t"])

						obj["v"]=v
						obj["t"]=1
					else:
						obj["v"]+=v
						obj["t"]+=1
				if increment:
					self.fig.canvas.draw()
					#time.sleep(1)

		print("done")
	def plot (self):


		self.fig, axs = plt.subplots(2,3,figsize=(15,7))

		#title = ["1s Volume","5s Volume","1m Volume","1s Trades","5s Trades","1m Trades"]

		self.timeframe = ["1s","5s","1m"]
		self.types = ["Volume","Trades"]

		self.vol = {}
		self.trades = {}

		total =[self.vol,self.trades]

		outlier = dict(linewidth=3, color='darkgoldenrod',marker='o')

		self.charts={}

		# for i in range(4):
		# 	lst.append(d[i]["vs"])
		# for i in range(4):
		# 	lst.append(d[i]["ts"])

		for i in range(6):

			axs[i//3][i%3].set_title(self.timeframe[i%3]+" "+self.types[i//3])

			axs[i//3][i%3].boxplot([],flierprops=outlier,vert=False, whis=1)

			total[i//3][self.timeframe[i%3]+"current"] = axs[i//3][i%3].axvline(1,linestyle="--")
			#print(type(total[i//3][self.timeframe[i%3]+"current"]),total[i//3][self.timeframe[i%3]+"current"])
			total[i//3][self.timeframe[i%3]] = axs[i//3][i%3]

			#self.charts[title[i]] = axs[i//3][i%3]

		self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
		self.canvas.get_tk_widget().pack()



window= Tk()
start= mclass (window)
window.mainloop()