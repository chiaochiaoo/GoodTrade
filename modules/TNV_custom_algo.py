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
		self.algo_activate = tk.BooleanVar(value=0)
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


		self.market_POE_algos = ttk.LabelFrame(self.root,text="Market POE algos")
		self.market_POE_algos.place(x=0.01, rely=0.205, relheight=0.1, relwidth=0.99)


		self.basket_hedging_algos = ttk.LabelFrame(self.root,text="Basket Hedging algos")
		self.basket_hedging_algos.place(x=0.01, rely=0.305, relheight=0.1, relwidth=0.99)

		self.corey_algos = ttk.LabelFrame(self.root,text="Corey algos")
		self.corey_algos.place(x=0.01, rely=0.405, relheight=0.2, relwidth=0.99)

		self.bax_algos = ttk.LabelFrame(self.root,text="Baxter algos")
		self.bax_algos.place(x=0.01, rely=0.605, relheight=0.1, relwidth=0.99)

		self.tick_opening = tk.BooleanVar(value=0)
		self.tick_intraday_v1 = tk.BooleanVar(value=0)
		self.tick_intraday_v2 = tk.BooleanVar(value=0)


		self.market_long = tk.BooleanVar(value=0)
		self.market_short = tk.BooleanVar(value=0)



		self.corey_PUFTB = tk.BooleanVar(value=0)
		self.corey_PUFTB_multiplier = tk.IntVar(value=1)

		self.corey_MNQ = tk.BooleanVar(value=0)
		self.corey_MNQ_multiplier = tk.IntVar(value=1)

		self.corey_QTSTT = tk.BooleanVar(value=0)
		self.corey_QTSTT_multiplier = tk.IntVar(value=1)

		self.corey_STSTT = tk.BooleanVar(value=0)
		self.corey_STSTT_multiplier = tk.IntVar(value=1)

		self.corey_IWTSTT = tk.BooleanVar(value=0)
		self.corey_IWTSTT_multiplier = tk.IntVar(value=1)

		self.corey_OTS = tk.BooleanVar(value=0)
		self.corey_OTS_multiplier = tk.IntVar(value=1)

		self.corey_STS = tk.BooleanVar(value=0)
		self.corey_STS_multiplier = tk.IntVar(value=1)

		# self.corey1 = tk.BooleanVar(value=0)
		# self.corey1_multiplier = tk.IntVar(value=1)
		# self.corey2 = tk.BooleanVar(value=0)
		# self.corey2_multiplier = tk.IntVar(value=1)
		# self.corey3 = tk.BooleanVar(value=0)
		# self.corey3_multiplier = tk.IntVar(value=1)


		self.bax1 = tk.BooleanVar(value=0)
		self.bax2 = tk.BooleanVar(value=0)
		self.bax3 = tk.BooleanVar(value=0)
		self.bax4 = tk.BooleanVar(value=0)
		self.bax5 = tk.BooleanVar(value=0)

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
		ttk.Checkbutton(self.market_timing_algos, variable=self.tick_intraday_v2).grid(sticky="w",column=col+1,row=row)

		col +=2

		ttk.Label(self.market_timing_algos, text="TICK Short:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.market_timing_algos, variable=self.tick_intraday_v2).grid(sticky="w",column=col+1,row=row)



	def algo_pannel(self):

		row = 1
		col = 1
		ttk.Label(self.algo_frame, text="Algo:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algo_frame, variable=self.algo_activate).grid(sticky="w",column=col+1,row=row)

		# ttk.Label(self.algo_frame, text="Default Basket Total Risk:").grid(sticky="w",column=col+2,row=row)
		# ttk.Entry(self.algo_frame, textvariable=self.algo_risk).grid(sticky="w",column=col+3,row=row)


		# row +=1

		# ttk.Label(self.algo_frame, text="Toggle All:").grid(sticky="w",column=col,row=row)
		# ttk.Checkbutton(self.algo_frame, variable=self.tick_opening).grid(sticky="w",column=col+1,row=row)


		row +=1

		ttk.Label(self.corey_algos, text="Corey PUFTB:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_PUFTB).grid(sticky="w",column=col+1,row=row)

		ttk.Label(self.corey_algos, text="Risk multiplier:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.corey_algos, textvariable=self.corey_PUFTB_multiplier).grid(sticky="w",column=col+3,row=row)

		row +=1

		ttk.Label(self.corey_algos, text="Corey MNQ :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_MNQ).grid(sticky="w",column=col+1,row=row)

		ttk.Entry(self.corey_algos, textvariable=self.corey_MNQ_multiplier).grid(sticky="w",column=col+3,row=row)
		ttk.Label(self.corey_algos, text="Risk multiplier:").grid(sticky="w",column=col+2,row=row)


		row +=1

		ttk.Label(self.corey_algos, text="Corey QTSTT :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_QTSTT).grid(sticky="w",column=col+1,row=row)

		ttk.Entry(self.corey_algos, textvariable=self.corey_QTSTT_multiplier).grid(sticky="w",column=col+3,row=row)
		ttk.Label(self.corey_algos, text="Risk multiplier:").grid(sticky="w",column=col+2,row=row)


		row +=1

		ttk.Label(self.corey_algos, text="Corey STSTT :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_STSTT).grid(sticky="w",column=col+1,row=row)

		ttk.Entry(self.corey_algos, textvariable=self.corey_STSTT_multiplier).grid(sticky="w",column=col+3,row=row)
		ttk.Label(self.corey_algos, text="Risk multiplier:").grid(sticky="w",column=col+2,row=row)

		row +=1

		ttk.Label(self.corey_algos, text="Corey IWTSTT :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_IWTSTT).grid(sticky="w",column=col+1,row=row)

		ttk.Entry(self.corey_algos, textvariable=self.corey_IWTSTT_multiplier).grid(sticky="w",column=col+3,row=row)
		ttk.Label(self.corey_algos, text="Risk multiplier:").grid(sticky="w",column=col+2,row=row)


		row +=1

		ttk.Label(self.corey_algos, text="Corey OTS :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_OTS).grid(sticky="w",column=col+1,row=row)

		ttk.Entry(self.corey_algos, textvariable=self.corey_OTS_multiplier).grid(sticky="w",column=col+3,row=row)
		ttk.Label(self.corey_algos, text="Risk multiplier:").grid(sticky="w",column=col+2,row=row)


		row +=1

		ttk.Label(self.corey_algos, text="Corey STS :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.corey_algos, variable=self.corey_STS).grid(sticky="w",column=col+1,row=row)

		ttk.Entry(self.corey_algos, textvariable=self.corey_STS_multiplier).grid(sticky="w",column=col+3,row=row)
		ttk.Label(self.corey_algos, text="Risk multiplier:").grid(sticky="w",column=col+2,row=row)





		row +=1

		ttk.Label(self.bax_algos, text="BAX1:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.bax_algos, variable=self.bax1).grid(sticky="w",column=col+1,row=row)

		col +=2

		ttk.Label(self.bax_algos, text="BAX2:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.bax_algos, variable=self.bax2).grid(sticky="w",column=col+1,row=row)

		col +=4

		ttk.Label(self.bax_algos, text="BAX3:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.bax_algos, variable=self.bax3).grid(sticky="w",column=col+1,row=row)

		col +=6

		ttk.Label(self.bax_algos, text="BAX4:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.bax_algos, variable=self.bax4).grid(sticky="w",column=col+1,row=row)

		col +=8

		ttk.Label(self.bax_algos, text="BAX5:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.bax_algos, variable=self.bax5).grid(sticky="w",column=col+1,row=row)		# for k in range(0,30):

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

	def corey_multiplier(self,data):


		basket = find_between(data,"Basket=",",") 
		symbol = find_between(data,"Order=*","*") 

		new_order = "Order=*"

		z = 0 
		for i in symbol.split(","):
			if z>=1:
				new_order+=","
			k = i.split(":")
			new_order+= k[0]
			new_order+= ":"+str(int(k[1])*self.corey1_multiplier.get())
			z+=1

		new_order+="*"


		data = "Basket="+basket+","+new_order

		return data


	def http_order(self,data):

		#print("RECEVING:",data)

		if "Basket" in data:

			## PARSE IT AND RE PARSE IT. ? ADD RISK TO IT. 

			name = find_between(data, "Basket=", ",")

			confimed = False 


			if name =="MarketLong" and self.market_long.get()==True:
				confimed = True
			elif name =="MarketShort" and self.market_short.get()==True:
				confimed = True
			elif name == "BAX1" and self.bax1.get()==True:
				confimed = True
			elif name =="BAX2" and self.bax2.get()==True:
				confimed = True
			elif name =="BAX3" and self.bax2.get()==True:
				confimed = True
			elif name =="BAX4" and self.bax2.get()==True:
				confimed = True
			elif name =="BAX5" and self.bax2.get()==True:
				confimed = True
			elif name =="COREY1" and self.corey1.get()==True:
				confimed = True

				data = self.corey_multiplier(data)
			elif name =="COREY2" and self.corey1.get()==True:
				confimed = True

				data = self.corey_multiplier(data)
			elif name =="COREY3" and self.corey1.get()==True:
				confimed = True

				data = self.corey_multiplier(data)


			if confimed:

				risk = int(self.algo_risk.get())
				data += ","+"Risk="+str(risk)+","
				msg = "http://localhost:4441/"	
				msg +=data
				print("Sending:",msg)

				requests.get(msg)
				reg1 = threading.Thread(target=request_post,args=(msg,), daemon=True)
				reg1.start()




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

