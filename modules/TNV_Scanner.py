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


# from TNV_PMB import *
# from TNV_TFM import *
# from TNV_StandardScanner import *


#from TNV_Trend import *
#from TNV_OR import *

try:
	from modules.TNV_Spread import *
	from modules.TNV_PMB import *
	from modules.TNV_TFM import *
	from modules.TNV_StandardScanner import *
except:
	from TNV_Spread import *
	from TNV_PMB import *
	from TNV_TFM import *
	from TNV_StandardScanner import *
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

		self.current_ts = 0
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


		self.today_frame = tk.Canvas(self.TNV_TAB)
		self.TNV_TAB.add(self.today_frame, text ='Custom Algo')
		self.custom_algo = Custom_Algo(self.today_frame,self)

		self.or_frame = tk.Canvas(self.TNV_TAB)
		self.TNV_TAB.add(self.or_frame, text ='Open Reversal')
		self.open_reversal = Open_Reversal(self.or_frame,NT,self)

		# PMB
		self.pmb_frame = tk.Canvas(self.TNV_TAB)
		self.TNV_TAB.add(self.pmb_frame, text ='PMB')
		self.pmb = Premarket_breakout(self.pmb_frame,NT,self)


		# # NH NL
		# self.nh_frame = tk.Canvas(self.TNV_TAB)
		# self.nl_frame = tk.Canvas(self.TNV_TAB)
		# self.TNV_TAB.add(self.nh_frame, text ='Near High')
		# self.TNV_TAB.add(self.nl_frame, text ='Near Low')
		# self.near_high = Near_high(self.nh_frame,NT)
		# self.near_low = Near_low(self.nl_frame,NT)

		# # JB 
		# self.vb_frame = tk.Canvas(self.TNV_TAB)
		# self.TNV_TAB.add(self.vb_frame, text ='Just Break')
		# self.volatility_scanner = Just_break(self.vb_frame,NT)

		# NH NL
		self.oh_frame = tk.Canvas(self.TNV_TAB)
		self.ol_frame = tk.Canvas(self.TNV_TAB)

		self.TNV_TAB.add(self.oh_frame, text ='Open High')
		self.TNV_TAB.add(self.ol_frame, text ='Open Low')
		self.oh = Open_high(self.oh_frame,NT,self)
		self.ol = Open_low(self.ol_frame,NT,self)

		# RRVOL
		self.rrvol_frame = tk.Canvas(self.TNV_TAB)
		self.TNV_TAB.add(self.rrvol_frame, text ='RRVol')
		self.rrvol = RRvol(self.rrvol_frame,NT)
 
		# self.trending_frame = tk.Canvas(self.TNV_TAB)
		# self.TNV_TAB.add(self.trending_frame, text ='Trending')
		# self.trending = ADX(self.trending_frame,NT,self)

		#Spread 
		self.spread_frame = tk.Canvas(self.TNV_TAB)
		self.TNV_TAB.add(self.spread_frame, text ='Spread')
		self.spread = Spread(self.spread_frame,NT,self)

		# # TFM
		self.TFM_frame = tk.Canvas(self.TNV_TAB)
		self.TNV_TAB.add(self.TFM_frame, text ='TFM')
		self.tfm = TFM(self.TFM_frame,self)


		# while True:
		# 	receiver = threading.Thread(target=self.update_entry,args=([filtered_df,"09:31"],),daemon=True)
		# 	receiver.start()
		# 	time.sleep(2)
		# 	print("New!")

		# filtered_df = pd.read_csv("current.csv",index_col=0)

		# self.update_entry([filtered_df,"09:31"])
		#self.update_entry()


		# receiver = threading.Thread(target=algo_server,args=() daemon=True)
		# receiver.start()

	def send_algo(self,msg):

		#print("recive,",msg)
		self.algo_commlink.send(msg)

	def color(self,vals,val):

		if val.get()[-4:]=="alse":
			vals["background"] = "red"
		elif val.get()[-4:]=="True":
			vals["background"] = "#97FEA8"


	def server_disconnection(self):

		pass 


	def http_order(self,data):

		self.custom_algo.http_order(data)

	def update_entry(self,data):

		now = datetime.now()
		
		system_ts = now.hour*60+now.minute 

		timestamp = data[1]

		ts= timestamp[:5]
		m,s=ts.split(":")
		m=int(m)
		s=int(s)
		ts=m*60+s

		#ts = timestamp[:]

		#print("package arrived at TNVscanner,",timestamp,"system time:",system_ts+1)


		#if it is not from the current minute or two, reject. 
		# if the package is old. skip.
		#if ts >=system_ts and timestamp!= self.current_ts:

		if 1:

			self.current_ts = timestamp
			self.NT_stat["text"] = "Last update: "+timestamp


			filtered_df = data[0]

			pair_df = data[3]

			#print("Current ts:",ts)

			#PB 
			#if ts<570:
			pb1 =  filtered_df.loc[(filtered_df["SC"]>=1)&(filtered_df["Market Cap"]<=4)&(filtered_df["price"]<=filtered_df["ph"])&(filtered_df["price"]>=filtered_df["pl"])]
			pb2 = filtered_df.loc[(filtered_df["SC"]<=-1)&(filtered_df["Market Cap"]<=4)&(filtered_df["price"]<=filtered_df["ph"])&(filtered_df["price"]>=filtered_df["pl"])]
			

			if len(pb1)+len(pb2)>25:

				#trim pb1 , pb2.
				pb = pd.concat([pb1,pb2])
				pb = pb.reindex(pb.SC.abs().sort_values(ascending=False).index)[:30]
				#print(pb)


			else:
				pb = pd.concat([pb1,pb2])
				#just add pb3.

			# pb1 = pb1.sort_values(by=["SC"],ascending=False)[:15]
			# pb2 = pb2.sort_values(by=["SC"],ascending=True)[:15]


			pb3 = filtered_df.loc[((filtered_df["SC"]<=-5)|(filtered_df["SC"]>=5))&(filtered_df["Market Cap"]==5)&(filtered_df["price"]>=5)&(filtered_df["price"]<=filtered_df["ph"])&(filtered_df["price"]>=filtered_df["pl"])][:10]
			pb = pd.concat([pb,pb3])

			pb = pb.reindex(pb.SC.abs().sort_values(ascending=False).index)[:35]

			# else:
			# 	pb = filtered_df.loc[(filtered_df["f5r"]>=1)&(filtered_df["Market Cap"]<=4)]
			# 	pb = pb.sort_values(by=["f5r"],ascending=False)[:20]


			### PRIORITIZE THE SPY500 ###
			### THEN THE LIST ####


			##################### NEAR LOW #############################
			at_low = filtered_df.loc[(filtered_df["rangescore"]<=0.1)][:20] #&&(filtered_df["last_break"])
			#at_low.to_csv("at low.csv")

			##################### NEAR HIGH #############################
			at_high = filtered_df.loc[(filtered_df["rangescore"]>=0.9)][:20]

			##################### Just break #############################
			just_break = filtered_df.loc[(filtered_df["just_break"]!="")&(filtered_df["break_span"]>=15)][:20]


			#reversalside is not null. shall not be nullified. only take the first reversal. 
			openreverse = filtered_df.loc[(filtered_df["reversal"]==True)&(filtered_df["Market Cap"]>0)&(filtered_df["reversalside"]!="")]
			openreverse = openreverse.sort_values(by=["reversal_timer"],ascending=False)[:20]
			

			# trending =  filtered_df.loc[(filtered_df["ema45time"]>=20)|(filtered_df["ema45time"]<=-20)]
			# trending =  trending.reindex(trending.ema45.abs().sort_values(ascending=False).index)[:20] #df.sort_values(by=["ema21"],ascending=False)

			# OH , OL, RRVOL

			#oh = filtered_df.loc[(filtered_df["oh"]>0.5)]
			#oh = filtered_df.loc[(filtered_df["ema21change"]<-20)]
			#oh = filtered_df.loc[(filtered_df["oh"]>0.5)].sort_values(by=["oh"],ascending=False)[:20]

			oh = pd.concat([filtered_df.loc[(filtered_df["ema45change"]<-20)&(filtered_df["oh"]>0.7)],filtered_df.loc[(filtered_df["oh"]>0.5)&(filtered_df["ema45change"]>-20)].sort_values(by=["oh"],ascending=False)[:30]])
			#oh = oh.loc[oh["Market Cap"]<5]
			#ol = filtered_df.loc[(filtered_df["ema21change"]>20)]
			# ol = filtered_df.loc[filtered_df["ol"]>0.5]
			# ol = ol.sort_values(by=["ol"],ascending=False)[:20]
			ol = pd.concat([filtered_df.loc[(filtered_df["ema45change"]>20)&(filtered_df["ol"]>0.7)],filtered_df.loc[(filtered_df["ol"]>0.5)&(filtered_df["ema45change"]<20)].sort_values(by=["ol"],ascending=False)[:30]])
			#ol = ol.loc[ol["Market Cap"]<5]
			rrvol = filtered_df.sort_values(by=["rrvol"],ascending=False)[:20]

			# self.volatility_scanner.update_entry(just_break)
			# self.near_low.update_entry(at_low)
			# self.near_high.update_entry(at_high)

			# if ts<570:
				
			# else:
			# 	self.pmb.update_entry2(pb)

			self.pmb.update_entry(pb)

			self.spread.update_entry(pair_df)
			self.open_reversal.update_entry(openreverse)
			# self.trending.update_entry(trending)
			
			self.oh.update_entry(oh)
			self.ol.update_entry(ol)
			self.rrvol.update_entry(rrvol)

			#print("package at TNVscanner fully processed,",timestamp)
		else:
			print("receiving old package.")

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

