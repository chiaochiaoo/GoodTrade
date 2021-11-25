import tkinter as tk                     
from tkinter import ttk 
import threading
import pandas as pd
import time
from datetime import datetime
#from pannel import *
#from modules.pannel import *

from tkinter import *


# from TNV_PMB import *
# from TNV_OR import *
# from TNV_TFM import *
# from TNV_Trend import *

from modules.TNV_PMB import *
from modules.TNV_OR import *
from modules.TNV_TFM import *
from modules.TNV_Trend import *

class fake_NT():

	def __init__(self):

		self.nasdaq_trader_symbols_ranking=[]

def ts_to_min(ts):
	ts = int(ts)
	m = ts//60
	s = ts%60

	return str(m)+":"+str(s)

class TNV_Scanner():

	def __init__(self,root,NT,commlink,data):

		
		self.root = root

		self.NT = NT

		self.algo_commlink = commlink

		self.data = data
		#self.NT_update_time = tk.StringVar(value='Last updated')
		#self.NT_update_time.set('Last updated')

		self.NT_stat = ttk.Label(self.root, text="Last update: ")
		self.NT_stat.place(x=10, y=10, height=25, width=260)	


		if data!=None:
			self.socket = Label(self.root,textvariable=self.data.algo_socket,background="red",height=1,width=12)
			self.connection =Label(self.root,textvariable=self.data.algo_manager_connected,background="red",height=1,width=14)

			self.socket.place(x=250,y=10)
			self.connection.place(x=350,y=10)

			self.data.algo_socket.trace('w', lambda *_,vals=self.socket,val=self.data.algo_socket: self.color(vals,val))
			self.data.algo_manager_connected.trace('w', lambda *_,vals=self.connection,val=self.data.algo_manager_connected: self.color(vals,val))



		self.TNV_TAB = ttk.Notebook(self.root)
		self.TNV_TAB.place(x=0,rely=0.05,relheight=1,width=640)

		# OR 
		self.or_frame = tk.Canvas(self.TNV_TAB)
		self.TNV_TAB.add(self.or_frame, text ='Open Reversal')
		self.open_reversal = Open_Reversal(self.or_frame,NT,self)

		# PMB
		self.pmb_frame = tk.Canvas(self.TNV_TAB)
		self.TNV_TAB.add(self.pmb_frame, text ='PMB')
		self.pmb = Premarket_breakout(self.pmb_frame,NT,self)

		# NH NL
		self.nh_frame = tk.Canvas(self.TNV_TAB)
		self.nl_frame = tk.Canvas(self.TNV_TAB)
		self.TNV_TAB.add(self.nh_frame, text ='Near High')
		self.TNV_TAB.add(self.nl_frame, text ='Near Low')
		self.near_high = Near_high(self.nh_frame,NT)
		self.near_low = Near_low(self.nl_frame,NT)

		# JB 
		self.vb_frame = tk.Canvas(self.TNV_TAB)
		self.TNV_TAB.add(self.vb_frame, text ='Just Break')
		self.volatility_scanner = Just_break(self.vb_frame,NT)

		# NH NL
		self.oh_frame = tk.Canvas(self.TNV_TAB)
		self.ol_frame = tk.Canvas(self.TNV_TAB)
		self.TNV_TAB.add(self.oh_frame, text ='Open High')
		self.TNV_TAB.add(self.ol_frame, text ='Open Low')
		self.oh = Open_high(self.oh_frame,NT)
		self.ol = Open_low(self.ol_frame,NT)

		# RRVOL
		self.rrvol_frame = tk.Canvas(self.TNV_TAB)
		self.TNV_TAB.add(self.rrvol_frame, text ='RRVol')
		self.rrvol = RRvol(self.rrvol_frame,NT)


 
		self.trending_frame = tk.Canvas(self.TNV_TAB)
		self.TNV_TAB.add(self.trending_frame, text ='Trending')
		self.trending = ADX(self.trending_frame,NT)

		# Spread 
		# self.spread_frame = tk.Canvas(self.TNV_TAB)
		# self.TNV_TAB.add(self.spread_frame, text ='Spread')
		# self.spread = Spread(self.spread_frame,NT)

		# # TFM
		# self.TFM_frame = tk.Canvas(self.TNV_TAB)
		# self.TNV_TAB.add(self.TFM_frame, text ='TradeForMe')
		# self.tfm = TFM(self.TFM_frame,self)


		#filtered_df = pd.read_csv("test.csv",index_col=0)

		#self.filtering(filtered_df)

		# self.trending.update_entry(item)
		# self.pmb.update_entry(item)
		# self.near_high.update_entry(item)
		# self.near_low.update_entry(item)
		#self.open_reversal.update_entry(item)
		#self.update_entry()

	def send_algo(self,msg):
		self.algo_commlink.send(msg)

	def color(self,vals,val):

		if val.get()[-4:]=="alse":
			vals["background"] = "red"
		elif val.get()[-4:]=="True":
			vals["background"] = "#97FEA8"


	def update_entry(self,data):

		timestamp = data[1]
		self.NT_stat["text"] = "Last update: "+timestamp

		filtered_df = data[0]

		pb =  filtered_df.loc[((filtered_df["SC"]>=1)|(filtered_df["SC"]<=-1))][:25]
		
		##################### NEAR LOW #############################
		at_high = filtered_df.loc[(filtered_df["rangescore"]<=0.1)][:25] #&&(filtered_df["last_break"])
		#at_low.to_csv("at low.csv")

		##################### NEAR HIGH #############################
		at_low = filtered_df.loc[(filtered_df["rangescore"]>=0.9)][:25]

		##################### Just break #############################
		just_break = filtered_df.loc[(filtered_df["just_break"]!="")&(filtered_df["break_span"]>=15)][:20]


		#reversalside is not null. shall not be nullified. only take the first reversal. 
		openreverse = filtered_df.loc[(filtered_df["reversal"]==True)&(filtered_df["Market Cap"]>0)&(filtered_df["reversalside"]!="")]
		openreverse = openreverse.sort_values(by=["reversal_timer"],ascending=False)[:20]
		

		trending =  filtered_df.loc[(filtered_df["ema21"]>=20)|(filtered_df["ema21"]<=-20)]
		trending =  trending.reindex(trending.ema45.abs().sort_values(ascending=False).index)[:20] #df.sort_values(by=["ema21"],ascending=False)

		# OH , OL, RRVOL

		oh = filtered_df.loc[filtered_df["oh"]>0.5]
		oh = oh.sort_values(by=["oh"],ascending=False)[:28]

		ol = filtered_df.loc[filtered_df["ol"]>0.5]
		ol = ol.sort_values(by=["ol"],ascending=False)[:28]
		rrvol = filtered_df.sort_values(by=["rrvol"],ascending=False)[:20]


		self.volatility_scanner.update_entry(just_break)
		self.open_reversal.update_entry(openreverse)
		self.near_low.update_entry(at_low)
		self.near_high.update_entry(at_high)
		self.trending.update_entry(trending)
		self.pmb.update_entry(pb)
		self.oh.update_entry(oh)
		self.ol.update_entry(ol)
		self.rrvol.update_entry(rrvol)


	# def update_entry(self,data):
	# 	timestamp = data[1]
	# 	self.NT_stat["text"] = "Last update: "+timestamp

	# 	#print(data[0].keys())
	# 	for key,item in data[0].items():
	# 		#print("HELLO,",key)
	# 		if key == "just_break":
	# 			self.volatility_scanner.update_entry(item)
	# 			#item.to_csv("test.csv")
	# 		elif key == "Open_Reseral":
	# 			self.open_reversal.update_entry(item)
	# 			#item.to_csv("2.csv")
	# 		elif key == "near_low":
	# 			self.near_low.update_entry(item)
	# 			#item.to_csv("3.csv")
	# 		elif key =="near_high":
	# 			self.near_high.update_entry(item)

	# 		elif key =="trending":
	# 			self.trending.update_entry(item)

	# 		# elif key =="spread":
	# 		# 	self.spread.update_entry(item)

	# 		elif key =="premarket_breakout":
	# 			self.pmb.update_entry(item)

	# 		elif key =="oh":
	# 			self.oh.update_entry(item)
	# 		elif key =="ol":
	# 			self.ol.update_entry(item)


	# 		elif key =="rrvol":
	# 			self.rrvol.update_entry(item)

