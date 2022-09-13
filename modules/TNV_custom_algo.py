import tkinter as tk                     
from tkinter import ttk 
import threading
import pandas as pd
import time
from datetime import datetime

import requests
#from pannel import *
#from modules.pannel import *

from tkinter import *
import json


# from modules.TNV_OR import *
# from modules.TNV_Trend import *
class fake_NT():

	def __init__(self):

		self.nasdaq_trader_symbols_ranking=[]

def ts_to_min(ts):
	ts = int(ts)
	m = ts//60
	s = ts%60

	return str(m)+":"+str(s)

def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data


class Custom_Algo():

	def __init__(self,root,TNV_scanner):

		self.root = root 
		# self.labels_width = [9,9,9]
		# self.labels = ["Time","Algo","Symbol"]
		#self.total_len = len(self.labels)
		self.tnv_scanner = TNV_scanner
		self.entries = []

		self.algo_risk = tk.DoubleVar(value=5)
		self.algo_activate = tk.BooleanVar(value=1)
		# self.l=0

		# for i in range(len(self.labels)): #Rows
		# 	self.b = tk.Button(self.root, text=self.labels[i],width=self.labels_width[i])#,command=self.rank
		# 	self.b.configure(activebackground="#f9f9f9")
		# 	self.b.configure(activeforeground="black")
		# 	self.b.configure(background="#d9d9d9")
		# 	self.b.configure(disabledforeground="#a3a3a3")
		# 	self.b.configure(relief="ridge")
		# 	self.b.configure(foreground="#000000")
		# 	self.b.configure(highlightbackground="#d9d9d9")
		# 	self.b.configure(highlightcolor="black")
		# 	self.b.grid(row=self.l, column=i)
		# self.l+=1

		current_y = 0
		self.algo_frame = ttk.LabelFrame(self.root,text="Algo setup")
		self.algo_frame.place(x=0.01, rely=0, relheight=0.1, relwidth=0.99)


		self.market_timing_algos = ttk.LabelFrame(self.root,text="Market Timing algos")
		self.market_timing_algos.place(x=0.01, rely=0.1, relheight=0.1, relwidth=0.99)


		# self.market_POE_algos = ttk.LabelFrame(self.root,text="Market POE algos")
		# self.market_POE_algos.place(x=0.01, rely=0.205, relheight=0.1, relwidth=0.99)


		# self.basket_hedging_algos = ttk.LabelFrame(self.root,text="Basket Hedging algos")
		# self.basket_hedging_algos.place(x=0.01, rely=0.305, relheight=0.1, relwidth=0.99)

		self.corey_algos = ttk.LabelFrame(self.root,text="Corey algos")
		self.corey_algos.place(x=0.01, rely=0.225, relheight=0.33, relwidth=0.99)

		self.bax_algos = ttk.LabelFrame(self.root,text="Baxter algos")
		self.bax_algos.place(x=0.01, rely=0.55, relheight=0.2, relwidth=0.99)

		self.tick_opening = tk.BooleanVar(value=0)
		self.tick_intraday_v1 = tk.BooleanVar(value=0)
		self.tick_intraday_v2 = tk.BooleanVar(value=0)


		self.market_long = tk.BooleanVar(value=0)
		self.market_short = tk.BooleanVar(value=0)


		self.corey_PUFTB = tk.BooleanVar(value=0)
		self.corey_PUFTB_multiplier = tk.IntVar(value=1)
		self.corey_PUFTB_risk = tk.IntVar(value=100)

		self.corey_MNQ = tk.BooleanVar(value=0)
		self.corey_MNQ_multiplier = tk.IntVar(value=1)
		self.corey_MNQ_risk = tk.IntVar(value=100)

		self.corey_QTSTT = tk.BooleanVar(value=0)
		self.corey_QTSTT_multiplier = tk.IntVar(value=1)
		self.corey_QTSTT_risk = tk.IntVar(value=100)

		self.corey_STSTT = tk.BooleanVar(value=0)
		self.corey_STSTT_multiplier = tk.IntVar(value=1)
		self.corey_STSTT_risk = tk.IntVar(value=100)

		self.corey_IWTSTT = tk.BooleanVar(value=0)
		self.corey_IWTSTT_multiplier = tk.IntVar(value=1)
		self.corey_IWTSTT_risk = tk.IntVar(value=100)

		self.corey_OTS = tk.BooleanVar(value=0)
		self.corey_OTS_multiplier = tk.IntVar(value=1)
		self.corey_OTS_risk = tk.IntVar(value=100)

		self.corey_STS = tk.BooleanVar(value=0)
		self.corey_STS_multiplier = tk.IntVar(value=1)
		self.corey_STS_risk = tk.IntVar(value=100)


		self.corey_YBO = tk.BooleanVar(value=0)
		self.corey_YBO_multiplier = tk.IntVar(value=1)
		self.corey_YBO_risk = tk.IntVar(value=100)

		self.corey_QCK = tk.BooleanVar(value=0)
		self.corey_QCK_multiplier = tk.IntVar(value=1)
		self.corey_QCK_risk = tk.IntVar(value=100)

		self.corey_TEST = tk.BooleanVar(value=0)
		self.corey_TEST_multiplier = tk.IntVar(value=1)
		self.corey_TEST_risk = tk.IntVar(value=100)

		self.bax1 = tk.BooleanVar(value=0)
		self.bax2 = tk.BooleanVar(value=0)
		self.bax3 = tk.BooleanVar(value=0)
		self.bax4 = tk.BooleanVar(value=0)
		self.bax5 = tk.BooleanVar(value=0)

		self.bax1_risk = tk.IntVar(value=5)
		self.bax2_risk = tk.IntVar(value=5)
		self.bax3_risk = tk.IntVar(value=5)
		self.bax4_risk = tk.IntVar(value=5)
		self.bax5_risk = tk.IntVar(value=5)


		self.market_timing_algos_pannel()
		self.algo_pannel()


	def market_timing_algos_pannel(self):

		row = 0
		col = 0

		self.market_timing_per_risk = tk.IntVar(value=1)
		self.market_timing_total_risk =tk.IntVar(value=1)

		ttk.Label(self.market_timing_algos, text="Risk Per Trade:").grid(sticky="w",column=col+0,row=row)
		ttk.Entry(self.market_timing_algos, textvariable=self.market_timing_per_risk).grid(sticky="w",column=col+1,row=row)

		row +=1

		ttk.Label(self.market_timing_algos, text="Stategy Total Risk:").grid(sticky="w",column=col+0,row=row)
		ttk.Entry(self.market_timing_algos, textvariable=self.market_timing_total_risk).grid(sticky="w",column=col+1,row=row)

		col +=2
		row = 0
		ttk.Label(self.market_timing_algos, text="Market Long Timing:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.market_timing_algos, variable=self.market_long).grid(sticky="w",column=col+1,row=row)

		col +=2

		ttk.Label(self.market_timing_algos, text="Market Short Timing:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.market_timing_algos, variable=self.market_short).grid(sticky="w",column=col+1,row=row)

		row+=1
		col -=2

		ttk.Label(self.market_timing_algos, text="TICK Long:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.market_timing_algos, variable=self.tick_intraday_v1).grid(sticky="w",column=col+1,row=row)

		col +=2

		ttk.Label(self.market_timing_algos, text="TICK Short:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.market_timing_algos, variable=self.tick_intraday_v2).grid(sticky="w",column=col+1,row=row)



	def algo_pannel(self):

		row = 1
		col = 1
		ttk.Label(self.algo_frame, text="Algo:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algo_frame, variable=self.algo_activate).grid(sticky="w",column=col+1,row=row)



		row +=1

		ttk.Label(self.corey_algos, text="Corey PUFTB:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_PUFTB).grid(sticky="w",column=col+1,row=row)

		ttk.Label(self.corey_algos, text="Share multiplier:").grid(sticky="w",column=col+4,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_PUFTB_multiplier).grid(sticky="w",column=col+5,row=row)

		ttk.Label(self.corey_algos, text="Strategy Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_PUFTB_risk).grid(sticky="w",column=col+3,row=row)

		row +=1

		ttk.Label(self.corey_algos, text="Corey MNQ :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_MNQ).grid(sticky="w",column=col+1,row=row)

		ttk.Label(self.corey_algos, text="Share multiplier:").grid(sticky="w",column=col+4,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_MNQ_multiplier).grid(sticky="w",column=col+5,row=row)

		ttk.Label(self.corey_algos, text="Strategy Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_MNQ_risk).grid(sticky="w",column=col+3,row=row)


		row +=1

		ttk.Label(self.corey_algos, text="Corey QTSTT :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_QTSTT).grid(sticky="w",column=col+1,row=row)

		ttk.Label(self.corey_algos, text="Share multiplier:").grid(sticky="w",column=col+4,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_QTSTT_multiplier).grid(sticky="w",column=col+5,row=row)

		ttk.Label(self.corey_algos, text="Strategy Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_QTSTT_risk).grid(sticky="w",column=col+3,row=row)


		row +=1

		ttk.Label(self.corey_algos, text="Corey STSTT :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_STSTT).grid(sticky="w",column=col+1,row=row)

		ttk.Label(self.corey_algos, text="Share multiplier:").grid(sticky="w",column=col+4,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_STSTT_multiplier).grid(sticky="w",column=col+5,row=row)

		ttk.Label(self.corey_algos, text="Strategy Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_STSTT_risk).grid(sticky="w",column=col+3,row=row)

		row +=1

		ttk.Label(self.corey_algos, text="Corey IWTSTT :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_IWTSTT).grid(sticky="w",column=col+1,row=row)

		ttk.Label(self.corey_algos, text="Share multiplier:").grid(sticky="w",column=col+4,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_IWTSTT_multiplier).grid(sticky="w",column=col+5,row=row)

		ttk.Label(self.corey_algos, text="Strategy Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_IWTSTT_risk).grid(sticky="w",column=col+3,row=row)


		row +=1

		ttk.Label(self.corey_algos, text="Corey OTS :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_OTS).grid(sticky="w",column=col+1,row=row)

		ttk.Label(self.corey_algos, text="Share multiplier:").grid(sticky="w",column=col+4,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_OTS_multiplier).grid(sticky="w",column=col+5,row=row)

		ttk.Label(self.corey_algos, text="Strategy Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_OTS_risk).grid(sticky="w",column=col+3,row=row)

		row +=1

		ttk.Label(self.corey_algos, text="Corey STS :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_STS).grid(sticky="w",column=col+1,row=row)

		ttk.Label(self.corey_algos, text="Share multiplier:").grid(sticky="w",column=col+4,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_STS_multiplier).grid(sticky="w",column=col+5,row=row)

		ttk.Label(self.corey_algos, text="Strategy Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_STS_risk).grid(sticky="w",column=col+3,row=row)


		row +=1

		ttk.Label(self.corey_algos, text="Corey YBO :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_YBO).grid(sticky="w",column=col+1,row=row)

		ttk.Label(self.corey_algos, text="Share multiplier:").grid(sticky="w",column=col+4,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_YBO_multiplier).grid(sticky="w",column=col+5,row=row)

		ttk.Label(self.corey_algos, text="Strategy Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_YBO_risk).grid(sticky="w",column=col+3,row=row)


		row +=1

		ttk.Label(self.corey_algos, text="Corey QCK :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_QCK).grid(sticky="w",column=col+1,row=row)

		ttk.Label(self.corey_algos, text="Share multiplier:").grid(sticky="w",column=col+4,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_QCK_multiplier).grid(sticky="w",column=col+5,row=row)

		ttk.Label(self.corey_algos, text="Strategy Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_QCK_risk).grid(sticky="w",column=col+3,row=row)


		row +=1

		ttk.Label(self.corey_algos, text="Corey TEST :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_TEST).grid(sticky="w",column=col+1,row=row)

		ttk.Label(self.corey_algos, text="Share multiplier:").grid(sticky="w",column=col+4,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_TEST_multiplier).grid(sticky="w",column=col+5,row=row)

		ttk.Label(self.corey_algos, text="Strategy Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_TEST_risk).grid(sticky="w",column=col+3,row=row)

		row +=1

		ttk.Button(self.corey_algos, text="Save Config",command=self.save_corey).grid(sticky="w",column=col,row=row)
		ttk.Button(self.corey_algos, text="Load Config",command=self.load_corey).grid(sticky="w",column=col+2,row=row)

		#row +=1

		ttk.Label(self.bax_algos, text="BAX1:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.bax_algos, variable=self.bax1).grid(sticky="w",column=col+1,row=row)

		ttk.Label(self.bax_algos, text="Strategy Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.bax_algos, textvariable=self.bax1_risk).grid(sticky="w",column=col+3,row=row)


		row +=1

		ttk.Label(self.bax_algos, text="BAX2:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.bax_algos, variable=self.bax2).grid(sticky="w",column=col+1,row=row)

		ttk.Label(self.bax_algos, text="Strategy Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.bax_algos, textvariable=self.bax2_risk).grid(sticky="w",column=col+3,row=row)



		row +=1

		ttk.Label(self.bax_algos, text="BAX3:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.bax_algos, variable=self.bax3).grid(sticky="w",column=col+1,row=row)
		ttk.Label(self.bax_algos, text="Strategy Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.bax_algos, textvariable=self.bax3_risk).grid(sticky="w",column=col+3,row=row)


		row +=1

		ttk.Label(self.bax_algos, text="BAX4:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.bax_algos, variable=self.bax4).grid(sticky="w",column=col+1,row=row)
		ttk.Label(self.bax_algos, text="Strategy Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.bax_algos, textvariable=self.bax4_risk).grid(sticky="w",column=col+3,row=row)


		row +=1

		ttk.Label(self.bax_algos, text="BAX5:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.bax_algos, variable=self.bax5).grid(sticky="w",column=col+1,row=row)		# for k in range(0,30):
		ttk.Label(self.bax_algos, text="Strategy Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.bax_algos, textvariable=self.bax5_risk).grid(sticky="w",column=col+3,row=row)


		# 	self.entries.append([])

		# 	for i in range(len(self.labels)): #Rows
				
		# 		if i == 9:
		# 			self.b = tk.Button(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
		# 		elif i ==9:
		# 			self.b = tk.Button(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
		# 		else:
		# 			self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
		# 		self.b.grid(row=self.l, column=i)
		# 		self.entries[k].append(self.b)
		# 		# if i == 9:
		# 		# 	self.b.grid_remove()
		# 	self.l+=1

	def save_corey(self):

		###

		d = {}

		d["corey_PUFTB_multiplier"]=self.corey_PUFTB_multiplier.get()
		d["corey_PUFTB_risk"]=self.corey_PUFTB_risk.get()

		d["corey_MNQ_multiplier"]=self.corey_MNQ_multiplier.get()
		d["corey_MNQ_risk"]=self.corey_MNQ_risk.get()

		d["corey_QTSTT_multiplier"]=self.corey_QTSTT_multiplier.get()
		d["corey_QTSTT_risk"]=self.corey_QTSTT_risk.get()

		d["corey_STSTT_multiplier"]=self.corey_STSTT_multiplier.get()
		d["corey_STSTT_risk"]=self.corey_STSTT_risk.get()

		d["corey_IWTSTT_multiplier"]=self.corey_IWTSTT_multiplier.get()
		d["corey_IWTSTT_risk"]=self.corey_IWTSTT_risk.get()

		d["corey_OTS_multiplier"]=self.corey_OTS_multiplier.get()
		d["corey_OTS_risk"]=self.corey_OTS_risk.get()

		d["corey_STS_multiplier"]=self.corey_STS_multiplier.get()
		d["corey_STS_risk"]=self.corey_STS_risk.get()

		d["corey_YBO_multiplier"]=self.corey_YBO_multiplier.get()
		d["corey_YBO_risk"]=self.corey_YBO_risk.get()

		d["corey_QCK_multiplier"]=self.corey_QCK_multiplier.get()
		d["corey_QCK_risk"]=self.corey_QCK_risk.get()

		d["corey_TEST_multiplier"]=self.corey_TEST_multiplier.get()
		d["corey_TEST_risk"]=self.corey_TEST_risk.get()

		with open('corey_setting.json', 'w') as fp:
			json.dump(d, fp)

	def load_corey(self):

		with open('corey_setting.json', 'r') as myfile:
		    data=myfile.read()

		# parse file
		d = json.loads(data)

		self.corey_PUFTB_multiplier.set(d["corey_PUFTB_multiplier"])
		self.corey_PUFTB_risk.set(d["corey_PUFTB_risk"])

		self.corey_MNQ_multiplier.set(d["corey_MNQ_multiplier"])
		self.corey_MNQ_risk.set(d["corey_MNQ_risk"])

		self.corey_QTSTT_multiplier.set(d["corey_QTSTT_multiplier"])
		self.corey_QTSTT_risk.set(d["corey_QTSTT_risk"])

		self.corey_STSTT_multiplier.set(d["corey_STSTT_multiplier"])
		self.corey_STSTT_risk.set(d["corey_STSTT_risk"])

		self.corey_IWTSTT_multiplier.set(d["corey_IWTSTT_multiplier"])
		self.corey_IWTSTT_risk.set(d["corey_IWTSTT_risk"])

		self.corey_OTS_multiplier.set(d["corey_OTS_multiplier"])
		self.corey_OTS_risk.set(d["corey_OTS_risk"])

		self.corey_STS_multiplier.set(d["corey_STS_multiplier"])
		self.corey_STS_risk.set(d["corey_STS_risk"])

		self.corey_YBO_multiplier.set(d["corey_YBO_multiplier"])
		self.corey_YBO_risk.set(d["corey_YBO_risk"])

		self.corey_QCK_multiplier.set(d["corey_QCK_multiplier"])
		self.corey_QCK_risk.set(d["corey_QCK_risk"])

		self.corey_TEST_multiplier.set(d["corey_TEST_multiplier"])
		self.corey_TEST_risk.set(d["corey_TEST_risk"])


	def corey_multiplier(self,data,multiplier,risk):


		basket = find_between(data,"Basket=",",") 
		symbol = find_between(data,"Order=*","*") 

		new_order = "Order=*"

		z = 0 
		for i in symbol.split(","):
			if z>=1:
				new_order+=","
			k = i.split(":")
			new_order+= k[0]
			new_order+= ":"+str(int(k[1])*multiplier.get())
			z+=1

		new_order+="*"

		data = "Basket="+basket+","+new_order

		risk__ = risk.get()
		data += ","+"Risk="+str(risk__)+","

		return data


	def http_order(self,data):

		print("RECEVING:",data)

		if "Basket" in data and self.algo_activate.get()==True:

			## PARSE IT AND RE PARSE IT. ? ADD RISK TO IT. 

			name = find_between(data, "Basket=", ",")
			confimed = False 

			if name =="MarketLong" and self.market_long.get()==True:
				confimed = True

				risk = int(self.market_timing_total_risk.get())
				data += ","+"Risk="+str(risk)+","

			elif name =="MarketShort" and self.market_short.get()==True:
				confimed = True
				risk = int(self.market_timing_total_risk.get())
				data += ","+"Risk="+str(risk)+","

			elif name == "BAX1" and self.bax1.get()==True:
				confimed = True
				risk = int(self.bax1_risk.get())
				data += ","+"Risk="+str(risk)+","

			elif name =="BAX2" and self.bax2.get()==True:
				confimed = True
				risk = int(self.bax2_risk.get())
				data += ","+"Risk="+str(risk)+","

			elif name =="BAX3" and self.bax3.get()==True:
				confimed = True
				risk = int(self.bax3_risk.get())
				data += ","+"Risk="+str(risk)+","

			elif name =="BAX4" and self.bax4.get()==True:
				confimed = True
				risk = int(self.bax4_risk.get())
				data += ","+"Risk="+str(risk)+","

			elif name =="BAX5" and self.bax5.get()==True:
				risk = int(self.bax5_risk.get())
				data += ","+"Risk="+str(risk)+","
				confimed = True

			elif "PUFTB" in name and self.corey_PUFTB.get()==True:
				confimed = True

				data = self.corey_multiplier(data,self.corey_PUFTB_multiplier,self.corey_PUFTB_risk)
			elif "MNQ" in name and self.corey_MNQ.get()==True:
				confimed = True

				data = self.corey_multiplier(data,self.corey_MNQ_multiplier,self.corey_MNQ_risk)
			elif "QTSTT" in name and self.corey_QTSTT.get()==True:
				confimed = True
				data = self.corey_multiplier(data,self.corey_QTSTT_multiplier,self.corey_QTSTT_risk)
			elif "STSTT" in name and self.corey_STSTT.get()==True:
				confimed = True
				data = self.corey_multiplier(data,self.corey_STSTT_multiplier,self.corey_STS_risk)
			elif "IWTSTT" in name and self.corey_IWTSTT.get()==True:
				confimed = True
				data = self.corey_multiplier(data,self.corey_IWTSTT_multiplier,self.corey_IWTSTT_risk)
			elif "OTS" in name and self.corey_OTS.get()==True:
				confimed = True
				data = self.corey_multiplier(data,self.corey_OTS_multiplier,self.corey_OTS_risk)
			elif "STS" in name and self.corey_STS.get()==True:
				confimed = True
				data = self.corey_multiplier(data,self.corey_STS_multiplier,self.corey_STS_risk)
			elif "YBO" in name and self.corey_YBO.get()==True:
				confimed = True
				data = self.corey_multiplier(data,self.corey_YBO_multiplier,self.corey_YBO_risk)
			elif "QCK" in name and self.corey_QCK.get()==True:
				confimed = True
				data = self.corey_multiplier(data,self.corey_QCK_multiplier,self.corey_QCK_risk)

			elif "TEST" in name and self.corey_TEST.get()==True:
				confimed = True
				data = self.corey_multiplier(data,self.corey_TEST_multiplier,self.corey_TEST_risk)

			if confimed:

				# risk = int(self.algo_risk.get())
				# data += ","+"Risk="+str(risk)+","
				msg = "http://localhost:4441/"	
				msg += data
				print("Sending:",msg)

				requests.get(msg)
				reg1 = threading.Thread(target=request_post,args=(msg,), daemon=True)
				reg1.start()

		else:
			print("Not activated")


def request_post(body):

	requests.get(body)


if __name__ == '__main__':

	root = tk.Tk() 
	root.title("GoodTrade v489") 
	root.geometry("640x840")

	# print(ratio_compute(0.8))
	# print(ratio_compute(1.2))

	Custom_Algo(root,fake_NT())

	root.mainloop()






	# 		info = [rank,avgv,relv,roc5,roc10,roc15,score,sc,so]
	# 		self.nasdaq.append([])

# # # # df=df.sort_values(by="rank",ascending=False)

# print(df)
# i=0
# for item,row in df.iterrows():
# 	#print(item,row)
# 	df.loc[item,"rank"] =i
# 	i+=1 
# print(df)
# df.loc[df["rank"]==2,"rank5"]=5


# print(df.loc[df["status"]=='New'])
# print(df)


# df=df.sort_values(by=["rank","status"],ascending=False)

# print(df)