class Open_Reversal(StandardScanner):
	def __init__(self,root,NT,tnv):

		self.labels_width = [9,6,5,7,7,5,6,6,6,6,6,6,8,6,6,6,6]
		self.labels = ["Symbol","Sector","Rel.V","Side","Re.SCORE","SC%","Listed","Since","Add","Algo"]
		self.total_len = len(self.labels)
		self.tnv_scanner = tnv
		super().__init__(root,NT)

		self.ts_location = 7

		# self.hour.set(9)
		# self.minute.set(30)
		# self.ehour.set(10)
		# self.eminute.set(30)

		#self.update_entry(pd.read_csv("tttt.csv",index_col=0))



	def send_group_algos(self,lst):

		risk = self.algo_risk.get()

		#print("HELLO.",lst)
		order = ["New order"]

		management = self.management.get()
		if risk>0:
			for i in range(len(lst)):
				#print(lst[i]["symbol"],lst[i]["support"],lst[i]["resistence"])

				change = 0.03
			
				if lst[i]["support"]>10 and lst[i]["support"]<20:
					change = 0.05

				if lst[i]["support"] >20:
					change = 0.06


				if lst[i]["side"] =="UP":
					order.append(["BreakAny",lst[i]["symbol"],lst[i]["support"]-change,lst[i]["resistence"],risk,{},"deploy",management])

					#print("sending",info)
				else:
					order.append(["BreakAny",lst[i]["symbol"],lst[i]["support"],lst[i]["resistence"]+change,risk,{},"deploy",management])

			self.tnv_scanner.send_algo(order)


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
					relv = row['rrvol']
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

									resistence = row['price']
									support = row['open'] #+ 0.5*abs(row['price']-row['open'])
									
								else:
									
									resistence = row['open'] #- 0.5*abs(row['price']-row['open'])

									support = row['price']

								#self.entries[entry][9]["command"]= lambda symbol=rank,support=support,side=side,resistence=resistence:self.send_algo(symbol,support,resistence,side)

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
				# df.to_csv(self.file)
			# except Exception as e:
			# 	print("TNV scanner construction open reversal:",e)

			if len(send_algo)>0:
				self.send_group_algos(send_algo)