class RRvol():
	def __init__(self,root,NT):

		self.buttons = []
		self.entries = []
		self.l = 1
		self.labels_width = [9,6,5,8,5,5,6,6,6,6,6,6,8,6]
		self.NT = NT
		self.labels = ["Symbol","Sector","RR.Vol","Rg.Score","SO%","SC%","listed","Add"]
		#[rank,sec,relv,near,high,so,sc]
		self.total_len = len(self.labels)
		self.root = root
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

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
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1

	def update_entry(self,data):


		df = data

		#df.to_csv("tttt.csv")
		entry = 0

		if 1:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				sec = row['sector']
				relv = row['rrvol']
				near = row['rangescore']
	
				so = row['SO']
				sc = row['SC']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,sec,relv,near,so,sc,listed]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(self.total_len):
					self.entries[entry][i]["text"] = ""
				entry+=1
		# except Exception as e:
		# 	print("TNV scanner construction near high:",e)


class Just_break():
	def __init__(self,root,NT):

		self.buttons = []
		self.entries = []
		self.l = 1
		self.labels_width = [9,6,5,5,5,5,6,6,6,6,6,6,8,6]
		self.NT = NT
		self.labels = ["Symbol","Sector","Rel.V","Side","Been","SO%","SC%","Rg eval","Vol eval","listed","Add"]
		self.root = root
		self.total_len = len(self.labels)
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

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
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		df = data


		#df.to_csv("tttt.csv")
		entry = 0

		try:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				sec = row['sector']
				relv = row['rel vol']
				side = row['just_break']

				span = row['break_span']
				so = row['SO']
				sc = row['SC']

				tr =  row['tr_eval']
				vol = row['vol_eval']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,sec,relv,side,span,so,sc,tr,vol,listed]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(self.total_len):
					self.entries[entry][i]["text"] = ""
				entry+=1
		except Exception as e:
			print("TNV scanner construction voli:",e)

