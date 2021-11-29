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
import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt
import json
import requests

timestamp = []
for i in range(240,1201):
	timestamp.append(i)
	
def rel_vol(lst,n):

	#lets say n=7.
	rv = [1 for i in range(n)]

	for i in range(n,len(lst)):

		avg = mean(lst[i-n:i])

		current = round(lst[i]/avg,2)
		#print(lst[i],avg,current)
		rv.append(current)
	rv[1:] = rv[:-1]
	return rv

def mean(lst):
	return sum(lst)/len(lst)

def EMA(lst,n):

	ema = [lst[0]]

	#print(np.round(lst,2))
	for i in range(1,len(lst)):
		current = lst[i]
		new = (current - ema[i-1])*(2/(n+1)) + ema[i-1]
		ema.append(new)
	ema[1:] = ema[:-1]
	#print(np.round(ema,2))
	return ema
	
def SMA(lst,n):
	lst1= []
	lst1.append(lst[0])
	for i in range(1,len(lst)):
		if i < n:
			lst1.append(mean(lst[:i+1]))
		else:
			lst1.append(mean(lst[i-n+1:i+1]))
			
	return np.array(lst1)
def get_min(time_str):
	"""Get Seconds from time."""

	h, m= time_str.split(':')

	ts = int(h) * 60 + int(m)

	return ts

def score(price):
	score = []

	for i in range(len(price)):
		if i<30:
			score.append(0)
		else:
			#print(i)
			r5=round(max(price[i-5:i]) - min(price[i-5:i]),2)

			back = max(0,i-120)
			#print(back,i-5,price[back:i-5])
			r120= round(max(price[back:i-5])-min(price[back:i-5]),2)
			if r120!=0:
				score.append(round(r5/r120,2))
			else:
				score.append(0)
	return score
	

	expected_m = round(EMA(EM,7)[-2],2)


def init_historical(dic):

	dic["oh"]=0
	dic["ol"]=0
	dic['sc'] = 0
	dic['sc%'] = 0

	# dic["opening_high"] = 0
	# dic["opening_low"] = 0

	dic["oh_max"]= 0
	dic["oh_min"]=0
	dic["oh_mean"]=0
	dic["oh_std"]=0

	dic["ol_max"]=0
	dic["ol_min"]=0
	dic["ol_mean"]=0
	dic["ol_std"]=0

	dic["sc_max"]=0
	dic["sc_min"]=0
	dic["sc_mean"]=0
	dic["sc_std"]=0

	dic["opening_high_max"]=0
	dic["opening_high_min"]=0
	dic["opening_high_mean"]=0
	dic["opening_high_std"]=0

	dic["opening_low_max"]=0
	dic["opening_low_min"]=0
	dic["opening_low_mean"]=0
	dic["opening_low_std"]=0


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

def compute_today(dic):

	dic["oh"]= round(dic["high"]-dic["open"],2)
	dic["ol"]= round(dic["open"]-dic["low"],2)
	
	# if dic["lows"][4]>dic["open"]:
	# 	dic["opening_high"] = round(dic["highs"][4] -dic["open"],2)
	# else:
	# 	dic["opening_low"] = round(dic["open"]-dic["lows"][4],2)


	total_vol = dic["pvolume"]
	vols = []

	c_vols = [0 for i in range(570,961)]
	for i in range(570,961):
		if i in dic["ts"]:
			k = dic["ts"].index(i)
			c_vols[i-570] = dic["volumes"][k]

	# for i in range(len(dic["volumes"])):
	vols = []
	for j in range(5,396,5):
		total_vol+=sum(c_vols[j-5:j])
		vols.append(total_vol)


	dic["vol5"] = vols

	#print(dic["date"],len(vols),vols[:3],dic["volumes"][:5])


def clean_up_data(dic):

	for key,value in dic.items():
		dic[key]["vol5"] = []

