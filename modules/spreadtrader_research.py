import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
from matplotlib.dates import DateFormatter
from scipy.stats import skew,kurtosis
import requests
import tkinter as tk                     
from tkinter import ttk 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys

timestamp = []
for i in range(240,1201):
	timestamp.append(i)
	
def SMA(lst,n):
	lst1= []
	if len(lst)>0:
		lst1.append(lst[0])
		for i in range(1,len(lst)):
			if i < n:
				lst1.append(mean(lst[:i+1]))
			else:
				lst1.append(mean(lst[i-n+1:i+1]))

		return np.array(lst1)
def mean(lst):
	return sum(lst)/len(lst)
def get_day(day_str):
	
	#09/28/2020
	m,d,y = day_str.split('/')
	
	return str(y)+str(m)+str(d)

def get_day_and_min(day_str,min_str):
	
	return int(get_day(day_str)+str(get_min(min_str)))
	
def get_min(time_str):
	"""Get Seconds from time."""
	h, m= time_str.split(':')
	#print(h,m)
	return int(h) * 60 + int(m)

def ts_to_str(timestamp):
	
	h= int(timestamp//60)
	m= int(timestamp%60)

	#chekc if they are 1 unit.
	
	if h//10 == 0:
		h = "0"+str(h)
	else:
		h = str(h)
		
	if m//10 == 0:
		m = "0"+str(m)
	else:
		m = str(m)
		
	return(h+":"+m)

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

def rate_change(lst):
	
	return lst.iloc[-1] - lst.iloc[0]

def range_(lst):
	
	return max(lst) - min(lst)

def process_one(s):
	
	#STEP 1 . ADD timestamp.
	datehour = []
	timestamp = []
	for i in range(len(s)):
		timestamp.append(get_min(s["time"][i]))
		datehour.append(s["day"][i]+" "+s["time"][i])

	s.insert(2,"timestamp", timestamp, True)     
	s.insert(2,"datehour", datehour, True) 
	
	
	# STEP 1.1 Interpolate value.?  WORRY ABOUT THIS PART LATER. 
	
	#1. Drop the first one before 9:30. 2. Drop the last one after 16:00.
	#Make up the missing values. 
	
	
	#STEP 2. Add percentage counter. 
	
	days = s.day.unique()

	#s.to_csv("test.csv")
	#print(s)
	for day in range(len(days)):
		#get the first value
		
		#print the first time 370. 
		#print(s.loc[s["datehour"]==(days[day] +" 09:30")]["open"])

		try:
			open_ = s.loc[s["datehour"]==(days[day] +" 09:30")]["open"].values[0]
	 

			s.loc[(s["day"]==days[day])&(s["timestamp"]>=570),"open_"] = open_
			#tomorrow's, before 9:30. 
			if day < len(days)-1:
				s.loc[(s["day"]==days[day+1])&(s["timestamp"]<570),"open_"] = open_
		except:
			print(days[day],"data corruption")
	
	percentage= []
	for i in range(len(s)):
		ratio = round((s["open"][i]-s["open_"][i])*100/s["open_"][i],4)
		percentage.append(ratio)
		
	
	s.insert(2,"change", percentage, True) 
	
	#STEP 3. DROP not used colomn
	drop =["open_","high","low","close","volume"]
	
	s= s.dropna()
	
	return s.drop(drop,axis=1)
def process(S,Q):
	
	S = process_one(S)
	Q = process_one(Q)
	
	j = pd.merge(S,Q,on='datehour')
	
	pricegap = []
	for i in range(len(j)):
		pricegap.append(j["change_x"][i]-j["change_y"][i])
		
	j.insert(1,"price_gap", pricegap, True) 
	
	return j.drop(["time_y","timestamp_y","day_y"],axis=1)


def new_window(symbol1=None,symbol2=None):
	root = tk.Tk() 
	root.title("GoodTrade PairTrader Researcher") 

	#s = spread_trader(root,None,True)
	r = researcher(root,symbol1,symbol2)
	root.geometry("1000x600")
	#root.minsize(600, 700)
	root.maxsize(1000, 600)
	root.mainloop()

def download(symbols,days,regular):

	postbody = "http://api.kibot.com/?action=login&user=sajali26@hotmail.com&password=guupu4upu"
	r= requests.post(postbody)
	for i in symbols:
		postbody = "http://api.kibot.com/?action=history&symbol="+str(i)+"&interval=1&period="+str(days)+"&regularsession="+str(regular)
		r= requests.post(postbody)
		if r.status_code==200:
			print("Donwload "+i+" successful. Writing to files")
			r = r.text
			with open("data/"+i+"_"+str(days)+".txt", "w") as text_file:
				text_file.write(r)

			print("Writing "+i+" completed.")

	return True


class researcher:
	def __init__(self,root,symbol1=None,symbol2=None):
		self.root = root

		self.config = ttk.LabelFrame(root,text="Parameters")
		self.config.place(x=10,rely=0.01,relheight=0.15,relwidth=0.95)

		self.charts_ = ttk.LabelFrame(root,text="Charts")
		self.charts_.place(x=10,rely=0.16,relheight=0.80,relwidth=0.95)

		self.tabControl = ttk.Notebook(self.charts_)
		self.tab1 = tk.Canvas(self.tabControl)
		self.tab2 = tk.Canvas(self.tabControl)
		self.tab3 = tk.Canvas(self.tabControl)
		self.tab4 = tk.Canvas(self.tabControl)

		self.tabControl.add(self.tab1, text ='Market hours') 
		self.tabControl.add(self.tab2, text ='9:30-11:00') 
		self.tabControl.add(self.tab3, text ='11:00-15:00') 
		self.tabControl.add(self.tab4, text ='15:00-16:00') 

		self.tabControl.pack(expand = 1, fill ="both") 
		self.charts=[self.tab1,self.tab2,self.tab3,self.tab4]

		self.l1=ttk.Label(self.config,text="Symbol1")
		self.l2=ttk.Label(self.config,text="Symbol2")
		self.l3=ttk.Label(self.config,text="Days")

		self.l1.grid(row = 1, column =1)
		self.l2.grid(row = 1, column =2)
		self.l3.grid(row = 1, column =3)


		self.s1 = tk.StringVar()
		self.s2 = tk.StringVar()
		self.d = tk.StringVar()
		if symbol1!=None:
			self.s1.set(symbol1)
		if symbol2!=None:
			self.s2.set(symbol2)

		self.symbol1 = ttk.Entry(self.config,textvariable=self.s1)
		self.symbol1.grid(row = 2, column =1)

		self.symbol2 = ttk.Entry(self.config,textvariable=self.s2)
		self.symbol2.grid(row = 2, column =2)


		self.days = ttk.Entry(self.config)
		self.days.grid(row = 2, column =3)

		self.button = ttk.Button(self.config,text="Analyze",command=self.get_chart)
		self.button.grid(row = 2, column =5)

		if symbol1!=None and symbol2!=None:
			self.d.set("7")

			self.get_chart()


	def get_chart(self):

		for i in self.charts:
			for widget in i.winfo_children():
				widget.destroy()
		symbol1 = self.symbol1.get()
		symbol2 = self.symbol2.get()
		days = self.days.get()

		try:
			days = int(days)
		except:
			print("days invalid.")

		self.graph(symbol1, symbol2, days)


	def graph(self,symbol1,symbol2,days):

		#download
		d= download([symbol1,symbol2], days, 1)

		if 1:
			plt.clf()
			p1 =pd.read_csv('data/'+symbol1+'_'+str(days)+'.txt',names=["day","time","open","high","low","close","volume"])
			p2= pd.read_csv('data/'+symbol2+'_'+str(days)+'.txt',names=["day","time","open","high","low","close","volume"])

			p = process(p1,p2)

			cond_s=[570,570,660,900]
			cond_e=[960,660,900,960]
			titles = ["Market hours","9:30-11:00","11:00-15:00","15:00-16:00"]

			outlier = dict(markerfacecolor='black', marker='o')
			min_form = DateFormatter("%H:%M")

			days = p.day_x.unique()

			for i in range(len(titles)):
				f= plt.figure(figsize=(9,4))  
				a1 = f.add_subplot(1,1,1) 
				for day in days[:]:
				#grab the time which bound between time. 
					t= pd.to_datetime(p.loc[(p["day_x"]==day)&(p["timestamp_x"]>=cond_s[i])&(p["timestamp_x"]<=cond_e[i])]["time_x"])
					gap = p.loc[(p["day_x"]==day)&(p["timestamp_x"]>=cond_s[i])&(p["timestamp_x"]<=cond_e[i])]["price_gap"]
					if len(gap)>1:
						a1.plot(t,SMA(gap.tolist(),15))
					a1.xaxis.set_major_formatter(min_form)
					a1.set_title(titles[i]+" Price Gap")


				plt.tight_layout()


				
				plotcanvas = FigureCanvasTkAgg(f, self.charts[i])
				plotcanvas.get_tk_widget().grid(column=1, row=1)

		else:
			print("failed")


new_window()


#Symbol1 Symbol2 Days 