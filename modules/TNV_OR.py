import tkinter as tk                     
from tkinter import ttk 
import threading
import pandas as pd
import time
from datetime import datetime
#from pannel import *
#from modules.pannel import *

from tkinter import *

def ts_to_min(ts):
	ts = int(ts)
	m = ts//60
	s = ts%60

	return str(m)+":"+str(s)

class Open_Reversal():
	def __init__(self,root,NT,TNV_scanner):

		self.tnv_scanner = TNV_scanner
		self.buttons = []
		self.entries = []
		self.l = 1
		self.NT = NT
		self.labels_width = [9,6,5,7,7,5,6,6,6,6,6,6,8,6,6,6,6]
		self.labels = ["Symbol","Sector","Rel.V","Side","Re.SCORE","SC%","Listed","Since","Add","Algo"]

		self.algo_risk = tk.DoubleVar(value=10)
		self.algo_activate = tk.BooleanVar(value=0)

		self.algo_placed = []
		self.ts_location = 7
		self.root = root
		self.recreate_labels(self.root)

		self.file = "signals/open_resersal_"+datetime.now().strftime("%m-%d")+".csv"

		#self.update_entry(pd.read_csv("tttt.csv",index_col=0))

	def recreate_labels(self,frame):

		self.algo_frame = ttk.LabelFrame(self.root,text="Algo setup")
		self.algo_frame.place(x=0, rely=0, relheight=0.2, relwidth=1)

		self.root = ttk.LabelFrame(self.root,text="")
		self.root.place(x=0, rely=0.12, relheight=0.8, relwidth=1)

		self.algo_pannel(self.algo_frame)
				# self.breakout_frame = ttk.LabelFrame(self.root,text="Volatility Breakout")
		# self.breakout_frame.place(x=0, rely=0.05, relheight=1, relwidth=0.95)


		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

		self.status_code = {}
		self.status_num = 0

		for i in range(len(self.labels)): #Rows
			self.b = tk.Button(self.root, text=self.labels[i],width=self.labels_width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=self.l, column=i)
			self.buttons.append(self.b)

		self.l+=1
		self.create_entry()

	def send_algo(self,symbol,support,resistence,side):

		#self.entries[entry][8]["command"]= lambda symbol=rank,side=side,open_=row['open'],stop_=rscore,risk_=self.algo_risk:self.send_algo(self,symbol,side,open_,stop_,risk_)
		risk = self.algo_risk.get()

		if risk>0:

			if side =="UP":
				info = ["New order",["BreakAny",symbol,support-0.02,resistence,risk,{},"deploy","TrendRider"]]
				#print("sending",info)
			else:
				info = ["New order",["BreakAny",symbol,support,resistence+0.02,risk,{},"deploy","TrendRider"]]
			self.tnv_scanner.send_algo(info)

	def send_group_algos(self,lst):

		risk = self.algo_risk.get()

		#print("HELLO.",lst)
		order = ["New order"]
		if risk>0:
			for i in range(len(lst)):
				#print(lst[i]["symbol"],lst[i]["support"],lst[i]["resistence"])

				change = 0.03
			
				if lst[i]["support"]>10 and lst[i]["support"]<20:
					change = 0.05

				if lst[i]["support"] >20:
					change = 0.06


				if lst[i]["side"] =="UP":
					order.append(["BreakAny",lst[i]["symbol"],lst[i]["support"]-change,lst[i]["resistence"],risk,{},"deploy","TrendRider"])

					#print("sending",info)
				else:
					order.append(["BreakAny",lst[i]["symbol"],lst[i]["support"],lst[i]["resistence"]+change,risk,{},"deploy","TrendRider"])

			self.tnv_scanner.send_algo(order)



	def algo_pannel(self,frame):

		row = 1
		col = 1
		ttk.Label(frame, text="Algo:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(frame, variable=self.algo_activate).grid(sticky="w",column=col+1,row=row)

		ttk.Label(frame, text="Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(frame, textvariable=self.algo_risk).grid(sticky="w",column=col+3,row=row)


		row = 2
		col = 1

		self.hour = tk.IntVar(value=9)
		self.minute = tk.IntVar(value=30)

		ttk.Label(frame, text="Start:").grid(sticky="w",column=col,row=row)
		ttk.Entry(frame, textvariable=self.hour).grid(sticky="w",column=col+1,row=row)

		ttk.Label(frame, text=":").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(frame, textvariable=self.minute).grid(sticky="w",column=col+3,row=row)


		self.rel_v = tk.DoubleVar(value=0)
		self.re_score = tk.DoubleVar(value=0)


		self.ehour = tk.IntVar(value=10)
		self.eminute = tk.IntVar(value=00)
		row = 3
		col = 1
		ttk.Label(frame, text="End").grid(sticky="w",column=col,row=row)
		ttk.Entry(frame, textvariable=self.ehour).grid(sticky="w",column=col+1,row=row)

		ttk.Label(frame, text=":").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(frame, textvariable=self.eminute).grid(sticky="w",column=col+3,row=row)

		self.side_ = tk.StringVar(value='x')
		self.listed_ = tk.BooleanVar(value=False)
		
		# row = 4
		# col = 1


		# ttk.Label(frame, text="Side:").grid(sticky="w",column=col,row=row)
		# l={"Up","Down","Any","Any"}
		# ttk.OptionMenu(frame, self.side_, *sorted(l)).grid(sticky="w",column=col+1,row=row)


		# ttk.Label(frame, text="Listed?").grid(sticky="w",column=col+2,row=row)
		# ttk.Checkbutton(frame, variable=self.listed_).grid(sticky="w",column=col+3,row=row)


		algo_timer = self.hour.get()*60 + self.minute.get()
		#print("algo time",algo_timer)

	def create_entry(self):

		for k in range(0,30):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				
				if i == 8:
					self.b = tk.Button(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				if i ==9:
					self.b = tk.Button(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				else:
					self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
				if i == 9:
					self.b.grid_remove()
			self.l+=1

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		now = datetime.now()
		ts = now.hour*60+now.minute
		
		algo_timer = self.hour.get()*60 + self.minute.get()

		end_timer = self.ehour.get()*60 + self.eminute.get()

		df = data

		#timestamp = data[1]
		#self.NT_stat["text"] = "Last update: "+timestamp
		#df.to_csv("tttt.csv")
		entry = 0

		send_algo=[]

		if len(data)>1:
			if 1:
				for index, row in df.iterrows():
					#print(row)

					#["Symbol","Vol","Rel.V","Side","Re.SCORE","SC%","Listed","Since","Ignore","Add"]
					rank = index
					vol = row['sector']
					relv = row['rel vol']
					side = row['reversalside']
					rscore = row['reversal_score']
					sc = row['SC']

					since = row['reversal_timer']

					row['Signal Time'] = since
					############ add since, and been to the thing #############

					if self.NT != None:
						if rank in self.NT.nasdaq_trader_symbols_ranking:
							listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
						else:
							listed = "No"
					else:
						listed = "No"
					#print(self.NT.nasdaq_trader_symbols)
					if 1: #score>0:	

						lst = [rank,vol,relv,side,rscore,sc,listed,since]

						ts_location = 7

						for i in range(len(lst)):
							
							if lst[ts_location] >=ts and lst[ts_location]>=algo_timer and lst[ts_location]<=end_timer:
								self.entries[entry][i]["background"] = "LIGHTGREEN"
								self.entries[entry][9].grid()

								if side == "UP":
									support = row['low']
									resistence = row['open']
								else:
									support = row['open']
									resistence = row['high']

								self.entries[entry][9]["command"]= lambda symbol=rank,support=support,side=side,resistence=resistence:self.send_algo(symbol,support,resistence,side)

								if self.algo_activate.get()==1:
									if rank not in self.algo_placed:

										#self.send_algo(rank,support,resistence,self.algo_risk)
										self.algo_placed.append(rank)

										order = {}

										order["symbol"] = rank
										order["support"] = support
										order["resistence"] = resistence

										order["side"] = side

										send_algo.append(order)

										#print(rank,self.algo_placed)
										
							if i == ts_location:
								self.entries[entry][i]["text"] = ts_to_min(lst[i])
							else:
								self.entries[entry][i]["text"] = lst[i]
								self.entries[entry][8].grid_remove() 
								#self.entries[entry][8].grid_remove() 
								#self.entries[entry][9].grid_forget()
							#self.entries[entry][8].grid() 
						#add the button here?

						entry+=1
						if entry ==30:
							break

				while entry<30:
					#print("ok")
					for i in range(10):
						self.entries[entry][i]["text"] = ""
					entry+=1

				# keep = ['Symbol', "Signal Time", 'rel vol', 'SC', 'reversalside','reversal_score','Signal Time',]

				# for i in df.columns:
				# 	if i not in keep:
				# 		df.pop(i)
				df.to_csv(self.file)
			# except Exception as e:
			# 	print("TNV scanner construction open reversal:",e)

			if len(send_algo)>0:
				self.send_group_algos(send_algo)

