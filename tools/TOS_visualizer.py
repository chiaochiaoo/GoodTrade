#import matplotlib
import matplotlib.pyplot as plt
import numpy as np
# matplotlib.use('TkAgg')


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.figure import Figure

import winsound 

import pandas as pd
from tkinter import *
import time
import threading
import json
import csv
import requests
import threading
import socket
import os

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
def ts_to_min(ts):
	h=ts//3600
	ts=ts%3600
	m=ts//60
	s=ts%60

	if h<10: h =str('0'+str(h))
	else:h=str(h)
	if m<10: m =str('0'+str(m))
	else:m=str(m)
	if s<10: s =str('0'+str(s)) 
	else:s=str(s)
	#print(m,s)
	return h+":"+m+":"+s

def IQR(x):
	
	if len(x)> 5:
		q75, q25 = np.percentile(x, [75 ,25])
		iqr = (q75 - q25)*1.5
		### only take the good one.
		y = []
		for i in x:
			if (i <= q75 + iqr) and (i >= q25 - iqr):
				y.append(i)
				
		x = y[:]
		#print(q75,q25,iqr)
		
	return x

class moudule_2:
	def __init__(self,  window):


		#self.alert_obj = sa.WaveObject.from_wave_file("chime.wav")

		self.window=window
		#self.all = LabelFrame(window).place(x=0,y=0,relheight=1,relwidth=1)


		#self.config = LabelFrame(self.window,text="Config").place(x=0,y=80,relheight=0.1,relwidth=1)
		#self.graph = LabelFrame(window,text="Graph").place(x=0,rely=1,relheight=0.9,relwidth=1)


		#self.box = Entry(window)
		self.symbol = None
		self.alert_sound = BooleanVar(value=True)

		self.p = DoubleVar(value=1)

		#v=LabelFrame(window).pack()

		self.symbol_reg = StringVar()

		Label(self.window,text="Symbol:").grid(column=1,row=1)
		Entry(self.window, text="symbol register",textvariable=self.symbol_reg).grid(column=2,row=1)
		Button(self.window, text="register", command=self.register).grid(column=3,row=1)

		Label(self.window,text="Alert threshold (Top X%)").grid(column=1,row=2)
		self.alert_config = Entry(self.window, text="alert sound",textvariable=self.p).grid(column=2,row=2)
		self.checker = Checkbutton(self.window, text="alert sound",variable=self.alert_sound).grid(column=3,row=2)

		self.i = 0

		self.update_complete = IntVar()

		self.reset_data()
		self.plot()

		dc = threading.Thread(target=self.TOS_listener, daemon=True)
		#dc = threading.Thread(target=self.simulated_input, daemon=True)

		dc.start()

		#up = threading.Thread(target=self.update_graph, daemon=True)
		#up.start()

		#self.setx()

		#self.TOS_listener()
		#self.update_graph()


	# def setx(self,count):
	# 	#self.v.append(self.v[-1]+1)
	# 	#self.ac.cla()
	# 	self.vol[self.timeframe[0]+"current"].set_data(1+count/100,[0,1])
	# 	print(self.vol[self.timeframe[0]+"current"].get_data())
	# 	self.figc.canvas.draw()

	def reset_data(self):


		self.vol1 = IntVar()
		self.trade1 = IntVar()

		self.vol5 = IntVar()
		self.trade5 = IntVar()

		self.vol60 = IntVar()
		self.trade60 = IntVar()

		self.default={"tms":0,"v":0,"t":0,"ts":[],"vs":[],"timestamps":[],"vvar":self.vol1,"tvar":self.trade1}

		self.c1={"tms":0,"v":0,"t":0,"ts":[],"vs":[],"vvar":self.vol1,"tvar":self.trade1}
		self.c5={"tms":0,"v":0,"t":0,"ts":[],"vs":[],"vvar":self.vol5,"tvar":self.trade5}
		self.c60={"tms":0,"v":0,"t":0,"ts":[],"vs":[],"vvar":self.vol60,"tvar":self.trade60}

	def update_chart(self):
		self.vol[self.timeframe[0]+"current"].set_data(self.update_complete.get(),[0,1])
		print(self.update_complete.get())
		self.figc.canvas.draw()

	def TOS_listener(self):
		UDP_IP = "127.0.0.1"
		UDP_PORT = 4401

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((UDP_IP, UDP_PORT))

		print("socket start")

		count = 0
		while True:
			data, addr = sock.recvfrom(1024)
			stream_data = str(data)

			symbol = find_between(stream_data, "Symbol=", ",")
			time = find_between(stream_data, "MarketTime=", ",")
			t1 = get_sec(time[:-4])
			size = int(find_between(stream_data, "Size=", ","))
			price = float(find_between(stream_data, "Price=", ","))

			#print(symbol,self.symbol,self.default)
			if symbol!=self.symbol:
				self.deregister(symbol)
			else:
				self.data_process(t1,size,price,time[:-4])


	def update_curret(self,a,b,c):
		#Call every second.
		#print("update chart")
		
		try:

			vol = [self.vol1,self.vol5,self.vol60]
			tra = [self.trade1,self.trade5,self.trade60]
			d = [self.default,self.c5,self.c60]

			if self.update_complete.get()%5==0:


				for i in range(2):

					obj=d[i]


					self.vol[self.timeframe[i]].cla()
					self.trades[self.timeframe[i]].cla()

					self.vol[self.timeframe[i]+"current"]=self.vol[self.timeframe[i]].axvline(vol[i].get(),color="r")

					self.vol[self.timeframe[i]].boxplot(obj["vs"],vert=False)
					#self.vol[self.timeframe[i]].set_xlim(-2,max(max(obj["vs"]),vol[i].get())+5)
					self.vol[self.timeframe[i]].set_title(self.timeframe[i%2]+" "+self.types[0])

					self.trades[self.timeframe[i]+"current"]=self.trades[self.timeframe[i]].axvline(tra[i].get(),color="r")
					self.trades[self.timeframe[i]].boxplot(obj["ts"],vert=False)
					#self.trades[self.timeframe[i]].set_xlim(-2,max(max(obj["ts"]),tra[i].get())+5)
					self.trades[self.timeframe[i]].set_title(self.timeframe[i%2]+" "+self.types[1])

				#print(self.default["timestamps"],self.default["vs"])
				#self.chart.cla()
				

				#self.spread_line.set_data(spread_time,self.spreads)

				#can i set a bit ahead of time?

			else:
				spread_time = pd.to_datetime(self.default["timestamps"],format='%H:%M:%S')

				self.chart.set_data(spread_time,self.default["vs"])
				self.chartframe.set_xlim(spread_time[0], spread_time[-1])
				self.chartframe.set_ylim(min(self.default["vs"])-0.1,max(self.default["vs"])+0.1)
				self.chartline.set_data(self.default["v"],[0,1])
			#print(self.default["tms"],self.c5["tms"],self.c5["vs"],sum(self.default["vs"][-5:]),self.vol5.get(),self.vol1.get())
			#print(self.default["vs"][-5:],sum(self.default["vs"][-60:]),self.vol60.get())
				#self.vol[self.timeframe[0]+"current"].set_data(self.update_complete.get(),[0,1])
			#print(self.c1["vs"],self.vol1.get())
			#print(self.chart.get_data())

			for i in range(2):
				obj=d[i]

				try:
					self.vol[self.timeframe[i]].set_xlim(max(max(obj["vs"]),vol[i].get())*-0.2,max(max(obj["vs"]),vol[i].get())*1.2)
					self.vol[self.timeframe[i%2]+"current"].set_data(vol[i].get(),[0,1])

					self.trades[self.timeframe[i]].set_xlim(max(max(obj["ts"]),tra[i].get())*-0.2,max(max(obj["ts"]),tra[i].get())*1.2)
					self.trades[self.timeframe[i%2]+"current"].set_data(tra[i].get(),[0,1])
				except Exception as e:
					print(e)
			self.f.canvas.draw()
		except Exception as e:
			print(e)

	def plot (self):

		
		self.timeframe = ["1s","5s"]
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
		self.f = plt.figure(1,figsize=(12,7))
		self.gs = self.f.add_gridspec(2, 4)


		self.chartframe = self.f.add_subplot(self.gs[0,:4])
		self.chart, = self.chartframe.plot([],[])
		self.chartline = self.chartframe.axhline(1,linestyle="--")

		self.vol1chart =self.f.add_subplot(self.gs[1,0])
		self.trade1chart =self.f.add_subplot(self.gs[1,1])
		self.vol5chart =self.f.add_subplot(self.gs[1,2])
		self.trade5chart = self.f.add_subplot(self.gs[1,3])

		self.vol["1s"] =self.vol1chart
		self.vol["5s"] =self.vol5chart
		self.trades["1s"] = self.trade1chart
		self.trades["5s"] =self.trade5chart

		self.vol["1s"+"current"] =self.vol1chart.axvline(1,linestyle="--")
		self.vol["5s"+"current"] =self.vol5chart.axvline(1,linestyle="--")
		self.trades["1s"+"current"] = self.trade1chart.axvline(1,linestyle="--")
		self.trades["5s"+"current"] =self.trade5chart.axvline(1,linestyle="--")

		#self.figc, axs = plt.subplots(2,3,figsize=(15,7))
		# for i in range(6):

		# 	axs[i//3][i%3].set_title(self.timeframe[i%3]+" "+self.types[i//3])

		# 	axs[i//3][i%3].boxplot([],flierprops=outlier,vert=False, whis=1)

		# 	total[i//3][self.timeframe[i%3]+"current"] = axs[i//3][i%3].axvline(1,linestyle="--")
		# 	#print(type(total[i//3][self.timeframe[i%3]+"current"]),total[i//3][self.timeframe[i%3]+"current"])
		# 	total[i//3][self.timeframe[i%3]] = axs[i//3][i%3]

		# 	#self.charts[title[i]] = axs[i//3][i%3]
		#print(self.vol)

		self.update_complete.trace('w',self.update_curret)

		self.canvas = FigureCanvasTkAgg(self.f, master=self.window)
		#self.canvas.get_tk_widget().pack()
		self.canvas.get_tk_widget().place(x=0,y=50,relheight=0.8,relwidth=0.8)
		#self.canvas.draw()

	def register(self):

		if self.symbol!=None:
			self.deregister(self.symbol)

		self.reset_data()

		symbol = self.symbol_reg.get().upper()

		print("registering:",symbol)
		self.symbol = symbol

		postbody = "http://localhost:8080/SetOutput?symbol=" + symbol + "&feedtype=TOS&output=4401&status=on"
		r= requests.post(postbody)
		print("status:",r.status_code)

	def deregister(self,symbol):

		postbody = "http://localhost:8080/Deregister?symbol=" + symbol + "&feedtype=TOS"
		r= requests.post(postbody)
		print("deregister status:",symbol,r.status_code)

	def update_interval(self,data,ts,v,t,interval):

		nts = ts//interval

		data["vvar"].set(sum(self.default["vs"][-interval:]))
		data["tvar"].set(sum(self.default["ts"][-interval:]))

		if nts != data["tms"]:

			data["tms"]=nts
			data["ts"].append(data["tvar"].get())
			data["vs"].append(data["vvar"].get())


	def simulated_input(self):

		trades= [self.trade1,self.trade5,self.trade60]
		volume = [self.vol1,self.vol5,self.vol60]


		count = 0
		with open('tos_test.csv') as csvfile:

			reader = csv.DictReader(csvfile)
			field = reader.fieldnames

			for row in reader:

				l=list(row.values())
				t1,size,price=int(l[0]),int(l[1]),float(l[2])

				self.data_process(t1,size,price)
				time.sleep(0.15)
				#print("next turn")

	def data_process(self,t1,vol,prize,t1str):

		if t1 > self.default["tms"]:
			#do two things. 1. update current second val. 2. update this value to all other bins.
			
			self.default["v"] = self.default["v"]//1000
			self.default["tms"]=t1

			if len(self.default["ts"])>360:
				self.default["ts"].pop(0)
				self.default["vs"].pop(0)
				self.default["timestamps"].pop(0)

			self.default["timestamps"].append(t1str)
			self.default["ts"].append(self.default["t"])
			self.default["vs"].append(self.default["v"])

			self.trade1.set(self.default["t"])
			self.vol1.set(self.default["v"])

			self.update_interval(self.c5,self.default["tms"],self.default["v"],self.default["t"],5)
			#self.update_interval(self.c60,self.default["tms"],self.default["v"],self.default["t"],60)
			try:
				self.alert_check()
			except Exception as e:
				print(e)
			self.update_complete.set(t1)

			self.default["v"] = vol
			self.default["t"] = 1
		else:
			self.default["v"]+=vol
			self.default["t"]+=1

	def alert_check(self):


		if self.alert_sound.get()==True:
			p = self.p.get()
			#print(p)
			x=100-p
			cutoff, q25 = np.percentile(self.default["vs"], [x ,0])

			if self.default["v"]>cutoff:
				try:
					winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
					#winsound.Beep(37,1)
					#playsound('chime.wav')
					print("alert triggered")
				except Exception as e:
					print(e)
	# def update_curret(self,a,b,c):
	# 	print("X")
	# 	pass


