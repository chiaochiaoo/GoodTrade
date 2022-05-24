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

class Spread():
	def __init__(self,root,NT,TNV_scanner):

		self.algo_name = "Spread"
		self.tnv_scanner = TNV_scanner
		self.buttons = []
		self.entries = []
		self.l = 1
		self.NT = NT
		self.labels_width = [9,10,5,8,8,5,5,5,5,8,5,5,5,5,8,6,6,6,6]
		self.labels = ["Pairs","Ratio","COR","Avg move","OH","OH Max","OL","OL Max","15-Avg  σ"]

		self.management = tk.StringVar(value="1:2 Exprmntl")

		self.algo_risk = tk.DoubleVar(value=10)
		self.algo_activate = tk.BooleanVar(value=False)


		#conditional box
		self.momentum_trade = tk.BooleanVar(value=True)
		self.reversal_trade = tk.BooleanVar(value=True)

		##############################
		self.data = None #pd.read_csv("current.csv")

		#m=self.reversal_trade .trace('w', lambda *_, data=self.data,: self.just_update_view(data))

		#self.fade = tk.BooleanVar(value=0)


		self.algo_placed = []
		self.ts_location = 7
		self.root = root


		self.hour = tk.IntVar(value=9)
		self.minute = tk.IntVar(value=29)

		self.ehour = tk.IntVar(value=9)
		self.eminute = tk.IntVar(value=35)

		self.rel_v = tk.DoubleVar(value=0)
		self.re_score = tk.DoubleVar(value=0)


		self.recreate_labels(self.root)

		self.name = "Breakout"
		self.toggle  = True

		

		#data = pd.read_csv("pair_test.csv")

		#self.update_entry(pd.read_csv("pair_test.csv",index_col=0))

		#self.file = "signals/open_resersal_"+datetime.now().strftime("%m-%d")+".csv"

		#self.update_entry(pd.read_csv("df_pair.csv",index_col=0))

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

		management = self.management.get()
		
		now = datetime.now()
		ts = now.hour*60+now.minute

		deployment=True
		if ts>=570:
			deployment = True
		else:
			deployment = False
			
		if risk>0:

			change = 0.03
			
			if support>10 and support<20:
				change = 0.06

			if support >20:
				change = 0.08


			if side =="UP":


				new_order = {}

				new_order["type_name"] = "Single"

				new_order["algo_id"]= self.name+"_"+symbol
				new_order["algo_name"]= self.algo_name

				new_order["entry_type"] = " BreakUp"
				new_order["symbol"] = symbol#lst[i]["symbol"]
				new_order["side"] = "Long"
				new_order["support"] = support -change#lst[i]["support"]
				new_order["resistence"] = resistence #lst[i]["resistence"]
				new_order["immediate_deployment"]= deployment
				new_order["management"] = management 
				new_order["risk"] = risk
				new_order["statistics"] = {}

				info = ["New order",new_order]
				#print("sending",info)
			else:

				new_order = {}
				new_order["type_name"] = "Single"

				new_order["algo_id"]= self.name+"_"+symbol
				new_order["algo_name"]= self.algo_name

				new_order["entry_type"] = " BreakDn"
				new_order["symbol"] = symbol
				new_order["side"] = "Short"
				new_order["support"] = support
				new_order["resistence"] = resistence + change
				new_order["immediate_deployment"]= deployment
				new_order["management"] = management 
				new_order["risk"] = risk
				new_order["statistics"] = {}

				info = ["New order",new_order]

			self.tnv_scanner.send_algo(info)


	def send_group_algos(self,lst):


		risk = self.algo_risk.get()
		management = self.management.get()
		
		order = ["New order"]

		#print("PMB HELLO",risk)
		if risk>0:

			#print("PMB HELLO2",lst)
			for i in range(len(lst)):

				new_order = {}

				# order["algo_name"] = "PairReversal"
				# order["algo_id"] = order["algo_name"]+order['symbol1']+order["symbol2"]
				# order['ratio'] = row['hedgeratio']
				# order['risk_per_pair'] = ycr*(mh-ph)

				new_order["algo_id"] = lst[i]["algo_id"] #"Manual"+"_"+symbol1+symbol2+str(ts)
				new_order["type_name"] = "Pair"
				new_order["algo_name"]= lst[i]["algo_name"]
				new_order["symbol1"] = lst[i]["symbol1"]
				new_order["symbol2"] = lst[i]["symbol2"]

				new_order["ratio"] = lst[i]["ratio"]

				new_order["share"] = risk//lst[i]['risk_per_pair']



				new_order["risk"] = risk
				new_order["management"] = management 

				new_order["symbol1_statistics"] = {}

				new_order["symbol2_statistics"] = {}

				new_order["support"] = 0
				new_order["resistence"] = 0
				new_order["immediate_deployment"]= True
				
				
				new_order["statistics"] = {}


				order.append(new_order)


			#print("sending order",order)
			self.tnv_scanner.send_algo(order)

	def algo_pannel(self,frame):

		row = 1
		col = 1
		ttk.Label(frame, text="Algo:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(frame, variable=self.algo_activate).grid(sticky="w",column=col+1,row=row)

		ttk.Label(frame, text="Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(frame, textvariable=self.algo_risk).grid(sticky="w",column=col+3,row=row)

		ttk.Label(frame, text="Management:").grid(sticky="w",column=col+4,row=row)
		ttk.OptionMenu(frame, self.management,*("","1:2 Exprmntl","FullManual","SemiManual","TrendRider")).grid(sticky="w",column=col+5,row=row)

		row = 2
		col = 1


		ttk.Label(frame, text="Deploy at:").grid(sticky="w",column=col,row=row)
		ttk.Entry(frame, textvariable=self.hour).grid(sticky="w",column=col+1,row=row)

		ttk.Label(frame, text=":").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(frame, textvariable=self.minute).grid(sticky="w",column=col+3,row=row)




		row = 3
		col = 1
		ttk.Label(frame, text="Algos:").grid(sticky="w",column=col,row=row)
		###
		row = 4
		col = 1
		ttk.Label(frame, text="Momentum").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(frame, variable=self.momentum_trade).grid(sticky="w",column=col+1,row=row)


		row = 4
		col = 3
		ttk.Label(frame, text="Reversal").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(frame, variable=self.reversal_trade).grid(sticky="w",column=col+1,row=row)




	def create_entry(self):

		for k in range(0,30):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				
				if i == 9:
					self.b = tk.Button(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				elif i ==9:
					self.b = tk.Button(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				else:
					self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
				# if i == 9:
				# 	self.b.grid_remove()
			self.l+=1


	#def deploy_now(self):

	def just_update_view(self,data):

		#if not self.data==None:

		try:
			data = self.filtering(data)

			self.just_update(data)
		except Exception as  e:
			print(e,"filtering issue")


	def filtering(self,data):

		# if self.reversal_trade.get()== True:
		# 	data =  data.loc[((data["ycr"]>=0.75)|(data["ycr"]<=0.25))]
			

		return data

#		self.labels = 

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		self.data = data


		now = datetime.now()
		ts = now.hour*60+now.minute
		
		algo_timer = self.hour.get()*60 + self.minute.get()

		end_timer = self.ehour.get()*60 + self.eminute.get()

		df = self.filtering(data)

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
					sec = str(row['hedgeratio'])
					sc = row['correlation_score']
					relv = row['correlation_stability']
					ycr = row['day_avg_move']
					ph = round(row['OH eval'],2)
					pl = round(row['OL eval'],2)

					mh = round(row['OH max'],2)
					ml = round(row['OL max'],2)
					pr = row['15_avg_sigma_per_pair']



					############ add since, and been to the thing #############

					#print(self.NT.nasdaq_trader_symbols)
					if 1: #score>0:	

						lst = [rank,sec,sc,ycr,ph,mh,pl,ml,pr]

						ts_location = 7

						for i in range(len(lst)):
							self.entries[entry][i]["text"] = lst[i]


							if self.algo_activate.get()==1 and self.reversal_trade.get()==1:
								if rank not in self.algo_placed:


									if (mh-ph)>= 0.15 and mh>=1:

										order = {}
										split = rank.split(',')
										order['symbol1'],order["symbol2"] = row['symbol1_ticker'],row['symbol2_ticker']

										order["algo_name"] = "PairReversal"
										order["algo_id"] = order["algo_name"]+order['symbol1']+order["symbol2"]
										order['ratio'] = row['hedgeratio']
										order['risk_per_pair'] = ycr*(mh-ph)

										send_algo.append(order)
										self.algo_placed.append(rank)
									elif (ml-pl)>= 0.15 and ml>=1:

										order = {}
										split = rank.split(',')
										order['symbol1'],order["symbol2"] = row['symbol2_ticker'],row['symbol1_ticker']
										order["algo_name"] = "PairReversal"
										order["algo_id"] = order["algo_name"]+order['symbol1']+order["symbol2"]

										order['ratio'] = row['hedgeratio']
										order['risk_per_pair'] = ycr*(ml-pl)
										send_algo.append(order)
										self.algo_placed.append(rank)
						entry+=1
						if entry ==30:
							break

				while entry<30:
					#print("ok")
					for i in range(5):
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

	def update_entry2(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		if self.toggle:
			self.labels = ["Symbol","Sector","F5E","F5VE","Rel.V","SC","SO","Prange","Listed","Toggle","Add"]

			for i in range(len(self.buttons)):
				self.buttons[i]["text"] = self.labels[i]

			self.toggle  = False


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
					#["Symbol","Sector","F5E","F5VE","Rel.V","SC","SO","Prange","Listed","Toggle","Add"]
					rank = index
					sec = row['sector']
					f5r = row['f5r']
					f5v = row['f5v']
					relv = row['rrvol']
					
					sc = row['SC']
					so = row['SO']
					pr = row['prange']

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

						lst = [rank,sec,f5r,f5v,relv,sc,so,pr,listed]

						ts_location = 7

						for i in range(len(lst)):
							self.entries[entry][i]["text"] = lst[i]

							#self.entries[entry][9].grid_remove() 	

							# if lst[ts_location] >=ts and lst[ts_location]>=algo_timer and lst[ts_location]<=end_timer:
							# 	self.entries[entry][i]["background"] = "LIGHTGREEN"
							# 	self.entries[entry][8].grid()

							if sc>0:
								side = "UP"
							else:
								side = "DOWN"
							support = row['pl']
							resistence = row['ph']

							#self.entries[entry][9]["command"]= lambda symbol=rank,support=support,side=side,resistence=resistence:self.send_algo(symbol,support,resistence,side)


							# if self.algo_activate.get()==1 and ts>=algo_timer and ts<=end_timer:
							# 	if rank not in self.algo_placed:

							# 		#self.send_algo(rank,support,resistence,self.algo_risk)
							# 		self.algo_placed.append(rank)

							# 		order = {}

							# 		order["symbol"] = rank
							# 		order["support"] = support
							# 		order["resistence"] = resistence

							# 		order["side"] = side

							# 		send_algo.append(order)


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

class fake_NT():

	def __init__(self):

		self.nasdaq_trader_symbols_ranking=[]

if __name__ == '__main__':

	root = tk.Tk() 
	root.title("GoodTrade v489") 
	root.geometry("640x840")

	#print(ratio_compute(0.8))
	#print(ratio_compute(1.2))

	Spread(root,fake_NT(),None)

	root.mainloop()
