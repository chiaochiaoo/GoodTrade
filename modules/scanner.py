import tkinter as tk
from tkinter import ttk
import threading
import pandas as pd
import time

#from pannel import *
from modules.pannel import *
#from modules.scanner_process_manager import *
from datetime import datetime

from modules.TNV_Scanner import *
from tkinter import *


def status_change(var,label):
	label["text"] = "Current Status: "+var.get()

class scanner(pannel):

	def __init__(self,root,tickers_manager,scanner_process,data,scanner_request,algo_comm):

		super()

		self.data = data
		#mark if already created. if so, just update the infos. 
		self.nasdaq_trader_created = False

		self.symbols_registry = []

		self.nasdaq_trader_symbols = []
		#self.nasdaq_trader_list = {}
		self.nasdaq_trader_symbols_ranking = {}
		#self.nasdaq_trader_ranking = []

		self.scanner_request = scanner_process

		self.extra_count = 101


		self.tabControl = ttk.Notebook(root)
		self.tabControl.place(x=0,rely=0.01,relheight=1,width=640)

		self.tab1 = tk.Canvas(self.tabControl)
		self.tab2 = tk.Canvas(self.tabControl)

		self.tabControl.add(self.tab2, text ='Nasdaq Trader') 
		self.tabControl.add(self.tab1, text ='TNV Scanner') 


		############## SACNNER ##############

		self.TNVscanner = TNV_Scanner(self.tab1,self,algo_comm)

		############################### Nasdaq Trader ############################################

		# self.NT_refresh = ttk.Button(self.tab2,
		# 	text ="Refresh",command=self.refresh_nasdaq).place(relx=0.01, rely=0.01, height=25, width=70)
		self.update_in_progress = False

		self.nasdaq_is_working_on_it = False
		self.nasdaq = []
		
		self.add_amount = tk.StringVar(self.tab2)
		self.add_choices = {'Top 5','Top 10','Top 20','Top 50','All'}
		self.add_amount.set('Top 5') 

		self.op = tk.OptionMenu(self.tab2, self.add_amount, *sorted(self.add_choices))
		#self.menu1 = ttk.Label(self.setting, text="Country").grid(row = 1, column = 3)
		self.op.place(x=295, rely=0.01, height=25, width=70)

		self.add_button = ttk.Button(self.tab2,
			text ="Add",command=self.add_symbols).place(x=380, rely=0.01, height=25, width=70)
		self.NT_update_time = tk.StringVar(root)
		self.NT_update_time.set('Last updated') 

		self.NT_stat = ttk.Label(self.tab2, textvariable=self.NT_update_time).place(x=10, rely=0.01, height=25, width=200)
		self.all = tk.Canvas(self.tab2)
		self.all.place(x=0,rely=0.05,relheight=1,width=640)

		self.NT_scanner_canvas = tk.Canvas(self.all)
		self.NT_scanner_canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)
		self.scroll = tk.Scrollbar(self.all)
		self.scroll.config(orient=tk.VERTICAL, command=self.NT_scanner_canvas.yview)
		self.scroll.pack(side=tk.RIGHT,fill="y")
		self.NT_scanner_canvas.configure(yscrollcommand=self.scroll.set)
		self.NT_scanner_frame = tk.Frame(self.NT_scanner_canvas)
		self.NT_scanner_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)
		self.NT_scanner_canvas.create_window(0, 0, window=self.NT_scanner_frame, anchor=tk.NW)

		self.df = None

		self.create_nasdaq_trader_pannel()
		self.recreate_labels(self.NT_scanner_frame)



		####################################### Finviz ################################################

		self.tickers_manager = tickers_manager

		self.scanner_process_manager = scanner_process

		# self.setting = ttk.LabelFrame(self.tab1,text="Scanner Settings") 
		# self.setting.place(relx=0.01, rely=0.01, relheight=1, width=480)

		# self.refresh = ttk.Button(self.setting,  
		# 	text ="Fetch Data",command=self.refresh).place(relx=0.8, rely=0.01, height=50, width=70)


		# self.market = tk.StringVar(self.setting)
		# self.choices2 = {'Nasdaq','NYSE','AMEX'}
		# self.market.set('Nasdaq') 

		# self.popupMenu2 = tk.OptionMenu(self.setting, self.market, *self.choices2)
		# self.menu2 = ttk.Label(self.setting, text="Select Market").grid(row = 1, column = 1)
		# self.popupMenu2.grid(row = 2, column =1)

		# self.signal = tk.StringVar(self.setting)
		# self.choices = { 'Most Active','Unusual Volume','Top Gainner','New Highs'}
		# self.signal.set('Most Active') 

		# self.popupMenu = tk.OptionMenu(self.setting, self.signal, *self.choices)
		# self.menu1 = ttk.Label(self.setting, text="Select signal type").grid(row = 1, column = 2)
		# self.popupMenu.grid(row = 2, column =2)

		# self.relv = tk.StringVar(self.setting)
		# self.relvc = {'0.5','1','2','3'}
		# self.relv.set('2') 

		# self.popupMenu3 = tk.OptionMenu(self.setting, self.relv, *self.relvc)
		# self.menu3 = ttk.Label(self.setting, text="Min RelVol").grid(row = 1, column = 3)
		# self.popupMenu3.grid(row = 2, column =3)

		# self.markcap = tk.StringVar(self.setting)
		# self.markcapchoice = {'Any','Mega','Large','Mid','Small','Large+','Mid+','Small+'}
		# self.markcap.set('Any') 

		# self.popupMenu4 = tk.OptionMenu(self.setting, self.markcap, *self.markcapchoice)
		# self.menu4 = ttk.Label(self.setting, text="Market Cap").grid(row = 1, column = 4)
		# self.popupMenu4.grid(row = 2, column =4)

		# self.downloading = False

		# self.status_info = ttk.Label(self.setting, text="Current Status: ")
		# self.status = tk.StringVar()
		# self.status.trace('w', lambda *_, var=self.status,label=self.status_info:status_change(var,label))
		# self.status_info.place(x = 0, y =60)

		# self.status.set("Ready")

		# self.tab = ttk.LabelFrame(self.setting,text="Scanner") 
		# self.tab.place(x=0, y=80, relheight=0.85, relwidth=1)

		# self.scanner_canvas = tk.Canvas(self.tab)
		# self.scanner_canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		# self.scroll = tk.Scrollbar(self.tab)
		# self.scroll.config(orient=tk.VERTICAL, command=self.scanner_canvas.yview)
		# self.scroll.pack(side=tk.RIGHT,fill="y")

		# self.scanner_canvas.configure(yscrollcommand=self.scroll.set)
		# #self.scanner_canvas.bind('<Configure>', lambda e: self.scanner_canvas.configure(scrollregion = self.scanner_canvas.bbox('all')))

		# self.scanner_frame = tk.Frame(self.scanner_canvas)
		# self.scanner_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)
		# self.scanner_canvas.create_window(0, 0, window=self.scanner_frame, anchor=tk.NW)

		# # labels = ["Symbol","Rel.V","Price","Change","Perf Week","MCap","Inst own",\
		# # "Inst tran","Insi own","Insi tran","Short float","Short Ratio","Prem Low","Prem high","Prem Avg","Status"]
		# # width = [8,6,6,6,8,8,8,8,8,8,10,10,10,10,10,10]

		# width = [8,12,10,6,10,10]
		# labels = ["Ticker","Cur.V","Avg.V","Rel.V","%"+"since close","Add to list"]

		# self.info = []

		# for i in range(len(labels)): #Rows
		# 	self.b = tk.Button(self.scanner_frame, text=labels[i],width=width[i])#,command=self.rank
		# 	self.b.configure(activebackground="#f9f9f9")
		# 	self.b.configure(activeforeground="black")
		# 	self.b.configure(background="#d9d9d9")
		# 	self.b.configure(disabledforeground="#a3a3a3")
		# 	self.b.configure(relief="ridge")
		# 	self.b.configure(foreground="#000000")
		# 	self.b.configure(highlightbackground="#d9d9d9")
		# 	self.b.configure(highlightcolor="black")
		# 	self.b.grid(row=1, column=i)

		#self.rebind(self.scanner_canvas,self.scanner_frame)


		# reg = threading.Thread(target=self.alwasy_update,args=(), daemon=True)
		# reg.start()

		# df = pd.read_csv("test.csv",index_col=0)
		# self.add_nasdaq_labels(["d",df,"csc"])

	def update_TNVscanner(self,df):
		self.TNVscanner.update_entry(df)

	def add_symbols(self):


		s = self.add_amount.get()

		l = []
		if s == 'Top 5':
			l = self.nasdaq_trader_symbols[:5]
		elif s == 'Top 10':
			l = self.nasdaq_trader_symbols[:10]
		elif s == 'Top 20':
			l = self.nasdaq_trader_symbols[:20]
		elif s == 'Top 50':
			l = self.nasdaq_trader_symbols[:50]
		elif s == 'All':
			l = self.nasdaq_trader_symbols

		for i in l:
			self.tickers_manager.add_symbol_reg_list(i)

	# def set_data_manager(self,dm):
	# 	self.data = dm

	def recreate_labels(self,frame):

		self.buttons =[]
				#3,14,5,6,4,6,6,6,10,5
		self.nasdaq_width = [4,14,5,6,4,4,6,6,6,12,5]

		self.labels = ["Rank","Symbol","Market","Price","Since","Been","SC%","SO%","L5R%","Status","Add"]


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

		self.status_sort = False
		self.price_sort = False
		self.speed_sort = False
		self.been_sort = False

		self.rank_sort = False

		self.sorting_order = None

		self.close_sort = False
		self.open_sort = False

		self.last_5 = False

		self.since_sort= False

		for i in range(len(self.labels)): #Rows
			self.b = tk.Button(frame, text=self.labels[i],width=self.nasdaq_width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=1, column=i)
			self.buttons.append(self.b)

		self.buttons[0]["command"] = self.rank_button
		self.buttons[1]["command"] = self.speed_button
		self.buttons[2]["command"] = self.market_button
		self.buttons[3]["command"] = self.price_button

		self.buttons[4]["command"] = self.since_button

		self.buttons[5]["command"] = self.been_button
		self.buttons[6]["command"] = self.close_button
		self.buttons[7]["command"] = self.open_button
		self.buttons[8]["command"] = self.last5_button

		self.buttons[9]["command"] = self.status_button


	def change_sorting_order(self,order):
		self.sorting_order = order
		self.nasdaq_labels_sort()
		self.add_nasdaq_labels_update()

	def rank_button(self):
		if self.rank_sort==True:
			self.rank_sort = False
		else:
			self.rank_sort = True

		self.change_sorting_order("rank")

	def been_button(self):
		if self.been_sort==True:
			self.been_sort = False
		else:
			self.been_sort = True

		self.change_sorting_order("been")		

	def since_button(self):
		if self.since_sort==True:
			self.since_sort = False
		else:
			self.since_sort = True

		self.change_sorting_order("since")

	def price_button(self):
		if self.price_sort==True:
			self.price_sort = False
		else:
			self.price_sort = True

		self.change_sorting_order("price")

	def market_button(self):


		if self.nasdaq_trader_created == True:
			for i in range(len(self.market_sort)):
				if self.market_sort[i] == 2:
					self.market_sort[i] = 0
				else:
					self.market_sort[i] +=1 

			self.df.loc[self.df["market"]==2,"market"]=3
			self.df.loc[self.df["market"]==1,"market"]=2
			self.df.loc[self.df["market"]==0,"market"]=1
			self.df.loc[self.df["market"]==3,"market"]=0

			self.change_sorting_order("market")

		#change current values. 

	def speed_button(self):
		self.change_sorting_order("speed")

	def status_button(self):

		if self.nasdaq_trader_created == True:

			for key in self.status_code:
				if  self.status_code[key] == self.status_num-1:
					self.status_code[key] = 0
				else:
					self.status_code[key] +=1 

			#update all the status code. 

			for key in self.status_code:
				self.df.loc[self.df["status"]==key,"status_code"]=self.status_code[key]

			self.change_sorting_order("status")

		print(self.status_code)

	def close_button(self):
		if self.close_sort==True:
			self.close_sort = False
		else:
			self.close_sort = True
		self.change_sorting_order("close")

	def last5_button(self):
		if self.last_5==True:
			self.last_5 = False
		else:
			self.last_5 = True
		self.change_sorting_order("last5")

	def open_button(self):
		if self.open_sort==True:
			self.open_sort = False
		else:
			self.open_sort = True
		self.change_sorting_order("open")

	def sorting_been(self):
		if self.been_sort==True:
			self.df=self.df.sort_values(by=["been"],ascending=False)
		else:
			self.df=self.df.sort_values(by=["been"],ascending=True)		

	def sorting_since(self):
		if self.since_sort==True:
			self.df=self.df.sort_values(by=["fats"],ascending=False)
		else:
			self.df=self.df.sort_values(by=["fats"],ascending=True)		

	def sorting_rank(self):

		if self.rank_sort==True:
			self.df=self.df.sort_values(by=["rank"],ascending=False)
		else:
			self.df=self.df.sort_values(by=["rank"],ascending=True)

	def sorting_market(self):
		self.df = self.df.sort_values(by=["market","rank5","status"],ascending=False)
		#just change the values. 

	def sorting_price(self):

		if self.price_sort==True:
			self.df=self.df.sort_values(by=["price"],ascending=False)
		else:
			self.df=self.df.sort_values(by=["price"],ascending=True)

	def sorting_speed(self):
		self.df = self.df.sort_values(by=["rank5","status"],ascending=False)

	def sortign_status(self):
		self.df = self.df.sort_values(by=["status_code","rank5"],ascending=False)

	def sorting_close(self):
		if self.close_sort==True:
			self.df = self.df.sort_values(by=["close"],ascending=False)
		else:
			self.df = self.df.sort_values(by=["close"],ascending=True)

	def sorting_open(self):
		if self.open_sort==True:
			self.df = self.df.sort_values(by=["open"],ascending=False)
		else:
			self.df = self.df.sort_values(by=["open"],ascending=True)

	def sorting_last5(self):
		if self.last_5==True:
			self.df = self.df.sort_values(by=["last5"],ascending=False)
		else:
			self.df = self.df.sort_values(by=["last5"],ascending=True)

	def nasdaq_labels_sort(self):

		if self.nasdaq_trader_created == True:
			if self.sorting_order == "rank":
				self.sorting_rank()
			elif self.sorting_order == "speed":
				self.sorting_speed()
			elif self.sorting_order == "market":
				self.sorting_market()
			elif self.sorting_order == "status":
				self.sortign_status()
			elif self.sorting_order == "price":
				self.sorting_price()
			elif self.sorting_order == "close":
				self.sorting_close()
			elif self.sorting_order == "open":
				self.sorting_open()
			elif self.sorting_order =="last5":
				self.sorting_last5()
			elif self.sorting_order =="since":
				self.sorting_since()
			elif self.sorting_order =="been":
				self.sorting_been()

		#df.sort_values(by='col1', ascending=False)

	def status_change(self,var):
		self.status.set(var)

	def status_nasdaqchange(self,var):
		self.NT_update_time.set(var)

	def market_suffix(self):
		market_ = self.market.get()
		market = ""
		if market_ == 'Nasdaq':
			market = '.NQ'
			#cond = 'sh_relvol_o2'

		elif market_ =='NYSE':
			market = '.NY'
			#cond = 'sh_relvol_o1'

		elif market_ =='AMEX':
			market = '.AM'
		return market


	def delete_old_lables(self):
		if len(self.info)>0:
			for i in self.info:
				for j in i:
					j.destroy()

	def delete_old_labels_nasdaq(self):
		#i needs to be canvas. 
		for widget in self.NT_scanner_frame.winfo_children():
				widget.destroy()

		# if len(self.nasdaq)>0:
		# 	for i in self.nasdaq:
		# 		for j in i:
		# 			j.destroy()

	def market_suffix_nasdaq_trader(self,symbol,market):

		sy = ""
		if market == "NY":
			sy =symbol +".NY"
		elif market == "AM" or market == "P" or market == "Z":
			sy = symbol +".AM"
		elif market == "Q" or market == "S" or market == "G":
			sy = symbol +".NQ"

		return sy


	def create_nasdaq_trader_pannel(self):

		self.labels = ["Rank","Symbol","Market","Price","Since","Been","SC%","SO%","L5R%","Status","Add"]
		self.nasdaq_width = [4,14,5,6,4,4,6,6,6,12,5]
		for k in range(0,102):

			self.nasdaq.append([])

			for i in range(len(self.labels)): #Rows

				if i==len(self.labels)-1:
					self.b = tk.Button(self.NT_scanner_frame, text=" ",width=self.nasdaq_width[i])#,command=self.rank
				else:
					self.b = tk.Label(self.NT_scanner_frame, text=" ",width=self.nasdaq_width[i])#,command=self.rank
				# self.b.configure(activebackground="#f9f9f9")
				# self.b.configure(activeforeground="black")
				# self.b.configure(background="#d9d9d9")
				# self.b.configure(disabledforeground="#a3a3a3")
				# self.b.configure(relief="ridge")
				# self.b.configure(foreground="#000000")
				# self.b.configure(highlightbackground="#d9d9d9")
				# self.b.configure(highlightcolor="black")
				self.b.grid(row=k+1, column=i)
				self.nasdaq[k].append(self.b)


			#add the button here
			#self.l+=1

		self.nasdaq_trader_created = True

		self.rebind(self.NT_scanner_canvas,self.NT_scanner_frame)
		
	def add_nasdaq_labels_init(self):

		df = self.df
		i = -1
		#width = [3,14,5,6,4,6,6,6,10,5]

		#print("init",len(self.df))
		for index, row in df.iterrows():
			i+=1
			if i<=100:
				rank = row['rank']
				symbol = row['symbol']
				price = row['price']
				roc5 = row['rank5']
				roc10 = row['rank10']
				roc30 = row['rank30']
				status = row['status']
				since = row['fa']
				been = row['been']
				market = symbol[-2:]
				
				info = [rank,index,market,price,since,been,symbol]
				self.nasdaq.append([])

				# ["Rank","Symbol","Market","Price","Since","Been","SC%","SO%","L5R%","Status","Add"]

				for j in range(len(self.nasdaq_width)):
					if j ==0 or j==2 or j==4 or j==5:
						self.nasdaq[i].append(tk.Label(self.NT_scanner_frame ,text=info[j],width=self.nasdaq_width[j]))
						self.nasdaq[i][j].grid(row=i+2, column=j,padx=0)

					elif j ==3:
						try:
							var =  self.data.get_symbol_price(symbol)
						except:
							var == None

						if var != None:
							self.nasdaq[i].append(tk.Label(self.NT_scanner_frame ,textvariable=var,width=self.nasdaq_width[j]))
						else:
							self.nasdaq[i].append(tk.Label(self.NT_scanner_frame ,text="NA",width=self.nasdaq_width[j]))

						self.nasdaq[i][j].grid(row=i+2, column=j,padx=0)
					#close
					elif j ==6:

						try:
							var = self.data.get_close_percentage(symbol)
						except:
							var == None

						if var != None:
							self.nasdaq[i].append(tk.Label(self.NT_scanner_frame ,textvariable=var,width=self.nasdaq_width[j]))
						else:
							self.nasdaq[i].append(tk.Label(self.NT_scanner_frame ,text="NA",width=self.nasdaq_width[j]))

						self.nasdaq[i][j].grid(row=i+2, column=j,padx=0)

					elif j ==7:

						try:
							var = self.data.get_open_percentage(symbol)
						except:
							var == None

						if var != None:
							self.nasdaq[i].append(tk.Label(self.NT_scanner_frame ,textvariable=var,width=self.nasdaq_width[j]))
						else:
							self.nasdaq[i].append(tk.Label(self.NT_scanner_frame ,text="NA",width=self.nasdaq_width[j]))

						self.nasdaq[i][j].grid(row=i+2, column=j,padx=0)
					elif j ==8:

						try:
							var = self.data.get_last_5_range_percentage(symbol)
						except:
							var == None

						if var != None:
							self.nasdaq[i].append(tk.Label(self.NT_scanner_frame ,textvariable=var,width=self.nasdaq_width[j]))
						else:
							self.nasdaq[i].append(tk.Label(self.NT_scanner_frame ,text="NA",width=self.nasdaq_width[j]))

						self.nasdaq[i][j].grid(row=i+2, column=j,padx=0)
					elif j ==9:

						try:
							var = self.data.get_position_status(symbol)
						except:
							var == None

						if var != None:
							self.nasdaq[i].append(tk.Label(self.NT_scanner_frame ,textvariable=var,width=self.nasdaq_width[j]))
						else:
							self.nasdaq[i].append(tk.Label(self.NT_scanner_frame ,text="NA",width=self.nasdaq_width[j]))

						self.nasdaq[i][j].grid(row=i+2, column=j,padx=0)

					elif j ==1:
						self.nasdaq[i].append(tk.Label(self.NT_scanner_frame ,text=info[j],width=self.nasdaq_width[j],background="SystemButtonFace"))
						self.nasdaq[i][j].grid(row=i+2, column=j,padx=0)

						if roc5>0:
							tex = info[j]+" ↑"+str(roc5)
							if int(roc10)>0:
								tex = tex+" ↑"+str(roc10)
							if int(roc30)>0:
								tex = tex+" ↑"+str(roc30)

							color = "#97FEA8"
							if roc5 >3: 
								color = "#BDFE10"
							if roc5 >5:
								color = "#FC3DC8"
							self.nasdaq[i][j]["text"]=tex
							self.nasdaq[i][j]["background"]=color
						else:
							self.nasdaq[i][j]["text"]=index
							self.nasdaq[i][j]["background"]="SystemButtonFace"
					elif j==10:

						self.nasdaq[i].append(tk.Button(self.NT_scanner_frame ,text="Add",width=self.nasdaq_width[j],command= lambda k=symbol: self.tickers_manager.add_symbol_reg_list(k)))
						self.nasdaq[i][j].grid(row=i+2, column=j,padx=0)
						self.nasdaq_trader_symbols.append(symbol)
						self.nasdaq_trader_symbols_ranking[symbol] = rank

		self.nasdaq_trader_created = True
		self.rebind(self.NT_scanner_canvas,self.NT_scanner_frame)

		print("pannel created")

	def add_nasdaq_labels_update(self):

		df = self.df

		i = 0

		self.update_pd()

		if self.nasdaq_trader_created==True:


			for index, row in df.iterrows():
				i+=1
				if i<=100:
					rank = row['rank']
					symbol = row['symbol']
					price = row['price']
					roc5 = row['rank5']
					roc10 = row['rank10']
					roc30 = row['rank30']
					status = row['status']
					market = symbol[-2:]
					since = row['fa']
					been = row['been']
					info = [rank,index,market,price,since,been,status,symbol]

				
					for j in range(len(self.nasdaq_width)):

						if j ==0 or j==2 or j==4 or j==5:
							self.nasdaq[i][j]["text"] = info[j]
						elif j == 3:
							try:
								var =  self.data.get_symbol_price(symbol)
							except:
								var == None

							if var != None:
								self.nasdaq[i][j]["textvariable"] = var
							else:
								self.nasdaq[i][j]["text"] = "NA"

						elif j == 6:
							try:
								var = self.data.get_close_percentage(symbol)
							except:
								var == None

							if var != None :
								self.nasdaq[i][j]["textvariable"] = var
							else:
								self.nasdaq[i][j]["text"] = "NA"
						elif j == 7:
							try:
								var = self.data.get_open_percentage(symbol)
							except:
								var == None

							if var != None :
								self.nasdaq[i][j]["textvariable"] = var
							else:
								self.nasdaq[i][j]["text"] = "NA"

						elif j == 8:
							try:
								var = self.data.get_last_5_range_percentage(symbol)
							except:
								var == None

							if var != None :
								self.nasdaq[i][j]["textvariable"] = var
							else:
								self.nasdaq[i][j]["text"] = "NA"

						elif j == 9:
							try:
								var = self.data.get_position_status(symbol)
							except:
								var == None

							if var != None :
								self.nasdaq[i][j]["textvariable"] = var
							else:
								self.nasdaq[i][j]["text"] = "NA"

						elif j ==1:
							if roc5>0:
								tex = info[j]+" ↑"+str(roc5)
								if int(roc10)>0:
									tex = tex+" ↑"+str(roc10)
								if int(roc30)>0:
									tex = tex+" ↑"+str(roc30)

								color = "#97FEA8"
								if roc5 >3: 
									color = "#BDFE10"
								if roc5 >5:
									color = "#FC3DC8"
								self.nasdaq[i][j]["text"]=tex
								self.nasdaq[i][j]["background"]=color
							else:
								self.nasdaq[i][j]["text"]=index
								self.nasdaq[i][j]["background"]="SystemButtonFace"
						elif j ==10:
							self.nasdaq_trader_symbols_ranking[symbol] = rank
							self.nasdaq_trader_symbols.append(symbol)
							self.nasdaq[i][j]["command"] = lambda k=symbol: self.tickers_manager.add_symbol_reg_list(k)
			print("pannel updated")
	#This is where every update comes in. 


	#gives the SDM price and status to pd. 
	# call this every 5 seconds
	def update_pd(self):

		#grab the data from symbol and update df.
		# status. price. 
		#row['symbol']
		df = self.df
		if self.nasdaq_trader_created==True and self.update_in_progress==False:
			self.update_in_progress = True 
			for index, row in df.iterrows():
				symbol = row["symbol"]
				status = self.data.get_position_status(symbol)
				close_ = self.data.get_close_percentage(symbol)
				open_ = self.data.get_open_percentage(symbol)
				last5 = self.data.get_last_5_range_percentage(symbol)

				if status != None:
					df.loc[index,"status"] = status.get()
					df.loc[index,"close"] = close_.get()
					df.loc[index,"open"] = open_.get()
					df.loc[index,"last5"] = last5.get()
				else:
					df.loc[index,"status"] = ""
					df.loc[index,"close"] = 0
					df.loc[index,"open"] = 0
					df.loc[index,"last5"] = 0

			statuts = df['status'].unique()

			for i in statuts:
				if i not in self.status_code:
					self.status_code[i]=self.status_num
					self.status_num+=1

			for key in self.status_code:
				df.loc[df["status"]==key,"status_code"] =  self.status_code[key]

		self.update_in_progress = False


	def add_nasdaq_labels(self,data):

		print("receive new data")

		now = datetime.now()
		ts = now.hour*60 + now.minute

		if ts>=570:
			self.buttons[7]["text"] = "SO%"
		else:
			self.buttons[7]["text"] = "RRR"	

		if 1:
			if self.nasdaq_is_working_on_it==False:

				self.nasdaq_is_working_on_it = True
				self.nasdaq_trader_symbols = []
				
			
				df = data[0]
				timestamp = data[1]
				

				#df = df[df.market =='NQ'][:20].copy()
				df.to_csv("test.csv")
				df.loc[df["market"]=='NQ',"market"] = self.market_sort[0]
				df.loc[df["market"]=='NY',"market"] = self.market_sort[1]
				df.loc[df["market"]=='AM',"market"] = self.market_sort[2]

				df["close"] = 0
				df["open"] = 0
				#registration 

				self.df = df

				for index, row in df.iterrows():
					if row['symbol'] not in self.symbols_registry:
						self.data.partial_register(row['symbol'])
				time.sleep(1)
				#update the SDM data to the PD

				self.update_pd()

				#update the infos from SDM

				#call the sort.
				#check if added.
				#update. 
				

				if self.nasdaq_trader_created == False:
					#time.sleep(5)
					self.add_nasdaq_labels_init()
				else:
					self.nasdaq_labels_sort()
					self.add_nasdaq_labels_update()

				self.NT_update_time.set(timestamp)

				#self.scanner_process_manager.updating_comlete()

				self.nasdaq_is_working_on_it = False
		# except Exception as e:
		# 	self.nasdaq_is_working_on_it = False
		# 	self.nasdaq_trader_created == False
		# 	print("NT:",e)

	def refresh(self):

		#this is where it downloads the stock info. Turn this into multi processing. just allocate the info and send it.

		cond = "sh_relvol_o"+self.relv.get()
		market_ = self.market.get()
		type_ = self.signal.get()
		cap = self.markcap.get()

		self.delete_old_lables()
		self.scanner_process_manager.send_request(cond,market_,type_,cap)

	#every 1 minute? i am relectant to do it here. 
	def refresh_nasdaq(self):
		#self.delete_old_labels_nasdaq()
		self.scanner_process_manager.refresh_nasdaq_trader()

	def add_labels(self,d):
		#This is where it adds the labels.

		if (len(d)==0):
			#got nothing!
			self.status_change("Unmatch results")
			self.scanner_process_manager.adding_comlete()
		else:
			width = [8,12,10,6,10,10]
			labels = ["Ticker","Cur.V","Avg.V","Rel.V","%"+"since close","Add to list"]
			suffix = self.market_suffix()

			self.info = []
			good = True
			try:
				for i in range(len(d)):
					#info = [d.iloc[i]["Ticker"],d.iloc[i]["Volume"],d.iloc[i]["Avg Volume"],d.iloc[i]["Rel Volume"],\d.iloc[i]["Change"],"","","",""]
					info = [d[i]["Ticker"],d[i]["Volume"],d[i]["Avg Volume"],d[i]["Rel Volume"],\
					d[i]["Change"],"","","",""]
					self.info.append([])
					for j in range(len(labels)):
						if j!= len(labels)-1:
							self.info[i].append(tk.Label(self.scanner_frame ,text=info[j],width=width[j]))
							#self.label_default_configure(self.info[i][j])
							self.info[i][j].grid(row=i+2, column=j,padx=0)
						else:
							self.info[i].append(tk.Button(self.scanner_frame ,text=info[j],width=width[j],command= lambda k=i: self.tickers_manager.add_symbol_reg_list(d[k]["Ticker"]+suffix)))
							#self.label_default_configure(self.info[i][j])
							self.info[i][j].grid(row=i+2, column=j,padx=0)
			except:
				good = False

			super().rebind(self.scanner_canvas,self.scanner_frame)

			self.scanner_process_manager.adding_comlete()

			if good:
				self.scanner_process_manager.adding_comlete()
				self.status_change("Ready")
			else:
				self.status_change("Please retry")
				self.scanner_process_manager.adding_comlete()



if __name__ == '__main__':

	root = tk.Tk() 
	root.title("GoodTrade v489") 
	root.geometry("640x840")

	TNVscanner(root,None)

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