"""
b'LocalTime=11:38:56.592,Message=TOS,MarketTime=11:38:56.839,Symbol=XLE.AM,Type=0,Price=49.09000,Size=230,Source=25,Condition= ,Tick=?,Mmid=Z,SubMarketId=32,Date=2021-08-02,BuyerId=0,SellerId=0\n'
b'LocalTime=11:38:56.593,Message=TOS,MarketTime=11:38:56.839,Symbol=XLE.AM,Type=0,Price=49.09000,Size=90,Source=25,Condition= ,Tick=?,Mmid=Z,SubMarketId=32,Date=2021-08-02,BuyerId=0,SellerId=0\n'
b'LocalTime=11:38:56.593,Message=TOS,MarketTime=11:38:56.839,Symbol=XLE.AM,Type=0,Price=49.09000,Size=180,Source=25,Condition= ,Tick=?,Mmid=Z,SubMarketId=32,Date=2021-08-02,BuyerId=0,SellerId=0\n'
b'LocalTime=11:38:56.593,Message=TOS,MarketTime=11:38:56.839,Symbol=XLE.AM,Type=0,Price=49.09000,Size=270,Source=25,Condition= ,Tick=?,Mmid=Z,SubMarketId=32,Date=2021-08-02,BuyerId=0,SellerId=0\n'
b'LocalTime=11:38:56.593,Message=TOS,MarketTime=11:38:56.839,Symbol=XLE.AM,Type=0,Price=49.09000,Size=260,Source=25,Condition= ,Tick=?,Mmid=Z,SubMarketId=32,Date=2021-08-02,BuyerId=0,SellerId=0\n'
b'LocalTime=11:38:56.593,Message=TOS,MarketTime=11:38:56.839,Symbol=XLE.AM,Type=0,Price=49.09000,Size=10,Source=25,Condition= ,Tick=?,Mmid=Z,SubMarketId=32,Date=2021-08-02,BuyerId=0,SellerId=0\n'
b'LocalTime=11:38:56.593,Message=TOS,MarketTime=11:38:56.839,Symbol=XLE.AM,Type=0,Price=49.09000,Size=270,Source=25,Condition= ,Tick=?,Mmid=Z,SubMarketId=32,Date=2021-08-02,BuyerId=0,SellerId=0\n'
"""

# x=[1,2,3,4,5,6,7,8,9,10]
# q75, q25 = np.percentile(x, [95 ,25])
# print(q75,q25)
# playsound('chime.wav')
# playsound('chime.wav')


#winsound.Beep(37,1)

winsound.PlaySound("SystemExit", winsound.SND_ALIAS)

root = Tk() 
root.title("TOS visualizer") 
root.geometry("1800x900")
root.minsize(1500, 600)
root.maxsize(3000, 1500)

start= moudule_2(root)
root.mainloop()
os._exit(1) 
print("exit")