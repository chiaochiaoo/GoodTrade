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

class TFM():
	def __init__(self,root,TNV_scanner):



		self.tabControl = ttk.Notebook(root)
		self.tab1 = tk.Canvas(self.tabControl)
		self.tab2 = tk.Canvas(self.tabControl)
		self.tab3 = tk.Canvas(self.tabControl)

		self.tabControl.add(self.tab1, text ='Single Trade') 

		self.tabControl.add(self.tab2, text ='Pair Trade') 

		self.tabControl.add(self.tab3, text ='Basket Trade') 

		self.tabControl.pack(expand = 1, fill ="both")

		s = SinlgeTrade(self.tab1,TNV_scanner)
		
		p = PairTrade(self.tab2,TNV_scanner)

class PairTrade():
	def __init__(self,root,TNV_scanner):

		self.tnv_scanner = TNV_scanner
		self.buttons = []
		self.entries = []
		self.l = 1


		self.symbol1 = tk.StringVar()
		self.symbol2 = tk.StringVar()
		self.symbol1_share = tk.IntVar()
		self.symbol2_share = tk.IntVar()


		self.algo_risk = tk.DoubleVar(value=10)

		self.file = "signals/open_resersal_"+datetime.now().strftime("%m-%d")+".csv"

		self.side_options = ("Long", "Short")
		self.type_options = ("Rightaway","Target")
		self.management_options = ("1:2 Exprmntl","1:2 Wide","Fib Only","SemiManual","FullManual")

		self.algo_placed = []
		self.ts_location = 7


		self.listening = ttk.LabelFrame(root) 
		self.listening.place(relx=0,rely=0,relheight=1,relwidth=1)


		self.root = root
		self.recreate_labels_single(self.root)
		

		
		#self.update_entry(pd.read_csv("tttt.csv",index_col=0))

	def recreate_labels_single(self,frame):

		self.symbol_frame = ttk.LabelFrame(self.root,text="Trade Setup")
		self.symbol_frame.place(x=0, rely=0.01, relheight=0.15, relwidth=1)

		self.entry_frame = ttk.LabelFrame(self.root,text="Entry Setup")
		self.entry_frame.place(x=0, rely=0.16, relheight=0.1, relwidth=1)

		self.management_frame = ttk.LabelFrame(self.root,text="Management Setup")
		self.management_frame.place(x=0, rely=0.27, relheight=0.12, relwidth=1)

		self.confirm_frame = ttk.LabelFrame(self.root,text="Confirmation")
		self.confirm_frame.place(x=0, rely=0.37, relheight=0.12, relwidth=1)
		# self.root = ttk.LabelFrame(self.root,text="")
		# self.root.place(x=0, rely=0.12, relheight=0.8, relwidth=1)

		self.trade_pannel(self.symbol_frame)

		self.entry_pannel(self.entry_frame)

		self.management_pannel(self.management_frame)

		self.confirmation_pannel(self.confirm_frame)

		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

		self.status_code = {}
		self.status_num = 0

		self.l+=1

	def recreate_labels_pair(self,frame):

		self.symbol_frame = ttk.LabelFrame(frame,text="Trade Setup")
		self.symbol_frame.place(x=0, rely=0.01, relheight=0.3, relwidth=1)

		self.entry_frame = ttk.LabelFrame(frame,text="Entry Setup")
		self.entry_frame.place(x=0, rely=0.31, relheight=0.1, relwidth=1)

		self.management_frame = ttk.LabelFrame(frame,text="Management Setup")
		self.management_frame.place(x=0, rely=0.42, relheight=0.12, relwidth=1)

		self.confirm_frame = ttk.LabelFrame(frame,text="Confirmation")
		self.confirm_frame.place(x=0, rely=0.52, relheight=0.12, relwidth=1)
		# self.root = ttk.LabelFrame(self.root,text="")
		# self.root.place(x=0, rely=0.12, relheight=0.8, relwidth=1)

		self.trade_pannel(self.symbol_frame)

		self.entry_pannel(self.entry_frame)

		self.management_pannel(self.management_frame)

		self.confirmation_pannel(self.confirm_frame)

		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

		self.status_code = {}
		self.status_num = 0

		self.l+=1


	def trade_pannel(self,frame):

		row = 1
		col = 1
		ttk.Label(frame, text="Symbol1:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Entry(frame, textvariable=self.symbol1).grid(sticky="w",column=col,row=row+1,padx=10)

		col +=1

		ttk.Label(frame, text="Symbol2:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Entry(frame, textvariable=self.symbol2).grid(sticky="w",column=col,row=row+1,padx=10)

		col +=1
		ttk.Label(frame, text="Risk:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Entry(frame, textvariable=self.algo_risk).grid(sticky="w",column=col,row=row+1,padx=10)
		# self.symbol1 = tk.StringVar()
		# self.symbol2 = tk.StringVar()
		# self.symbol1_share = tk.IntVar()
		# self.symbol2_share = tk.IntVar()
		row +=2

		col = 1
		ttk.Label(frame, text="Symbol1 Share:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Entry(frame, textvariable=self.symbol1_share).grid(sticky="w",column=col,row=row+1,padx=10)

		col +=1
		ttk.Label(frame, text="Symbol2 Share:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Entry(frame, textvariable=self.symbol2_share).grid(sticky="w",column=col,row=row+1,padx=10)



	def entry_pannel(self,frame):

		self.side = tk.StringVar()
		self.type = tk.StringVar()

		self.limit_price = tk.DoubleVar()


		self.side.set("Long")
		self.type.set("Rightaway")


		row = 2
		col = 1


		# ttk.Label(frame, text="Side:").grid(sticky="w",column=col,row=row,padx=10)
		# ttk.OptionMenu(frame, self.side,self.side_options[0],*self.side_options).grid(sticky="w",column=col,row=row+1,padx=10)

		# col += 1
		ttk.Label(frame, text="Type:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.OptionMenu(frame, self.type,self.type_options[0],*self.type_options).grid(sticky="w",column=col,row=row+1,padx=10)

		# col += 1
		# ttk.Label(frame, text="Limit Price (If applicable):").grid(sticky="w",column=col,row=row,padx=10)
		# ttk.Entry(frame, textvariable=self.limit_price).grid(sticky="w",column=col,row=row+1,padx=10)


		
		# row = 4
		# col = 1

		# ttk.Label(frame, text="Side:").grid(sticky="w",column=col,row=row)
		# l={"Up","Down","Any","Any"}
		# ttk.OptionMenu(frame, self.side_, *sorted(l)).grid(sticky="w",column=col+1,row=row)


		# ttk.Label(frame, text="Listed?").grid(sticky="w",column=col+2,row=row)
		# ttk.Checkbutton(frame, variable=self.listed_).grid(sticky="w",column=col+3,row=row)

		#print("algo time",algo_timer)

	def management_pannel(self,frame):



		self.stop = tk.DoubleVar()
		self.management_type = tk.StringVar()


		row = 2
		col = 1

		# ttk.Label(frame, text="Stop:").grid(sticky="w",column=col,row=row,padx=10)
		# ttk.Entry(frame, textvariable=self.stop).grid(sticky="w",column=col,row=row+1,padx=10)

		# col += 1
		ttk.Label(frame, text="Management Type:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.OptionMenu(frame, self.management_type,self.management_options[0],*self.management_options).grid(sticky="w",column=col,row=row+1,padx=10)

	def confirmation_pannel(self,frame):

		self.status = ttk.Label(frame, text="Status:")
		self.status.grid(sticky="w",column=2,row=1,padx=10)

		tk.Button(frame, text="Place",width=15,command=self.send_algo).grid(padx=50,pady=15,row=1, column=1)#,command=self.rank


	def confirmation_pannel_pair(self,frame):

		self.status = ttk.Label(frame, text="Status:")
		self.status.grid(sticky="w",column=2,row=1,padx=10)

		tk.Button(frame, text="Place",width=15,command=self.send_algo).grid(padx=50,pady=15,row=1, column=1)#,command=self.rank




	def send_algo(self):


		#check, symbol, risk. type. timing / price, 

		try:
			symbol1 = self.symbol1.get().upper()
			symbol2 = self.symbol2.get().upper()

			symbol1share = self.symbol1_share.get()
			symbol2share = self.symbol2_share.get()

			#side = self.side.get()
			risk = self.algo_risk.get()

			type_ = self.type.get()
			#stop = self.stop.get()
			
			management = self.management_type.get()

			entryplan = ""

			support = 0
			resistence = 0

			# if type_=="Rightaway":
			# 	if side == "Long":
			# 		entryplan= "Instant Long"
			# 		support = stop
			# 	elif side =="Short":
			# 		entryplan= "Instant Short"
			# 		resistence = stop
			# else:
			# 	triggerprice = self.limit_price.get()

			# 	if side == "Long":
			# 		entryplan= "Target Long"
			# 		resistence = triggerprice
			# 		support = stop
			# 	elif side =="Short":
			# 		entryplan= "Target Short"
			# 		resistence = stop
			# 		support = triggerprice

			check = [symbol1,symbol2,symbol1share,symbol2share,risk,management]

			for i in check:
				if i =="" or i==0:

					self.status["text"]="error"
			#self.entries[entry][8]["command"]= lambda symbol=rank,side=side,open_=row['open'],stop_=rscore,risk_=self.algo_risk:self.send_algo(self,symbol,side,open_,stop_,risk_)
			

			#["New order",[" BreakUp",symbol,support-change,resistence,risk,{},"Notdeploy","TrendRider"]]
			if risk>0:

				new_order = {}

				new_order["type_name"] = "Pair"
				new_order["algo_name"]= "Manual Trade Pair"
				new_order["symbol1"] = symbol1
				new_order["symbol2"] = symbol2

				new_order["symbol1share"] = symbol1_share
				new_order["symbol2share"] = symbol2_share

				new_order["risk"] = risk
				new_order["management"] = management 

				new_order["symbol1_statistics"] = {}

				new_order["symbol2_statistics"] = {}

				new_order["support"] = support
				new_order["resistence"] = resistence
				new_order["immediate_deployment"]= True
				
				
				new_order["statistics"] = {}


				info = ["New order",new_order]

				#[entryplan,symbol,support,resistence,risk,{},"deploy",management]
				self.tnv_scanner.send_algo(info)

				self.status["text"]="Status: Algo placed"
		except Exception as e:
			print(e)
			self.status["text"]="Status: error"

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



class SinlgeTrade():
	def __init__(self,root,TNV_scanner):

		self.tnv_scanner = TNV_scanner
		self.buttons = []
		self.entries = []
		self.l = 1


		self.symbol = tk.StringVar()
		self.algo_risk = tk.DoubleVar(value=10)

		self.file = "signals/open_resersal_"+datetime.now().strftime("%m-%d")+".csv"

		self.side_options = ("Long", "Short")
		self.type_options = ("Rightaway","Target")
		self.management_options = ("1:2 Exprmntl","1:2 Wide","Fib Only","SemiManual","FullManual")

		self.algo_placed = []
		self.ts_location = 7


		self.listening = ttk.LabelFrame(root) 
		self.listening.place(relx=0,rely=0,relheight=1,relwidth=1)


		self.root = root
		self.recreate_labels_single(self.root)
		

		
		#self.update_entry(pd.read_csv("tttt.csv",index_col=0))

	def recreate_labels_single(self,frame):

		self.symbol_frame = ttk.LabelFrame(self.root,text="Trade Setup")
		self.symbol_frame.place(x=0, rely=0.01, relheight=0.1, relwidth=1)

		self.entry_frame = ttk.LabelFrame(self.root,text="Entry Setup")
		self.entry_frame.place(x=0, rely=0.11, relheight=0.1, relwidth=1)

		self.management_frame = ttk.LabelFrame(self.root,text="Management Setup")
		self.management_frame.place(x=0, rely=0.22, relheight=0.12, relwidth=1)

		self.confirm_frame = ttk.LabelFrame(self.root,text="Confirmation")
		self.confirm_frame.place(x=0, rely=0.32, relheight=0.12, relwidth=1)
		# self.root = ttk.LabelFrame(self.root,text="")
		# self.root.place(x=0, rely=0.12, relheight=0.8, relwidth=1)

		self.trade_pannel(self.symbol_frame)

		self.entry_pannel(self.entry_frame)

		self.management_pannel(self.management_frame)

		self.confirmation_pannel(self.confirm_frame)

		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

		self.status_code = {}
		self.status_num = 0

		self.l+=1

	def recreate_labels_pair(self,frame):

		self.symbol_frame = ttk.LabelFrame(frame,text="Trade Setup")
		self.symbol_frame.place(x=0, rely=0.01, relheight=0.1, relwidth=1)

		self.entry_frame = ttk.LabelFrame(frame,text="Entry Setup")
		self.entry_frame.place(x=0, rely=0.11, relheight=0.1, relwidth=1)

		self.management_frame = ttk.LabelFrame(frame,text="Management Setup")
		self.management_frame.place(x=0, rely=0.22, relheight=0.12, relwidth=1)

		self.confirm_frame = ttk.LabelFrame(frame,text="Confirmation")
		self.confirm_frame.place(x=0, rely=0.32, relheight=0.12, relwidth=1)
		# self.root = ttk.LabelFrame(self.root,text="")
		# self.root.place(x=0, rely=0.12, relheight=0.8, relwidth=1)

		self.trade_pannel(self.symbol_frame)

		self.entry_pannel(self.entry_frame)

		self.management_pannel(self.management_frame)

		self.confirmation_pannel(self.confirm_frame)

		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

		self.status_code = {}
		self.status_num = 0

		self.l+=1


	def trade_pannel(self,frame):

		row = 1
		col = 1
		ttk.Label(frame, text="Symbol:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Entry(frame, textvariable=self.symbol).grid(sticky="w",column=col,row=row+1,padx=10)


		col +=1
		ttk.Label(frame, text="Risk:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Entry(frame, textvariable=self.algo_risk).grid(sticky="w",column=col,row=row+1,padx=10)

	def entry_pannel(self,frame):

		self.side = tk.StringVar()
		self.type = tk.StringVar()

		self.limit_price = tk.DoubleVar()


		self.side.set("Long")
		self.type.set("Rightaway")


		row = 2
		col = 1


		ttk.Label(frame, text="Side:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.OptionMenu(frame, self.side,self.side_options[0],*self.side_options).grid(sticky="w",column=col,row=row+1,padx=10)

		col += 1
		ttk.Label(frame, text="Type:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.OptionMenu(frame, self.type,self.type_options[0],*self.type_options).grid(sticky="w",column=col,row=row+1,padx=10)

		col += 1
		ttk.Label(frame, text="Limit Price (If applicable):").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Entry(frame, textvariable=self.limit_price).grid(sticky="w",column=col,row=row+1,padx=10)


		
		# row = 4
		# col = 1

		# ttk.Label(frame, text="Side:").grid(sticky="w",column=col,row=row)
		# l={"Up","Down","Any","Any"}
		# ttk.OptionMenu(frame, self.side_, *sorted(l)).grid(sticky="w",column=col+1,row=row)


		# ttk.Label(frame, text="Listed?").grid(sticky="w",column=col+2,row=row)
		# ttk.Checkbutton(frame, variable=self.listed_).grid(sticky="w",column=col+3,row=row)

		#print("algo time",algo_timer)

	def management_pannel(self,frame):



		self.stop = tk.DoubleVar()
		self.management_type = tk.StringVar()


		row = 2
		col = 1

		ttk.Label(frame, text="Stop:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Entry(frame, textvariable=self.stop).grid(sticky="w",column=col,row=row+1,padx=10)

		col += 1
		ttk.Label(frame, text="Management Type:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.OptionMenu(frame, self.management_type,self.management_options[0],*self.management_options).grid(sticky="w",column=col,row=row+1,padx=10)

	def confirmation_pannel(self,frame):

		self.status = ttk.Label(frame, text="Status:")
		self.status.grid(sticky="w",column=2,row=1,padx=10)

		tk.Button(frame, text="Place",width=15,command=self.send_algo).grid(padx=50,pady=15,row=1, column=1)#,command=self.rank


	def confirmation_pannel_pair(self,frame):

		self.status = ttk.Label(frame, text="Status:")
		self.status.grid(sticky="w",column=2,row=1,padx=10)

		tk.Button(frame, text="Place",width=15,command=self.send_algo).grid(padx=50,pady=15,row=1, column=1)#,command=self.rank




	def send_algo(self):


		#check, symbol, risk. type. timing / price, 

		try:
			symbol = self.symbol.get().upper()
			side = self.side.get()
			risk = self.algo_risk.get()

			type_ = self.type.get()
			stop = self.stop.get()
			
			management = self.management_type.get()
			entryplan = ""

			support = 0
			resistence = 0

			if type_=="Rightaway":
				if side == "Long":
					entryplan= "Instant Long"
					support = stop
				elif side =="Short":
					entryplan= "Instant Short"
					resistence = stop
			else:
				triggerprice = self.limit_price.get()

				if side == "Long":
					entryplan= "Target Long"
					resistence = triggerprice
					support = stop
				elif side =="Short":
					entryplan= "Target Short"
					resistence = stop
					support = triggerprice

			check = [symbol,side,risk,type_,stop,management]

			for i in check:
				if i =="" or i==0:

					self.status["text"]="error"
			#self.entries[entry][8]["command"]= lambda symbol=rank,side=side,open_=row['open'],stop_=rscore,risk_=self.algo_risk:self.send_algo(self,symbol,side,open_,stop_,risk_)
			

			#["New order",[" BreakUp",symbol,support-change,resistence,risk,{},"Notdeploy","TrendRider"]]
			if risk>0:

				new_order = {}

				new_order["type_name"] = "Single"
				new_order["algo_name"]= "Manual Trade"
				new_order["entry_type"] = entryplan
				new_order["symbol"] = symbol
				new_order["side"] = side
				new_order["support"] = support
				new_order["resistence"] = resistence
				new_order["immediate_deployment"]= True
				new_order["management"] = management 
				new_order["risk"] = risk
				new_order["statistics"] = {}


				info = ["New order",new_order]

				#[entryplan,symbol,support,resistence,risk,{},"deploy",management]
				self.tnv_scanner.send_algo(info)

				self.status["text"]="Status: Algo placed"
		except Exception as e:
			print(e)
			self.status["text"]="Status: error"

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



if __name__ == '__main__':

	root = tk.Tk() 
	root.title("TFM") 
	root.geometry("640x840")

	TFM(root,None)

	root.mainloop()