class Open_high():
	def __init__(self,root,NT):

		self.buttons = []
		self.entries = []
		self.l = 1
		self.labels_width = [9,6,5,8,5,5,6,6,6,6,6,6,8,6]
		self.NT = NT
		self.labels = ["Symbol","Sector","OH","Rel.V","Rg.Score","High","SO%","SC%","listed","Add"]
		#[rank,sec,relv,near,high,so,sc]
		self.total_len = len(self.labels)
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

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		df = data


		#df.to_csv("tttt.csv")
		entry = 0

		if 1:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				sec = row['sector']
				relv = row['rrvol']
				near = row['rangescore']
				high = row['high']

				oh = row["oh"]
				so = row['SO']
				sc = row['SC']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,sec,oh,relv,near,high,so,sc,listed]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(self.total_len):
					self.entries[entry][i]["text"] = ""
				entry+=1
		# except Exception as e:
		# 	print("TNV scanner construction near high:",e)

class Open_low():
	def __init__(self,root,NT):

		self.buttons = []
		self.entries = []
		self.l = 1
		self.labels_width = [9,6,5,8,5,5,6,6,6,6,6,6,8,6]
		self.NT = NT
		self.labels = ["Symbol","Sector","OL","Rel.V","Rg.Score","High","SO%","SC%","listed","Add"]
		#[rank,sec,relv,near,high,so,sc]
		self.total_len = len(self.labels)
		self.root = root
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

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
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		df = data


		#df.to_csv("tttt.csv")
		entry = 0

		if 1:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				sec = row['sector']
				relv = row['rrvol']
				near = row['rangescore']
				high = row['high']

				oh = row["ol"]
				so = row['SO']
				sc = row['SC']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,sec,oh,relv,near,high,so,sc,listed]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(self.total_len):
					self.entries[entry][i]["text"] = ""
				entry+=1
		# except Exception as e:
		# 	print("TNV scanner construction near high:",e)