class Open_high(StandardScanner):
	def __init__(self,root,NT,tnv):

		self.labels_width = [9,6,5,8,5,5,6,6,6,6,6,6,8,6]
		self.labels = ["Symbol","Sector","OH","Rel.V","E45T","E45C","SO%","SC%","listed","Add"]
		self.total_len = len(self.labels)
		self.tnv_scanner = tnv
		super().__init__(root,NT)

		self.open = tk.BooleanVar(value=0)
		self.algo_activate.set(True)
		row = 3
		col = 5

		self.reversal_type = tk.StringVar(value="Both")
		# ttk.Label(self.algo_frame, text="OpenBreak:").grid(sticky="w",column=col,row=row)
		# ttk.Checkbutton(self.algo_frame, variable=self.open).grid(sticky="w",column=col+1,row=row)
		ttk.Label(self.algo_frame, text="Reversal Type:").grid(sticky="w",column=col,row=row)
		ttk.OptionMenu(self.algo_frame, self.reversal_type,*("","Both","Reversal Candle","EMA Break")).grid(sticky="w",column=col+1,row=row)

		self.openbreak = []


		self.algo_name = "Open_high"
		self.algo_name_fade = "Open_high_fade"
		self.algo_name_alternative = "Open_high_break"


	def update_entry(self,data):

		df = data


		#df.to_csv("tttt.csv")
		entry = 0
		threshold = 25

		now = datetime.now()
		ts = now.hour*60+now.minute

		algo_timer = self.hour.get()*60 + self.minute.get()
		end_timer = self.ehour.get()*60 + self.eminute.get()

		algo_timer = 0
		#print("fade:",self.fade.get())
		send_algo = []

		open_ = self.open.get()
		fade = self.fade.get()
		

		fast_reversal = False
		slow_reversal = False

		type_ = self.reversal_type.get()

		if type_=="Both":
			fast_reversal = True
			slow_reversal = True
		elif type_=="Reversal Candle":
			fast_reversal = True
			slow_reversal = False
		elif type_ =="EMA Break":
			fast_reversal = False
			slow_reversal = True

		if 1:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				sec = row['sector']
				relv = row['rrvol']

				# near = row['rangescore']
				# high = row['high']

				e21t = row['ema45time']
				e21c = row['ema45change']

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

					lst = [rank,sec,oh,relv,e21t,e21c,so,sc,listed]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

					trade = rank+str(ts)

					if trade not in self.algo_placed and self.algo_activate.get()==1 \
					and ts>=algo_timer and ts<=end_timer:

						send = False
						
						order = {}
						order["symbol"] = rank


						# if open_ and row["oh"]>0.5 and row["f5r"]>0.8 and relv>1.2 and ts<=700 and rank not in self.openbreak:   #hist_oh

						# 	order["support"] = row['open']	#- (row['high']-row['price'])
						# 	order["resistence"] = row['price']
						# 	order["side"] = "UP"

						# 	send=True
						# 	self.openbreak.append(rank)
						# 	self.algo_placed.append(trade)

						if fast_reversal and row['ema45time']>=25 and row['oh']>=0.5 and row['new_high_this_5']==True and row['prev_5_close_range'] <=0.25 and row['prev_5_close_eval']>1.3:

							if fade==True:
								order["support"] = row['price']	- row['hist_oh']*0.1 #(row['high']-row['price'])
								order["resistence"] = row['price']
								order["side"] = "UP"	

								order["algo_name"] = self.algo_name_fade
								order["algo_id"] = self.algo_name_fade + rank  +"_fast_"+ str(ts//90)
							else:
								order["support"] = row['price']	 
								order["resistence"] = row['high']+ (row['hist_oh']*0.1)
								order["side"] = "DOWN"	

								order["algo_name"] = self.algo_name
								order["algo_id"] = self.algo_name + rank   +"_fast_"+ str(ts//90)
							send=True
							self.algo_placed.append(trade)

						if slow_reversal and row['ema45change']<=-25 and row['oh']>=1:


							if fade==True:
								order["support"] = row['price']	- (row['high']-row['price'])
								order["resistence"] = row['price']
								order["side"] = "UP"	

								order["algo_name"] = self.algo_name_fade
								order["algo_id"] = self.algo_name_fade + rank  +"_slow_"+ str(ts//30)
							else:
								order["support"] = row['price']	 
								order["resistence"] = row['high'] + (row['hist_oh']*0.05)
								order["side"] = "DOWN"	

								order["algo_name"] = self.algo_name
								order["algo_id"] = self.algo_name + rank   +"_slow_"+  str(ts//30)

							self.algo_placed.append(trade)		
							send=True

						if slow_reversal and row['ema45change']<=-50 and row['oh']>=0.8:

							if fade==True:
								order["support"] = row['price']	- (row['high']-row['price'])
								order["resistence"] = row['price']
								order["side"] = "UP"	

								order["algo_name"] = self.algo_name_fade
								order["algo_id"] = self.algo_name_fade + rank  + str(ts//30)
							else:
								order["support"] = row['price']	
								order["resistence"] = row['high']  + (row['hist_oh']*0.025)
								order["side"] = "DOWN"

								order["algo_name"] = self.algo_name
								order["algo_id"] = self.algo_name + rank  + str(ts//30)

							self.algo_placed.append(trade)			
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

class Open_low(StandardScanner):
	def __init__(self,root,NT,tnv):

		
		self.labels_width = [9,6,5,8,5,5,6,6,6,6,6,6,8,6]
		self.labels = ["Symbol","Sector","OL","Rel.V","E45T","E45C","SO%","SC%","listed","Add"]
		self.total_len = len(self.labels)
		self.tnv_scanner = tnv
		super().__init__(root,NT)

		self.open = tk.BooleanVar(value=0)
		self.algo_activate.set(True)
		row = 3
		col = 5
		self.reversal_type = tk.StringVar(value="Both")
		# ttk.Label(self.algo_frame, text="OpenBreak:").grid(sticky="w",column=col,row=row)
		# ttk.Checkbutton(self.algo_frame, variable=self.open).grid(sticky="w",column=col+1,row=row)
		ttk.Label(self.algo_frame, text="Reversal Type:").grid(sticky="w",column=col,row=row)
		ttk.OptionMenu(self.algo_frame, self.reversal_type,*("","Both","Reversal Candle","EMA Break")).grid(sticky="w",column=col+1,row=row)

		self.openbreak = []

		self.algo_name = "Open_low"
		self.algo_name_fade = "Open_low_fade"
		self.algo_name_alternative = "Open_low_break"


	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		df = data


		#df.to_csv("tttt.csv")
		entry = 0

		now = datetime.now()
		ts = now.hour*60+now.minute

		algo_timer = self.hour.get()*60 + self.minute.get()
		end_timer = self.ehour.get()*60 + self.eminute.get()
		send_algo = []

		open_ = self.open.get()
		fade = self.fade.get()

		fast_reversal = False
		slow_reversal = False

		type_ = self.reversal_type.get()

		if type_=="Both":
			fast_reversal = True
			slow_reversal = True
		elif type_=="Reversal Candle":
			fast_reversal = True
			slow_reversal = False
		elif type_ =="EMA Break":
			fast_reversal = False
			slow_reversal = True

		if 1:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				sec = row['sector']
				relv = row['rrvol']
				# near = row['rangescore']
				# high = row['high']

				e21t = row['ema45time']
				e21c = row['ema45change']

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

					lst = [rank,sec,oh,relv,e21t,e21c,so,sc,listed]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]

					trade = rank+str(ts)

					if trade not in self.algo_placed and self.algo_activate.get()==1 and ts>=algo_timer and ts<=end_timer:

						send = False

						order = {}
						order["symbol"] = rank
						

						#print(trade,open_, row["ol"],row["f5r"],relv,ts,)
						# if open_ and row["ol"]>0.5 and row["f5r"]>0.5 and relv>0.5 and ts<=600 and rank not in self.openbreak:

						# 	order["support"] = 	row['price'] #- (row['high']-row['price'])
						# 	order["resistence"] =  row['open']
						# 	order["side"] = "DOWN"
						# 	send=True

						# 	self.openbreak.append(rank)
						# 	self.algo_placed.append(trade)

						if fast_reversal and row['ema45time']<=-25 and row['ol']>=0.5 and row['new_high_this_5']==True and row['prev_5_close_range'] >=0.75 and row['prev_5_close_eval']>1.3:

							if fade==True:
								order["support"] =  row['price']	 
								order["resistence"] = row['price'] +  row['hist_ol']*0.1  #(row['price']-row['low'])
								order["side"] = "DOWN"

								order["algo_name"] = self.algo_name_fade
								order["algo_id"] = self.algo_name_fade +"_fast_"+ rank[:-3]  + str(ts//90)

							else:	
								order["support"] = row['low'] -  row['hist_ol']*0.1
								order["resistence"] = row['price']	
								order["side"] = "UP"			

								order["algo_name"] = self.algo_name
								order["algo_id"] = self.algo_name + "_fast_" + rank[:-3]  + str(ts//90)
							send=True
							self.algo_placed.append(trade)

						if slow_reversal and row['ema45change']>=25 and row['ol']>=0.5:

							if fade==True:
								order["support"] =  row['price']	 
								order["resistence"] = row['price'] + (row['price']-row['low'])
								order["side"] = "DOWN"

								order["algo_name"] = self.algo_name_fade
								order["algo_id"] = self.algo_name_fade +"_slow_"+ rank[:-3]  + str(ts//30)

							else:	
								order["support"] = row['low'] -  row['hist_ol']*0.1  #0.03	
								order["resistence"] = row['price']	
								order["side"] = "UP"			

								order["algo_name"] = self.algo_name
								order["algo_id"] = self.algo_name + "_slow_" + rank[:-3]  + str(ts//30)
							send=True
							self.algo_placed.append(trade)

						if slow_reversal and row['ema45change']>=50 and row['ol']>=1:


							if fade==True:
								order["support"] =  row['price']	 
								order["resistence"] = row['price'] + (row['price']-row['low'])
								order["side"] = "DOWN"

								order["algo_name"] = self.algo_name_fade
								order["algo_id"] = self.algo_name_fade +"_slow_"+ rank[:-3]  + str(ts//30)

							else:	
								order["support"] = row['low'] -  row['hist_ol']*0.1
								order["resistence"] = row['price']	
								order["side"] = "UP"	

								order["algo_name"] = self.algo_name
								order["algo_id"] = self.algo_name +"_slow_" + rank[:-3]  + str(ts//30)		
							send=True
							self.algo_placed.append(trade)

		
						if send:
							send_algo.append(order)

				entry+=1
				if entry ==50:
					break
			while entry<50:
				#print("ok")
				for i in range(self.total_len):
					self.entries[entry][i]["text"] = ""
				entry+=1


		if len(send_algo)>0:
			self.send_group_algos(send_algo)
		# except Exception as e:
		# 	print("TNV scanner construction near high:",e)

class ADX(StandardScanner):
	def __init__(self,root,NT,TNV):

		
		self.labels_width = [9,6,12,5,8,5,6,6,6,6,6,6,8,6]

		self.labels = ["Symbol","Sector","TrendScore","Rg.Score","Rel.V","SO%","SC%","listed","Add"]
		self.tnv_scanner = TNV
		self.total_len = len(self.labels)
		super().__init__(root,NT)

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

def ratio_compute(n):

	if n<1:
		return str(int(100*n)) +":100"
	else:
		return "100:"+str(int(100/n)) 



class TodayTrade():

	def __init__(self,root,TNV_scanner):

		self.root = root 
		self.labels_width = [9,9,9]
		self.labels = ["Time","Algo","Symbol"]
		self.total_len = len(self.labels)
		self.tnv_scanner = TNV_scanner
		self.entries = []
		self.l=0

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

		self.l+=1
		self.create_entry()

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

		self.algo_frame = ttk.LabelFrame(self.root,text="Algo setup")
		self.algo_frame.place(x=0, rely=0, relheight=0.1, relwidth=1)


		self.algos = ttk.LabelFrame(self.root,text="Custom Algos / Risk multiplier")
		self.algos.place(x=0, rely=0.101, relheight=0.85, relwidth=1)

		self.tick_opening = tk.BooleanVar(value=0)
		self.tick_intraday_v1 = tk.BooleanVar(value=0)
		self.tick_intraday_v2 = tk.BooleanVar(value=0)


		self.market_long = tk.BooleanVar(value=0)
		self.market_short = tk.BooleanVar(value=0)


		self.corey1 = tk.BooleanVar(value=0)
		self.corey1_multiplier = tk.IntVar(value=1)
		self.corey2 = tk.BooleanVar(value=0)
		self.corey2_multiplier = tk.IntVar(value=1)
		self.corey3 = tk.BooleanVar(value=0)
		self.corey3_multiplier = tk.IntVar(value=1)


		self.bax1 = tk.BooleanVar(value=0)
		self.bax2 = tk.BooleanVar(value=0)
		self.bax3 = tk.BooleanVar(value=0)
		self.bax4 = tk.BooleanVar(value=0)
		self.bax5 = tk.BooleanVar(value=0)


		self.algo_pannel()

	def algo_pannel(self):

		row = 1
		col = 1
		ttk.Label(self.algo_frame, text="Algo:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algo_frame, variable=self.algo_activate).grid(sticky="w",column=col+1,row=row)

		ttk.Label(self.algo_frame, text="Basket Total Risk:").grid(sticky="w",column=col+2,row=row)
		ttk.Entry(self.algo_frame, textvariable=self.algo_risk).grid(sticky="w",column=col+3,row=row)


		row +=1

		ttk.Label(self.algo_frame, text="Toggle All:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algo_frame, variable=self.tick_opening).grid(sticky="w",column=col+1,row=row)


		row +=1

		ttk.Label(self.algos, text="Market Long:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algos, variable=self.market_long).grid(sticky="w",column=col+1,row=row)


		row +=1

		ttk.Label(self.algos, text="Market Short:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algos, variable=self.market_short).grid(sticky="w",column=col+1,row=row)


		row +=1

		ttk.Label(self.algos, text="TICK Long:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algos, variable=self.tick_intraday_v2).grid(sticky="w",column=col+1,row=row)

		row +=1

		ttk.Label(self.algos, text="TICK Short:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algos, variable=self.tick_intraday_v2).grid(sticky="w",column=col+1,row=row)



		row +=1

		ttk.Label(self.algos, text="Corey Dip Buy:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algos, variable=self.corey1).grid(sticky="w",column=col+1,row=row)

		ttk.Entry(self.algos, textvariable=self.corey1_multiplier).grid(sticky="w",column=col+2,row=row)

		row +=1

		ttk.Label(self.algos, text="Corey algo 2 :").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algos, variable=self.corey2).grid(sticky="w",column=col+1,row=row)

		ttk.Entry(self.algos, textvariable=self.corey2_multiplier).grid(sticky="w",column=col+2,row=row)


		row +=1

		ttk.Label(self.algos, text="Corey algo 3:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algos, variable=self.corey3).grid(sticky="w",column=col+1,row=row)

		ttk.Entry(self.algos, textvariable=self.corey3_multiplier).grid(sticky="w",column=col+2,row=row)

		row +=1

		ttk.Label(self.algos, text="BAX1:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algos, variable=self.bax1).grid(sticky="w",column=col+1,row=row)

		row +=1

		ttk.Label(self.algos, text="BAX2:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algos, variable=self.bax2).grid(sticky="w",column=col+1,row=row)

		row +=1

		ttk.Label(self.algos, text="BAX3:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algos, variable=self.bax3).grid(sticky="w",column=col+1,row=row)

		row +=1

		ttk.Label(self.algos, text="BAX4:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algos, variable=self.bax4).grid(sticky="w",column=col+1,row=row)

		row +=1

		ttk.Label(self.algos, text="BAX5:").grid(sticky="w",column=col,row=row)
		ttk.Checkbutton(self.algos, variable=self.bax5).grid(sticky="w",column=col+1,row=row)		# for k in range(0,30):

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

