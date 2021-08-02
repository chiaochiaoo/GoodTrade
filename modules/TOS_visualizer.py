#import matplotlib
import matplotlib.pyplot as plt
import numpy as np
# matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.figure import Figure


from tkinter import *
import time
import threading
import json
import csv
import requests
import threading
import socket

def find_between(data, first, last):
    try:
        start = data.index(first) + len(first)
        end = data.index(last, start)
        return data[start:end]
    except ValueError:
        return data
def get_sec(time_str):
    """Get Seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

class moudule_2:
	def __init__(self,  window,symbol):
		self.window = window
		#self.box = Entry(window)
		# self.button = Button (window, text="check", command=self.plot)
		# self.box.pack ()
		# self.button.pack()
		# self.button2 = Button (window, text="Simulated", command=self.simulated_input)
		# self.button2.pack()
		self.i = 0

		self.update_complete = IntVar()

		self.vol1 = IntVar()
		self.trade1 = IntVar()

		self.vol5 = IntVar()
		self.trade5 = IntVar()

		self.vol60 = IntVar()
		self.trade60 = IntVar()

		self.c1={"tms":0,"v":0,"t":0,"ts":[],"vs":[]}
		self.c5={"tms":0,"v":0,"t":0,"ts":[],"vs":[]}
		self.c60={"tms":0,"v":0,"t":0,"ts":[],"vs":[]}

		self.plot()
		#self.register(symbol)

		dc = threading.Thread(target=self.TOS_listener, daemon=True)
		dc.start()

		#up = threading.Thread(target=self.update_graph, daemon=True)
		#up.start()

		#self.setx()

		#self.TOS_listener()
		#self.update_graph()



	def setx(self,count):
		#self.v.append(self.v[-1]+1)
		#self.ac.cla()
		self.vol[self.timeframe[0]+"current"].set_data(1+count/100,[0,1])
		print(self.vol[self.timeframe[0]+"current"].get_data())
		self.figc.canvas.draw()


	def TOS_listener(self):
		UDP_IP = "127.0.0.1"
		UDP_PORT = 4401

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((UDP_IP, UDP_PORT))

		print("socket start")

		trades= [self.trade1,self.trade5,self.trade60]
		volume = [self.vol1,self.vol5,self.vol60]
		d = [self.c1,self.c5,self.c60]

		while True:
			data, addr = sock.recvfrom(1024)
			stream_data = str(data)

			time = find_between(stream_data, "MarketTime=", ",")
			t1 = get_sec(time[:-4])
			size = int(find_between(stream_data, "Size=", ","))
			price = float(find_between(stream_data, "Price=", ","))

			t5 = t1//5
			t60= t1//60

			t = [t1,t5,t60]
			increment = False
			increment_ = 0
			for i in range(3):

				timestamp = t[i]
				obj = d[i]

				if timestamp != obj["tms"]:
					obj["tms"]=timestamp
					obj["ts"].append(obj["t"])
					obj["vs"].append(obj["v"])

					volume[i].set(obj["v"])
					trades[i].set(obj["t"])

					increment = True
					obj["v"]=size
					obj["t"]=1
				else:
					obj["v"]+=size
					obj["t"]+=1
					#print(self.c1)

			if increment: ###bar, every second. Distribution, every 5 second. (with cap capacity.)
				#print("update")
				self.update_complete.set(self.update_complete.get()+1)
				#print(self.c1)


				#for i in range(3):
					# self.vol[self.timeframe[i]].cla()
					# self.trades[self.timeframe[i]].cla()

					# self.vol[self.timeframe[i]].boxplot(obj["vs"],vert=False)
					# self.vol[self.timeframe[i]].set_title(self.timeframe[i%3]+" "+self.types[0])
					# self.trades[self.timeframe[i]].boxplot(obj["ts"],vert=False)
					# self.trades[self.timeframe[i]].set_title(self.timeframe[i%3]+" "+self.types[1])

					#print(type(self.vol[self.timeframe[i]+"current"]))
				# 	self.vol[self.timeframe[i]+"current"].set_data(1,[0,1])
				# 	self.trades[self.timeframe[i]+"current"].set_data(1.15,[0,1])

				# self.fig.canvas.draw()

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


	def update_curret(self,a,b,c):
		#Call every second.
		#print("update chart")
		vol = [self.vol1,self.vol5,self.vol60]
		tra = [self.trade1,self.trade5,self.trade60]
		
		if self.update_complete.get()%10==0:

			d = [self.c1,self.c5,self.c60]
			for i in range(3):

				obj=d[i]
				self.vol[self.timeframe[i]].cla()
				self.trades[self.timeframe[i]].cla()

				self.vol[self.timeframe[i]].axvline(vol[i].get(),color="r")

				self.vol[self.timeframe[i]].boxplot(obj["vs"],vert=False)
				self.vol[self.timeframe[i]].set_title(self.timeframe[i%3]+" "+self.types[0])

				self.trades[self.timeframe[i]].axvline(tra[i].get(),color="r")
				self.trades[self.timeframe[i]].boxplot(obj["ts"],vert=False)
				self.trades[self.timeframe[i]].set_title(self.timeframe[i%3]+" "+self.types[1])

		else:
			for i in range(3):
				self.vol[self.timeframe[i%3]+"current"].set_data(vol[i].get(),[0,1])
				self.trades[self.timeframe[i%3]+"current"].set_data(tra[i].get(),[0,1])

			print("only current,",self.vol1.get())
		self.figc.canvas.draw()

	def update_chart(self):
		chart.set_data(val.get(),[0,1])
		self.figc.canvas.draw()

	def plot (self):

		self.figc, axs = plt.subplots(2,3,figsize=(15,7))
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
		#print(self.vol)

		self.update_complete.trace('w',self.update_curret)

		self.canvas = FigureCanvasTkAgg(self.figc, master=self.window)
		self.canvas.get_tk_widget().pack()
		self.canvas.draw()

	def register(self,symbol):
		postbody = "http://localhost:8080/SetOutput?symbol=" + symbol + "&feedtype=TOS&output=4401&status=on"
		r= requests.post(postbody)
		print("status:",r.status_code)


"""
b'LocalTime=11:38:56.592,Message=TOS,MarketTime=11:38:56.839,Symbol=XLE.AM,Type=0,Price=49.09000,Size=230,Source=25,Condition= ,Tick=?,Mmid=Z,SubMarketId=32,Date=2021-08-02,BuyerId=0,SellerId=0\n'
b'LocalTime=11:38:56.593,Message=TOS,MarketTime=11:38:56.839,Symbol=XLE.AM,Type=0,Price=49.09000,Size=90,Source=25,Condition= ,Tick=?,Mmid=Z,SubMarketId=32,Date=2021-08-02,BuyerId=0,SellerId=0\n'
b'LocalTime=11:38:56.593,Message=TOS,MarketTime=11:38:56.839,Symbol=XLE.AM,Type=0,Price=49.09000,Size=180,Source=25,Condition= ,Tick=?,Mmid=Z,SubMarketId=32,Date=2021-08-02,BuyerId=0,SellerId=0\n'
b'LocalTime=11:38:56.593,Message=TOS,MarketTime=11:38:56.839,Symbol=XLE.AM,Type=0,Price=49.09000,Size=270,Source=25,Condition= ,Tick=?,Mmid=Z,SubMarketId=32,Date=2021-08-02,BuyerId=0,SellerId=0\n'
b'LocalTime=11:38:56.593,Message=TOS,MarketTime=11:38:56.839,Symbol=XLE.AM,Type=0,Price=49.09000,Size=260,Source=25,Condition= ,Tick=?,Mmid=Z,SubMarketId=32,Date=2021-08-02,BuyerId=0,SellerId=0\n'
b'LocalTime=11:38:56.593,Message=TOS,MarketTime=11:38:56.839,Symbol=XLE.AM,Type=0,Price=49.09000,Size=10,Source=25,Condition= ,Tick=?,Mmid=Z,SubMarketId=32,Date=2021-08-02,BuyerId=0,SellerId=0\n'
b'LocalTime=11:38:56.593,Message=TOS,MarketTime=11:38:56.839,Symbol=XLE.AM,Type=0,Price=49.09000,Size=270,Source=25,Condition= ,Tick=?,Mmid=Z,SubMarketId=32,Date=2021-08-02,BuyerId=0,SellerId=0\n'
"""

window= Tk()
start= moudule_2(window,"XLE.AM")
window.mainloop()