def compute_historical(dates,dic):

	#print(dates[14:])


	#jump to 14.


	for i in range(10,len(dates)):
		#print("process",dates[i],i-14,i)
		data = dic[dates[i]]
		
		oh = []
		ol = []
		oph = []
		opl = []
		sc = [] 

		stamps = np.array([570+i*5 for i in range(79)])
		df = pd.DataFrame(columns = stamps)


		for j in range(i-10,i):
			try:
				df.loc[dates[j]] = dic[dates[j]]["vol5"]
			except Exception as e:
				print(e,dic[dates[j]]["vol5"])
				#print(dates[j],dic[dates[j]]["vol5"],len(dic[dates[j]]["vol5"]))
			if dic[dates[j]]["oh"] > dic[dates[j]]["ol"]:
				oh.append(dic[dates[j]]["oh"])
			else:
				ol.append(dic[dates[j]]["ol"])

			# if dic[dates[j]]["opening_high"] ==0:
			# 	opl.append(dic[dates[j]]["opening_low"])
			# else:
			# 	oph.append(dic[dates[j]]["opening_high"])

			sc.append(abs(dic[dates[j]]["sc"]))
		#print(len(oh),len(ol),len(oph),len(opl),len(sc),dic[dates[j]]["opening_low"],dic[dates[j]]["opening_high"])
		#print(df)
		
		rel_vol = df.mean().tolist()


		a = np.arange(79)
		p = np.poly1d(np.polyfit(a*5, rel_vol, 10))

		new = [i for i in range(391)]
		rel_vol = [int(a) for a in p(new)]  
		#print(dic[dates[j]]["vol5"])
		dic[dates[i]]["rrvol"]= rel_vol
		subject = oh

		try:
			dic[dates[i]]["oh_max"]= round(max(subject),3)
			dic[dates[i]]["oh_min"]= round(min(subject),3)
			dic[dates[i]]["oh_mean"]= round(np.mean(subject),3)
			dic[dates[i]]["oh_std"]= round(np.std(subject),3)
		except:
			subject = ol
			dic[dates[i]]["oh_max"]= round(max(subject)/2,3)
			dic[dates[i]]["oh_min"]=round(min(subject),3)
			dic[dates[i]]["oh_mean"]=round(np.mean(subject)/2,3)
			dic[dates[i]]["oh_std"]=round(np.std(subject),3)


		subject = ol

		try:
			dic[dates[i]]["ol_max"]= round(max(subject),3)
			dic[dates[i]]["ol_min"]=round(min(subject),3)
			dic[dates[i]]["ol_mean"]=round(np.mean(subject),3)
			dic[dates[i]]["ol_std"]=round(np.std(subject),3)
		except:
			subject = oh
			dic[dates[i]]["ol_max"]= round(max(subject)/2,3)
			dic[dates[i]]["ol_min"]=round(min(subject),3)
			dic[dates[i]]["ol_mean"]=round(np.mean(subject)/2,3)
			dic[dates[i]]["ol_std"]=round(np.std(subject),3)





		subject = sc
		dic[dates[i]]["sc_max"]= round(max(subject),3)
		dic[dates[i]]["sc_min"]= round(min(subject),3)
		dic[dates[i]]["sc_mean"]=round(np.mean(subject),3)
		dic[dates[i]]["sc_std"]=round(np.std(subject),3)

		# subject = oph
		# dic[dates[i]]["opening_high_max"]=round( max(subject),3)
		# dic[dates[i]]["opening_high_min"]=round(min(subject),3)
		# dic[dates[i]]["opening_high_mean"]=round(np.mean(subject),3)
		# dic[dates[i]]["opening_high_std"]=round(np.std(subject),3)

		# subject = opl
		# dic[dates[i]]["opening_low_max"]= round(max(subject),3)
		# dic[dates[i]]["opening_low_min"]= round(min(subject),3)
		# dic[dates[i]]["opening_low_mean"]= round(np.mean(subject),3)
		# dic[dates[i]]["opening_low_std"]= round(np.std(subject),3)

		#dic[dates[i]]["vol5"] = []
		#dic["vol5"] = []
		#print(dates[j],dic[dates[i]]["oh_mean"],dic[dates[i]]["sc_mean"],dic[dates[i]]["ol_mean"],sc)
	# keys=["oh_max","oh_min","oh_mean","oh_std","ol_max","ol_min","ol_mean","ol_std","sc_max","sc_min","sc_mean","sc_std",]
	# for i in range(14,len(dates)):
	# 	print(dates[i])
	# 	for j in keys:
	# 		print(j,dic[dates[i]][j])
	