class Near_high():
	def __init__(self,root,NT):

		self.buttons = []
		self.entries = []
		self.l = 1
		self.labels_width = [9,6,5,8,5,5,6,6,6,6,6,6,8,6]
		self.NT = NT
		self.labels = ["Symbol","Sector","Rel.V","Rg.Score","High","SO%","SC%","listed","Add"]
		#[rank,sec,relv,near,high,so,sc]
		self.total_len = len(self.labels)
		self.root = root
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

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
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		df = data


		#df.to_csv("tttt.csv")
		entry = 0

		if 1:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				sec = row['sector']
				relv = row['rel vol']
				near = row['rangescore']
				high = row['high']

				so = row['SO']
				sc = row['SC']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,sec,relv,near,high,so,sc,listed]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(self.total_len):
					self.entries[entry][i]["text"] = ""
				entry+=1
		# except Exception as e:
		# 	print("TNV scanner construction near high:",e)

class Near_low():
	def __init__(self,root,NT):

		self.buttons = []
		self.entries = []
		self.l = 1
		self.labels_width = [9,6,5,8,5,5,6,6,6,6,6,6,8,6]
		self.NT = NT
		self.labels = ["Symbol","Sector","Rel.V","Rg.Score","Low","SO%","SC%","listed","Add"]
		#[rank,sec,relv,near,high,so,sc]
		self.root = root

		self.total_len = len(self.labels)
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

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
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		df = data


		#df.to_csv("tttt.csv")
		entry = 0

		try:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				sec = row['sector']
				relv = row['rel vol']
				near = row['rangescore']
				high = row['low']

				so = row['SO']
				sc = row['SC']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,sec,relv,near,high,so,sc,listed]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(self.total_len):
					self.entries[entry][i]["text"] = ""
				entry+=1
		except Exception as e:
			print("TNV scanner construction near low:",e)




class Spread():
	def __init__(self,root,NT):

		self.buttons = []
		self.entries = []
		self.l = 1
		self.labels_width = [9,8,4,4,4,8,6,8,6,6,6,6,8,6]
		self.NT = NT
		self.labels = ["Pairs","CurSpread","Cur σ","PC σ","OP σ","Last5m σ","Ratio","R.Stability","Add"]
		#[rank,sec,relv,near,high,so,sc]
		self.total_len = len(self.labels)
		self.root = root
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

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
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]
		# Index(['symbol1', 'symbol2', 'current_spread', 'date', 'ratio_mean',
		#        'ratio_stability', 'outlier', 'neg_tail997', 'pos_tail997',
		#        'neg_tail990', 'pos_tail990', 'neg_tail970', 'pos_tail970',
		#        'coefficient', 'intercept', 'std', 'pe', 'pr', 'avgr', 'stdr',
		#        'quality', 'current_sigma'],
		df = data


		#df.to_csv("tttt.csv")
		entry = 0

		if 1:
			for index, row in df.iterrows():
				#print(row)
				#["Pairs","CurSpread","Cur σ","PC σ","OP σ","DayMax σ","DayLow σ","Ratio","R.Stability","Add"]
				#"current_sigma","close_sigma","open_sigma","max_sigma","min_sigma","last5_sigma"
				rank = index
				spread = round(row['current_spread'],2)
				sig = round(row['current_sigma'],2)

				pcsig = round(row['close_sigma'],2)
				opsig = round(row['open_sigma'],2)

				last5 = round(row['last5_sigma'],2)

				ratio = ratio_compute(row['coefficient'])
				ratio_stability = str(round((1-row['ratio_stability'])*100))+"%"


				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,spread,sig,pcsig,opsig,last5,ratio,ratio_stability]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(self.total_len):
					self.entries[entry][i]["text"] = ""
				entry+=1
		# except Exception as e:
		# 	print("TNV scanner construction near high:",e)


