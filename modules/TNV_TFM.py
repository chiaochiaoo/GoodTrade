import tkinter as tk                     
from tkinter import ttk 
import threading
import pandas as pd
import time
from datetime import datetime
import requests
import numpy as np
import threading

#from pannel import *
#from modules.pannel import *

from tkinter import *

try:
	from modules.pair_processing import *
except:
	from pair_processing import *

try:
	from scipy.stats import pearsonr
	#import numpy as np
except ImportError:
	import pip
	pip.main(['install', 'scipy'])
	from scipy.stats import pearsonr


try:
	import mplfinance as mpf
	#import numpy as np
except ImportError:
	import pip
	pip.main(['install', 'mplfinance'])
	import mplfinance as mpf




TRADETYPE = "Trade_type="
ALGOID ="Algo_id="
ALGONAME ="Algo_name="
SYMBOL = "Symbol="
ENTRYPLAN = "Entry_type="
SUPPORT = "Support="
RESISTANCE = "Resistance="
RISK =  "Risk="
SIDE =  "Side="
DEPLOY = "Deploy="
MANAGEMENT = "Management="


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

		self.pair_number = tk.DoubleVar(value=1)


		self.s1ratio=0
		self.s2ratio=0

		self.symbol1_share = tk.IntVar()
		self.symbol2_share = tk.IntVar()

		self.risk_per_share = tk.DoubleVar(value=1)

		self.xr = 0
		self.yr = 0
		self.cor = 0

		self.hedge_ratio = tk.StringVar()
		self.hedge_stability = tk.StringVar()
		self.correlation = tk.StringVar()
		self.correlation_stability = tk.StringVar()

		self.expected_risk = tk.StringVar()

		#self.standard_risk = tk.StringVar()

		self.algo_risk = tk.DoubleVar(value=0)

		self.pair_number.trace('w',  lambda *_ : self.recompute_total_risk())
		self.risk_per_share.trace('w',  lambda *_ : self.recompute_total_risk())
		

		self.file = ""#"signals/open_resersal_"+datetime.now().strftime("%m-%d")+".csv"

		self.side_options = ("Long", "Short")
		self.type_options = ("Rightaway","Target")
		self.management_options = ("1:2 Exprmntl","Market Making","Fib Only","SemiManual","FullManual","MarketMaking")

		self.algo_placed = []
		self.ts_location = 7


		self.listening = ttk.LabelFrame(root) 
		self.listening.place(relx=0,rely=0,relheight=1,relwidth=1)


		self.root = root
		self.recreate_labels_single(self.root)
		

		
		#self.update_entry(pd.read_csv("tttt.csv",index_col=0))

	def recompute_total_risk(self):
		try:
			self.algo_risk.set(float(self.risk_per_share.get()*self.pair_number.get()))
		except:
			pass
	def recreate_labels_single(self,frame):

		self.symbol_frame = ttk.LabelFrame(self.root,text="Trade Setup")
		self.symbol_frame.place(x=0, rely=0.01, relheight=0.25, relwidth=0.5)


		self.info_frame = ttk.LabelFrame(self.root,text="Info")
		self.info_frame.place(relx=0.5, rely=0.01, relheight=0.25, relwidth=0.5)


		self.entry_frame = ttk.LabelFrame(self.root,text="Entry Setup")
		self.entry_frame.place(x=0, rely=0.26, relheight=0.1, relwidth=1)

		self.management_frame = ttk.LabelFrame(self.root,text="Management Setup")
		self.management_frame.place(x=0, rely=0.37, relheight=0.12, relwidth=1)

		self.confirm_frame = ttk.LabelFrame(self.root,text="Confirmation")
		self.confirm_frame.place(x=0, rely=0.47, relheight=0.12, relwidth=1)
		# self.root = ttk.LabelFrame(self.root,text="")
		# self.root.place(x=0, rely=0.12, relheight=0.8, relwidth=1)

		self.info_pannel(self.info_frame)
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


	def info_pannel(self,frame):

		row = 1
		col = 1
		ttk.Label(frame, text="Hedge Ratio:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Label(frame,textvariable=self.hedge_ratio).grid(sticky="w",column=col+1,row=row,padx=10)
		row += 1
		#col = 1
		ttk.Label(frame, text="Ratio Stability:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Label(frame,textvariable=self.hedge_stability).grid(sticky="w",column=col+1,row=row,padx=10)

		row += 1
		#col = 1
		ttk.Label(frame, text="Correlation:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Label(frame,textvariable=self.correlation).grid(sticky="w",column=col+1,row=row,padx=10)

		row += 1
		#col = 1
		ttk.Label(frame, text="Correlation stb:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Label(frame,textvariable=self.correlation_stability).grid(sticky="w",column=col+1,row=row,padx=10)

		row += 1
		#col = 1
		ttk.Label(frame, text="15MIN Expected Return:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Label(frame,textvariable=self.expected_risk).grid(sticky="w",column=col+1,row=row,padx=10)

		row += 1
		x= ttk.Label(frame, text="Total Risk:")
		x.grid(sticky="w",column=col,row=row,padx=10)
		x["background"] = "yellow"
		ttk.Label(frame,textvariable=self.algo_risk).grid(sticky="w",column=col+1,row=row,padx=10)


	def trade_pannel(self,frame):

		row = 1
		col = 1
		ttk.Label(frame, text="Symbol1:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Entry(frame, textvariable=self.symbol1).grid(sticky="w",column=col,row=row+1,padx=10)

		col +=1

		ttk.Label(frame, text="Symbol2:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Entry(frame, textvariable=self.symbol2).grid(sticky="w",column=col,row=row+1,padx=10)


		# self.symbol1 = tk.StringVar()
		# self.symbol2 = tk.StringVar()
		# self.symbol1_share = tk.IntVar()
		# self.symbol2_share = tk.IntVar()
		row +=2

		col = 1

		
		ttk.Label(frame, text="Pair Amount:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Entry(frame, textvariable=self.pair_number).grid(sticky="w",column=col,row=row+1,padx=10)

		# col +=1
		# ttk.Label(frame, text="Symbol2 Share:").grid(sticky="w",column=col,row=row,padx=10)
		# ttk.Entry(frame, textvariable=self.symbol2_share).grid(sticky="w",column=col,row=row+1,padx=10)



		#row +=2
		col += 1

		ttk.Label(frame, text="Risk per pair:").grid(sticky="w",column=col,row=row,padx=10)
		ttk.Entry(frame, textvariable=self.risk_per_share).grid(sticky="w",column=col,row=row+1,padx=10)

		col = 1
		row +=2
		tk.Button(frame, text="Check",width=15,command=self.button).grid(row=row+1, column=col)#,command=self.rank

		col +=1
		tk.Button(frame, text="Plot",width=15,command=self.plot).grid(row=row+1, column=col)#,command=self.rank

	def button(self):

		reg = threading.Thread(target=self.info_set,args=(), daemon=True)
		reg.start()

	def plot(self):

		symbol1,symbol2 = self.symbol1.get(),self.symbol2.get()

		try:
			draw_pair(symbol1,symbol2,self.xr,self.yr)
		except Exception as e:
			print("ploting issue",e)
		# reg = threading.Thread(target=draw_pair,args=(symbol1,symbol2,self.xr,self.yr), daemon=True)
		# reg.start()

	def info_set(self):

		d=hedge_ratio(self.symbol1.get(),self.symbol2.get())
		self.hedge_ratio.set(str(d["hedgeratio"]))

		self.s1ratio = d["hedgeratio"][0]
		self.s2ratio = d["hedgeratio"][1]

		self.hedge_stability.set(str(d["hedgeratio_stability"]))
		self.correlation.set(str(d["correlation_score"]))
		self.correlation_stability.set(str(d["correlation_stability"]))

		self.expected_risk.set(str(d["15M_expected_risk"]))

		self.xr = d["hedgeratio"][0]
		self.yr = d["hedgeratio"][1]
		self.cor=d["correlation_score"]

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
		now = datetime.datetime.now()
		ts = now.hour*60+now.minute+now.second
		try:
			symbol1 = self.symbol1.get().upper()
			symbol2 = self.symbol2.get().upper()

			symbol1share = self.symbol1_share.get()
			symbol2share = self.symbol2_share.get()

			ratio = (self.s1ratio,self.s2ratio)
			pair = self.pair_number.get()

			#side = self.side.get()
			risk = self.algo_risk.get()

			type_ = self.type.get()
			#stop = self.stop.get()

			sigma = float(self.expected_risk.get())
			
			management = self.management_type.get()

			entryplan = ""

			support = 0
			resistence = 0


			check = [symbol1,symbol2,ratio,pair,risk,management]

			for i in check:
				if i =="" or i==0:

					self.status["text"]="error"
			#self.entries[entry][8]["command"]= lambda symbol=rank,side=side,open_=row['open'],stop_=rscore,risk_=self.algo_risk:self.send_algo(self,symbol,side,open_,stop_,risk_)
			

			#["New order",[" BreakUp",symbol,support-change,resistence,risk,{},"Notdeploy","TrendRider"]]
			if risk>0:

				new_order = {}

				new_order["algo_id"] = "Manual"+"_"+symbol1+symbol2+str(ts)
				new_order["type_name"] = "Pair"
				new_order["algo_name"]= "Manual Trade Pair"
				new_order["symbol1"] = symbol1
				new_order["symbol2"] = symbol2

				new_order["ratio"] = ratio
				new_order["share"] = pair

				new_order["sigma"] = sigma
				new_order["risk"] = risk
				new_order["management"] = management 

				new_order["symbol1_statistics"] = {}

				new_order["symbol2_statistics"] = {}

				new_order["support"] = support
				new_order["resistence"] = resistence
				new_order["immediate_deployment"]= True
				
				
				new_order["statistics"] = {}


				info = ["New order",new_order]

				print(info)
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

		self.file = ""#"signals/open_resersal_"+datetime.now().strftime("%m-%d")+".csv"

		self.side_options = ("Long", "Short")
		self.type_options = ("Rightaway","Target")
		self.management_options = ("1:2 Exprmntl","1:2 Wide","Fib Only","SemiManual","FullManual","MarketMaking")

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
		now = datetime.datetime.now()
		ts = now.hour*60+now.minute+now.second

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


				new_order["algo_id"]= "Manual"+"_"+symbol+str(ts)

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

				strs = [TRADETYPE,ALGOID,ALGONAME,SYMBOL,ENTRYPLAN,SUPPORT,RESISTANCE,RISK,SIDE,DEPLOY,MANAGEMENT]

				vals = ["Single",new_order["algo_id"],new_order["algo_name"],new_order["symbol"],new_order["entry_type"],new_order["support"],new_order["resistence"],new_order["risk"],new_order["side"],"T",new_order["management"]]


				msg = "http://localhost:4441/"	

				for i in range(len(strs)):

					msg+=strs[i]+str(vals[i])+","

				print("HTTP REQUEST:",msg)
				#[entryplan,symbol,support,resistence,risk,{},"deploy",management]
				#self.tnv_scanner.send_algo(info)

				requests.get(msg)


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




def get_min(time_str):
	"""Get Seconds from time."""

	h, m= time_str.split(':')

	ts = int(h) * 60 + int(m)

	return ts

if __name__ == '__main__':

	root = tk.Tk() 
	root.title("TFM") 
	root.geometry("640x840")

	PairTrade(root,None)

	# symbol1 = "JETS.AM"
	# symbol2 = "SPY.AM"
	# print(hedge_ratio(symbol1,symbol2))

	root.mainloop()