def combine(filename):

	#dic = {}
	
	symbol = filename#.split("/")[1][:-4]

	dic = {}

	all_dates = []
	magnitude = []
	volume = []

	f = open(filename, "r")
	lastdate=0

	for x in f:
		lst=x.split(",")
		date = lst[0]
		if date not in dic:
			dic[date] = {}
			dic[date]['symbol'] = symbol
			dic[date]['date'] = date
			if lastdate==0:
				dic[date]['lastdate'] = date
			else:
				#wrap up yesterday's.  dic[lastdate]['high']= max(dic[lastdate]["highs"])
				dic[date]['lastdate'] = lastdate
				try:
					dic[lastdate]['high']= max(dic[lastdate]["highs"])
					dic[lastdate]['low']= min(dic[lastdate]["lows"])
					dic[lastdate]['volume'] = sum(dic[lastdate]["volumes"]) + dic[lastdate]['pvolume']
					dic[lastdate]['magnitude'] = round(max(dic[lastdate]['high']-dic[lastdate]['open'],dic[lastdate]['open']-dic[lastdate]['low']),2)
				except:
					print("problem with",symbol)
				compute_today(dic[lastdate])

				volume.append(dic[lastdate]['volume'])
				magnitude.append(dic[lastdate]['magnitude'])

			
			dic[date]['open'] = 0
			dic[date]['close'] = 0
			
			dic[date]['pvolume'] = 0
			dic[date]['volume'] = 0
			dic[date]['magnitude'] = 0
			dic[date]['expected_magnitude'] = 0
			dic[date]['yrelv'] = 0

			dic[date]['ph'] = 0
			dic[date]['pl'] = 0

			init_historical(dic[date])

			dic[date]["highs"]=[]
			dic[date]["lows"]=[]
			dic[date]["opens"]=[]
			dic[date]["closes"]=[]
			dic[date]["volumes"]=[]
			dic[date]["ts"]=[]


			all_dates.append(date)

		try:
			ts = get_min(lst[1])

		except Exception as e:
			print(e,lst[1],filename,)
			break

		if ts>=570 and ts<=960:
			open_ =  float(lst[2])
			high = float(lst[3])
			low = float(lst[4])
			close_ =  float(lst[5])
			vol = int(lst[6])

			dic[date]["opens"].append(open_)
			dic[date]["closes"].append(close_)
			dic[date]["highs"].append(high)
			dic[date]["lows"].append(low)

			# dic[date]["highs"].append(max(dic[date]["highs"]))
			# dic[date]["lows"].append(min(dic[date]["lows"]))

			dic[date]["ts"].append(ts)
			# dic[date]["time"].append(lst[1])
			dic[date]["volumes"].append(vol)
			if ts>=570 and dic[date]['open']==0:
				dic[date]['open'] = open_
				if dic[date]['lastdate'] != date:
					prev_close = dic[dic[date]['lastdate']]['close']

					#dic[date]["volumes"][-1]+=dic[date]["pvolume"]
					if prev_close!=0:
						dic[date]['sc'] = round(open_  - prev_close,2)
						dic[date]['sc%'] = round((open_  - prev_close)*100/prev_close,2)

			if ts>=959 and ts<= 960:
				dic[date]['close'] = close_

		elif ts<570:
			vol = int(lst[6])
			high = float(lst[3])
			low = float(lst[4])

			if high>dic[date]['ph']:
				dic[date]['ph'] = high

			if low<dic[date]['pl'] or dic[date]['pl']==0:
				dic[date]['pl'] = low

			dic[date]["pvolume"]+=vol

		lastdate = date

	#calculate the expected magnitude. 7 period.

	# LAST DATE 
	dic[lastdate]['high']= max(dic[lastdate]["highs"])
	dic[lastdate]['low']= min(dic[lastdate]["lows"])
	dic[lastdate]['volume'] = sum(dic[lastdate]["volumes"]) + dic[lastdate]['pvolume']
	dic[lastdate]['magnitude'] =  round(max(dic[lastdate]['high']-dic[lastdate]['open'],dic[lastdate]['open']-dic[lastdate]['low']),2)
	compute_today(dic[lastdate])
	volume.append(dic[lastdate]['volume'])
	magnitude.append(dic[lastdate]['magnitude'])


	expected_m = EMA(magnitude,7)
	rel_v = rel_vol(volume,7)

	#Historical goes here too. 

	if len(all_dates)!=len(expected_m) or len(all_dates)!=len(rel_v):
		print("length match error")
		print(len(all_dates))
		print(len(expected_m))
		print(len(rel_v))
		print(len(magnitude))
		print(len(volume))
	else:
		for i in range(len(all_dates)):
			dic[all_dates[i]]['expected_magnitude'] = expected_m[i]
			dic[all_dates[i]]['yrelv'] = rel_v[i]


	for key,d in dic.items():
		if d['open'] == 0 or d['high']==0 or d['low']==0:
			print(symbol,key,"error on open value.")

	compute_historical(all_dates,dic)

	#print(dic.keys())
	f.close()

	clean_up_data(dic)

	return dic
	#create_time_file(dic,symbol,out_put_folder)