class Premarket_pick():
	def __init__(self,root,NT):
		self.buttons = []
		self.entries = []
		self.l = 1
		self.NT = NT
		self.labels_width = [9,6,5,7,7,7,7,7,6,6,6,6,8,6]
		self.labels = ["Symbol","A.Vol","Rel.V","RR.ratio","Ex.Mmtm","Rg.SCORE","SC%","Listed","Add"]
		self.root = root
		self.recreate_labels(self.root)

		self.file = "signals/premarket_pick_"+datetime.now().strftime("%m-%d")+".csv"

		#self.update_entry([pd.read_csv("test2.csv",index_col=0)])

	def recreate_labels(self,frame):

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

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		df = data
		#timestamp = data[1]

		#self.NT_stat["text"] = "Last update: "+timestamp

		#df.to_csv("tttt.csv")
		entry = 0

		if len(data)>1:
			try:
				for index, row in df.iterrows():
					#print(row)

					#["Symbol","Vol","Rel.V","Side","Re.SCORE","SC%","Listed","Since","Ignore","Add"]
					rank = index
					vol = row['Avg VolumeSTR']
					relv = row['rel vol']
					side = row['reversalside']
					rscore = row['rangescore']
					sc = row['SC']

					since = ts_to_min(row['reversal_timer'])

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

						for i in range(len(lst)):
							self.entries[entry][i]["text"] = lst[i]
						entry+=1
						if entry ==50:
							break

				while entry<50:
					#print("ok")
					for i in range(10):
						self.entries[entry][i]["text"] = ""
					entry+=1

				# keep = ['Symbol', "Signal Time", 'rel vol', 'SC', 'reversalside','reversal_score','Signal Time',]

				# for i in df.columns:
				# 	if i not in keep:
				# 		df.pop(i)
				#df.to_csv(self.file)
			except Exception as e:
				print("TNV scanner construction Premarket_pick:",e)

class Open_Break():
	def __init__(self,root,NT):
		self.buttons = []
		self.entries = []
		self.l = 1
		self.NT = NT
		self.labels_width = [9,6,5,7,5,5,6,6,6,6,8,6]
		self.labels = ["Symbol","A.Vol","Rel.V","Br.SCORE","5M","SO%","SC%","Listed","Since","Last","Ignore","Add"]
		self.file = "signals/open_break_"+datetime.now().strftime("%m-%d")+".csv"
		self.root = root
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

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
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1

	def update_entry(self,data):

		#at most 8.

		#["Symbol","A.Vol","Rel.V","Br.SCORE","5M","SO%","SC%","Listed","Since","Last","Ignore","Add"]
		df = data


		#df.to_csv("open_break_out.csv")
		entry = 0

		try:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				vol = row['Avg VolumeSTR']
				relv = row['rel vol']
				brscore = row['score2']
				roc5 = row['5ROCP']
				so = row['SO']
				sc = row['SC']
				since = ts_to_min(row['since'])
				last = row['last']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,vol,relv,brscore,roc5,so,sc,listed,since,last]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(10):
					self.entries[entry][i]["text"] = ""
				entry+=1

		except Exception as e:
			print("TNV scanner construction open break:",e)

class CoreysPick():
	def __init__(self,root,NT):
		self.buttons = []
		self.entries = []
		self.l = 1
		self.NT = NT
		self.labels_width = [9,6,5,7,5,5,6,6,6,6,8,6]
		self.labels = ["Symbol","A.Vol","Rel.V","Br.SCORE","5M","SO%","SC%","Listed","Since","Last","Ignore","Add"]
		self.file = "signals/Coreypick"+datetime.now().strftime("%m-%d")+".csv"
		self.root = root
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

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
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1


	def update_entry(self,data):

		#at most 8.

		#["Symbol","A.Vol","Rel.V","Br.SCORE","5M","SO%","SC%","Listed","Since","Last","Ignore","Add"]
		df = data


		#df.to_csv("open_break_out.csv")
		entry = 0

		try:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				vol = row['Avg VolumeSTR']
				relv = row['rel vol']
				brscore = row['score2']
				roc5 = row['5ROCP']
				so = row['SO']
				sc = row['SC']
				since = row['since']
				last = row['last']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,vol,relv,brscore,roc5,so,sc,listed,since,last]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(10):
					self.entries[entry][i]["text"] = ""
				entry+=1

		except Exception as e:
			print("TNV scanner construction open break:",e)


def ratio_compute(n):

	if n<1:
		return str(int(100*n)) +":100"
	else:
		return "100:"+str(int(100/n)) 
if __name__ == '__main__':

	root = tk.Tk() 
	root.title("GoodTrade v489") 
	root.geometry("640x840")

	print(ratio_compute(0.8))
	print(ratio_compute(1.2))

	TNV_Scanner(root,fake_NT(),None,None)

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

