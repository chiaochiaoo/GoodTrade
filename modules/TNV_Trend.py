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



class StandardScanner():
	def __init__(self,root,NT,TNV):

		self.algo_placed = []
		self.buttons = []
		self.entries = []
		self.l = 1
		self.tnv_scanner = TNV
		self.NT = NT


		self.root = root

		self.algo_risk = tk.DoubleVar(value=10)
		self.algo_activate = tk.BooleanVar(value=0)

		self.recreate_labels(self.root)


	def recreate_labels(self,frame):

		self.algo_frame = ttk.LabelFrame(self.root,text="Algo setup")
		self.algo_frame.place(x=0, rely=0, relheight=0.2, relwidth=1)

		self.root = ttk.LabelFrame(self.root,text="")
		self.root.place(x=0, rely=0.12, relheight=0.8, relwidth=1)

		self.labels_position = {}
		self.labels_position["Rank"]=0
		self.labels_position["Symbol"]=1
		self.labels_position["Market"]=2
		self.labels_position["Price"]=3
		self.labels_position["Since"]=4
		self.labels_position["Been"]=5
		self.labels_position["SC%"]=6
		self.labels_position["SO%"]=7
		self.labels_position["L5R%"]=8
		self.labels_position["Status"]=9
		self.labels_position["Add"]=10

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

		self.algo_pannel(self.algo_frame)
		self.create_entry()

	def algo_pannel(self,frame):

		row = 1
		col = 1
		ttk.Label(frame, text="Algo:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(frame, variable=self.algo_activate).grid(sticky="w",column=col+1,row=row)

		ttk.Label(frame, text="Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(frame, textvariable=self.algo_risk).grid(sticky="w",column=col+3,row=row)


		row = 2
		col = 1

		self.hour = tk.IntVar(value=10)
		self.minute = tk.IntVar(value=00)

		ttk.Label(frame, text="Start:").grid(sticky="w",column=col,row=row)
		ttk.Entry(frame, textvariable=self.hour).grid(sticky="w",column=col+1,row=row)

		ttk.Label(frame, text=":").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(frame, textvariable=self.minute).grid(sticky="w",column=col+3,row=row)


		self.rel_v = tk.DoubleVar(value=0)
		self.re_score = tk.DoubleVar(value=0)


		self.ehour = tk.IntVar(value=15)
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

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1



class ADX(StandardScanner):
	def __init__(self,root,NT,TNV):

		
		self.labels_width = [9,6,12,5,8,5,6,6,6,6,6,6,8,6]

		self.labels = ["Symbol","Sector","TrendScore","Rg.Score","Rel.V","SO%","SC%","listed","Add"]
		self.tnv_scanner = TNV
		self.total_len = len(self.labels)
		super().__init__(root,NT,TNV)

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		df = data


		#df.to_csv("tttt.csv")
		entry = 0


		threshold = 25

		now = datetime.now()
		ts = now.hour*60+now.minute

		algo_timer = self.hour.get()*60 + self.minute.get()
		end_timer = self.ehour.get()*60 + self.eminute.get()

		send_algo =[]
		if 1:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				sec = row['sector']
				relv = row['rrvol']
				near = row['rangescore']

				adx = str([row['ema9time'],row['ema21time'],row['ema45time']])
				so = row['SO']
				sc = row['SC']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,sec,adx,near,relv,so,sc,listed]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

					if self.algo_activate.get()==1 and ts>=algo_timer and ts<=end_timer:
						if rank not in self.algo_placed:

							send = False

							order = {}
							order["symbol"] = rank

							

							if row['ema9time']==1 or row['ema21time']==1:

								if row['ema45time']>=25:
									order["support"] = round(row['ema45'],2)
									order["resistence"] = row['price']	
									order["side"] = "UP"			
									send=True

							if row['ema9time']==-1 or row['ema21time']==-1:

								if row['ema45time']<=-25:

									order["support"] = row['price']	
									order["resistence"] =  round(row['ema45'],2)
									order["side"] = "DOWN"
									send=True							


			
							if send:
								send_algo.append(order)

			while entry<50:
				#print("ok")
				for i in range(self.total_len):
					self.entries[entry][i]["text"] = ""
				entry+=1

			if len(send_algo)>0:
				self.send_group_algos(send_algo)
		# except Exception as e:
		# 	print("TNV scanner construction near high:",e)
	

	def send_group_algos(self,lst):

		risk = self.algo_risk.get()

		#print("HELLO.",lst)
		order = ["New order"]
		if risk>0:
			for i in range(len(lst)):

				if lst[i]["side"]=="UP":
					order.append([" BreakUp",lst[i]["symbol"],lst[i]["support"],lst[i]["resistence"],risk,{},"deploy","1:2 Exprmntl"])

				elif lst[i]["side"]=="DOWN":
					order.append([" BreakDn",lst[i]["symbol"],lst[i]["support"],lst[i]["resistence"],risk,{},"deploy","1:2 Exprmntl"])


			self.tnv_scanner.send_algo(order)


	# def send_algo(self,symbol,support,resistence,side):

	# 	print("sending",symbol,support,resistence,side)
	# 	#self.entries[entry][8]["command"]= lambda symbol=rank,side=side,open_=row['open'],stop_=rscore,risk_=self.algo_risk:self.send_algo(self,symbol,side,open_,stop_,risk_)
	# 	risk = self.algo_risk.get()

	# 	if risk>0:

	# 		# change = 0.03
			
	# 		# if support>10 and support<20:
	# 		# 	change = 0.06

	# 		# if support >20:
	# 		# 	change = 0.08

	# 		if side =="UP":
	# 			info = ["New order",[" BreakUp",symbol,support,resistence,risk,{},"deploy","TrendRider"]]
	# 			#print("sending",info)
	# 		else:
	# 			info = ["New order",[" BreakDn",symbol,support,resistence,risk,{},"deploy","TrendRider"]]
	# 		self.tnv_scanner.send_algo(info)


# class ADX(StandardScanner):
# 	def __init__(self,root,NT):

# 		self.buttons = []
# 		self.entries = []
# 		self.l = 1
# 		self.labels_width = [9,6,12,5,8,5,6,6,6,6,6,6,8,6]

# 		self.labels = ["Symbol","Sector","TrendScore","Rg.Score","Rel.V","SO%","SC%","listed","Add"]

# 		self.total_len = len(self.labels)
# 		self.root = root
# 		self.recreate_labels(self.root)

# 	def recreate_labels(self,frame):

# 		self.labels_position = {}
# 		self.labels_position["Rank"]=0
# 		self.labels_position["Symbol"]=1
# 		self.labels_position["Market"]=2
# 		self.labels_position["Price"]=3
# 		self.labels_position["Since"]=4
# 		self.labels_position["Been"]=5
# 		self.labels_position["SC%"]=6
# 		self.labels_position["SO%"]=7
# 		self.labels_position["L5R%"]=8
# 		self.labels_position["Status"]=9
# 		self.labels_position["Add"]=10

# 		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

# 		self.status_code = {}
# 		self.status_num = 0

# 		for i in range(len(self.labels)): #Rows
# 			self.b = tk.Button(self.root, text=self.labels[i],width=self.labels_width[i])#,command=self.rank
# 			self.b.configure(activebackground="#f9f9f9")
# 			self.b.configure(activeforeground="black")
# 			self.b.configure(background="#d9d9d9")
# 			self.b.configure(disabledforeground="#a3a3a3")
# 			self.b.configure(relief="ridge")
# 			self.b.configure(foreground="#000000")
# 			self.b.configure(highlightbackground="#d9d9d9")
# 			self.b.configure(highlightcolor="black")
# 			self.b.grid(row=self.l, column=i)
# 			self.buttons.append(self.b)

# 		self.l+=1
# 		self.create_entry()

# 	def create_entry(self):

# 		for k in range(0,50):

# 			self.entries.append([])

# 			for i in range(len(self.labels)): #Rows
# 				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
# 				self.b.grid(row=self.l, column=i)
# 				self.entries[k].append(self.b)
# 			self.l+=1