def new_window(symbol1=None,symbol2=None):
	root = tk.Tk() 
	root.title("GoodTrade Symbol Researcher") 

	#s = spread_trader(root,None,True)
	r = researcher(root,symbol1)
	root.geometry("1600x850")
	root.minsize(1400, 700)
	root.maxsize(1920, 1080)
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

### LOAD A STOCK and process it ###
def l(v):
	z=[]
	for i in v:
		z.append(chr(i))

	return (''.join(map(str, z)))

def request(req,symbol):
	try:
		r= requests.post(req)
		r= r.text

		if r[:3] == "404" or r[:3] =="405":
			print(symbol,"Not found")
			return ""
		else:
			return r

	except Exception as e:
		print(e)
		return ""

def l(v):
	z=[]
	for i in v:
		z.append(chr(i))

	return (''.join(map(str, z)))

def get_min(time_str):
	"""Get Seconds from time."""
	h, m= time_str.split(':')
	#print(h,m)
	return int(h) * 60 + int(m)

def min_to_ts(i):
	
	return str(i//60)+":"+str(i%60)
def IQR(x,t):

	if len(x)> 5:
		q75, q25 = np.percentile(x, [100-t ,t])
		iqr = (q75 - q25)*1.5
		### only take the good one.
		y = []
		for i in x:
			if (i <= q75 + iqr) and (i >= q25 - iqr):
				y.append(i)

		x = y[:]
		#print(q75,q25,iqr)

	return x

def IQR_line(x,t):

	if len(x)> 5:
		q75, q25 = np.percentile(x, [100-t ,t])
		return q75,q25

def fetch_data(symbol,day):

	req = symbol.split(".")[0]
	i = symbol
	v= [38, 117, 115, 101, 114, 61, 115, 97, 106, 97, 108, 105, 50, 54, 64, 104, 111, 116, 109, 97, 105, 108, 46, 99, 111, 109, 38, 112, 97, 115, 115, 119, 111, 114, 100, 61, 103, 117, 117, 112, 117, 52, 117, 112, 117]

	postbody = "http://api.kibot.com/?action=history&symbol="+req+"&interval=60&period="+str(day)+"&regularsession=1" +l(v)

	r= request(postbody, symbol)

	test= {}
	if r!="":

		for line in r.splitlines():
			lst=line.split(",")

			date = lst[0]
			time = get_min(lst[1])
			open_ =  float(lst[2])
			high = float(lst[3])
			low = float(lst[4])
			close_ =  float(lst[5])
			r = round(high-low,3)
			#print(time)
			if date not in test:
				test[date] = {}
				test[date]["ph"]=high
				test[date]["pl"]=low
				test[date]["open"]=[]
				test[date]["close"]=[]
				test[date]["high"]=[]
				test[date]["low"]=[]
				test[date]["ts"]=[]

			if time>=570 and time<=960:

				test[date]["open"].append(open_)
				test[date]["close"].append(close_)
				
				test[date]["high"].append(high)
				test[date]["low"].append(low)
				test[date]["ts"].append(time)
				


	return test

def fetch_data_day(symbol,day):

	req = symbol.split(".")[0]
	i = symbol
	v= [38, 117, 115, 101, 114, 61, 115, 97, 106, 97, 108, 105, 50, 54, 64, 104, 111, 116, 109, 97, 105, 108, 46, 99, 111, 109, 38, 112, 97, 115, 115, 119, 111, 114, 100, 61, 103, 117, 117, 112, 117, 52, 117, 112, 117]

	postbody = "http://api.kibot.com/?action=history&symbol="+req+"&interval=1&period="+str(day)+"&regularsession=1" +l(v)

	r= request(postbody, symbol)
	
	t=r
	with open("test.txt", "w",newline='') as text_file:
		text_file.write(t)
	#save to temp.txt
	
	return combine("test.txt")

def draw_oh(d):
	
	extreme = []

	val = 0
	for i in range(570,960):
		
		if i in d["ts"]:
			i =d["ts"].index(i)
			cur = d["closes"][i]-d["open"]
			if cur >0: #bigger
				val = cur/d["oh_mean"] 
			else: #less
				val = cur/d["ol_mean"]
		extreme.append(val)  
			
	
	return np.array(extreme)

class researcher:
	def __init__(self,root,symbol1=None):
		self.root = root

		self.config = ttk.LabelFrame(root,text="Parameters")
		self.config.place(x=10,rely=0.01,relheight=0.15,relwidth=0.95)

		self.charts_ = ttk.LabelFrame(root,text="Charts")
		self.charts_.place(x=10,rely=0.16,relheight=0.80,relwidth=0.95)

		self.tabControl = ttk.Notebook(self.charts_)
		self.tab1 = tk.Canvas(self.tabControl)
		self.tab2 = tk.Canvas(self.tabControl)

		self.current = None
		self.tabControl.add(self.tab1, text ='Since Close') 
		self.tabControl.add(self.tab2, text ='OHOL') 

		self.tabControl.pack(expand = 1, fill ="both") 
		self.charts=[self.tab1,self.tab2]

		ttk.Label(self.config,text="Symbol1").grid(row = 1, column =1)
		ttk.Label(self.config,text="Days").grid(row = 1, column =2)
		ttk.Label(self.config,text="SC%/ filter").grid(row = 1, column =3)
		ttk.Label(self.config,text="OHOL%/ filter").grid(row = 1, column =4)
		ttk.Label(self.config,text="time after(optional)").grid(row = 1, column =5)
		ttk.Label(self.config,text="time before(optional)").grid(row = 1, column =6)


		#ttk.Label(self.config,text="Input positive value for > and inpu").grid(row = 4, column =4)

		self.datastart = tk.StringVar(value="Data Start:")
		self.dataend = tk.StringVar(value="Data End:")
		self.total_periods = tk.StringVar(value="Total Trading Days:")

		ttk.Label(self.config,textvariable=self.datastart).grid(row = 3, column =1)
		ttk.Label(self.config,textvariable=self.dataend).grid(row = 4, column =1)
		ttk.Label(self.config,textvariable=self.total_periods).grid(row = 5, column =1)

		self.symbol = tk.StringVar(value="SPY")

		self.d = tk.StringVar()
		self.sc = tk.DoubleVar(value=-1)
		self.oh = tk.DoubleVar(value=0)
		self.days = tk.IntVar(value=30)

		self.before = tk.IntVar(value=16)
		self.after =tk.IntVar(value=9)

		ttk.Entry(self.config,textvariable=self.symbol).grid(row = 2, column =1)
		ttk.Entry(self.config,textvariable=self.days).grid(row = 2, column =2)
		ttk.Entry(self.config,textvariable=self.sc).grid(row = 2, column =3)
		ttk.Entry(self.config,textvariable=self.oh).grid(row = 2, column =4)
		ttk.Entry(self.config,textvariable=self.after).grid(row = 2, column =5)
		ttk.Entry(self.config,textvariable=self.before).grid(row = 2, column =6)

		self.button=ttk.Button(self.config,text="Analyze",command=self.get_chart)
		self.button.grid(row = 2, column =7)

	def get_chart(self):

		for i in self.charts:
			for widget in i.winfo_children():
				widget.destroy()
		symbol1 = self.symbol.get()
		days = self.days.get()+20

		try:
			days = int(days)
		except:
			print("days invalid.")

		#self.graph(symbol1, days)
		if self.current!=self.symbol.get()+str(self.days.get()):
			self.data=fetch_data_day(symbol1,days)

			self.datastart.set("Data Start: "+str(list(self.data.keys())[14:][0]))
			self.dataend.set("Data End: "+str(list(self.data.keys())[14:][-1]))
			self.total_periods.set("Total Trading Days: "+str(len(list(self.data.keys())[14:])))
			self.current=self.symbol.get()+str(self.days.get())
			self.graph()
		else:
			self.graph()


	def graph(self):

		#download
		#d= download([symbol1,symbol2], days, 1)
		
		ts = pd.to_datetime([ts_to_str(i) for i in range(570,960)])
		min_form = DateFormatter("%H:%M")
		#print(self.data)
		if 1:
			plt.clf()

			titles = ["SC/% filter","Extremity"]


			for i in range(len(titles)):
				f= plt.figure(figsize=(14,6))  
				a1 = f.add_subplot(1,1,1) 

				if i==0:

					sc =  self.sc.get()
					lst = []
					for key in list(self.data.keys())[14:]:
		
						if sc>0:
							if self.data[key]["sc%"]>=sc:
								extreme = draw_oh(self.data[key])
								a1.plot(ts,extreme)
								lst.append(extreme)
						else:
							if self.data[key]["sc%"]<=sc:
								extreme = draw_oh(self.data[key])
								a1.plot(ts,extreme)
								lst.append(extreme)

					try:     
						a1.plot(ts,np.mean(lst,axis=0),linewidth=10,alpha=0.25,label="mean move")
					except:
						pass
					a1.set_ylabel("Relative Extremity")
					a1.set_xlabel("time")
					a1.xaxis.set_major_formatter(min_form)
					a1.legend()


				elif i==1:


					oh =  self.oh.get()
					lst = []

					before = self.before.get()
					after = self.after.get()

					start = max(0,(after-9)*30)
					end = min(360,360-(16-before)*60)

					for key in list(self.data.keys())[14:]:
		
						extreme = draw_oh(self.data[key])
						if oh>0:
							if np.any(extreme>=oh):
								idx = np.where(extreme>=oh)[0][0]

								if idx>=start and idx<=end:
									a1.plot(ts,extreme)
									a1.plot(ts[idx],extreme[idx],"r^",markersize=10)
									print(idx)
									lst.append(extreme)
						else:
							if np.any(extreme<=oh):
								idx = np.where(extreme<=oh)[0][0]

								if idx>=start and idx<=end:
									a1.plot(ts,extreme)
									a1.plot(ts[idx],extreme[idx],"rv",markersize=10)
									lst.append(extreme)

					try:     
						a1.plot(ts,np.mean(lst,axis=0),linewidth=10,alpha=0.25,label="mean move")
					except:
						pass
					a1.set_ylabel("Relative Extremity")
					a1.set_xlabel("time")
					a1.xaxis.set_major_formatter(min_form)
					a1.legend()











				plt.tight_layout()

				
				plotcanvas = FigureCanvasTkAgg(f, self.charts[i])
				plotcanvas.get_tk_widget().grid(column=1, row=1)

		else:
			print("failed")

new_window()


#Symbol1 Symbol2 Days 