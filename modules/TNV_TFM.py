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
		self.root = root
		self.recreate_labels(self.root)


		
		#self.update_entry(pd.read_csv("tttt.csv",index_col=0))

	def recreate_labels(self,frame):

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

				info = ["New order",[entryplan,symbol,support,resistence,risk,{},"deploy",management]]

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
				#df.to_csv(self.file)
			# except Exception as e:
			# 	print("TNV scanner construction open reversal:",e)

			if len(send_algo)>0:
				self.send_group_algos(send_algo)


if __name__ == '__main__':

	root = tk.Tk() 
	root.title("TFM") 
	root.geometry("640x840")

	TFM(root,None)

	root.mainloop()

