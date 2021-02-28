import tkinter as tk                     
from tkinter import ttk 
import threading
import pandas as pd

from pannel import *
from scanner_process_manager import *


def status_change(var,label):
	label["text"] = "Current Status: "+var.get()

class scanner(pannel):

	def __init__(self,root,tickers_manager,scanner_process:scanner_process_manager):

		super()

		#mark if already created. if so, just update the infos. 
		self.nasdaq_trader_created = False

		self.nasdaq_trader_symbols = []
		self.nasdaq_trader_list = {}
		self.nasdaq_trader_symbols_ranking = []
		self.nasdaq_trader_ranking = []

		self.tabControl = ttk.Notebook(root)
		self.tabControl.place(x=0,rely=0.01,relheight=1,width=500)

		self.tab1 = tk.Canvas(self.tabControl)
		self.tab2 = tk.Canvas(self.tabControl)

		self.tabControl.add(self.tab1, text ='Finviz') 
		self.tabControl.add(self.tab2, text ='Nasdaq Trader') 
		self.nasdaq = []
		############################### Nasdaq Trader ############################################

		self.nasdaq = []

		# self.NT_refresh = ttk.Button(self.tab2,
		# 	text ="Refresh",command=self.refresh_nasdaq).place(relx=0.01, rely=0.01, height=25, width=70)

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

		width = [3,7,7,11,11,10,5]
		labels = ["Rank","Symbol","MKT Center","Matched Shares","Last Matched","Open Orders","Add"]

		self.NT = ttk.Notebook(self.tab2)
		self.NT.place(x=0,rely=0.05,relheight=1,width=500)

		self.all = tk.Canvas(self.NT)
		self.fastmover = tk.Canvas(self.NT)
		self.newhigh = tk.Canvas(self.NT)
		self.newlow = tk.Canvas(self.NT)

		self.NT.add(self.all, text ='All')
		self.NT.add(self.fastmover, text ='FastMover')
		self.NT.add(self.newhigh, text ='New High')
		self.NT.add(self.newlow, text ='New Low')


		self.NT_scanner_canvas = tk.Canvas(self.all)
		self.NT_scanner_canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)
		self.scroll = tk.Scrollbar(self.all)
		self.scroll.config(orient=tk.VERTICAL, command=self.NT_scanner_canvas.yview)
		self.scroll.pack(side=tk.RIGHT,fill="y")
		self.NT_scanner_canvas.configure(yscrollcommand=self.scroll.set)
		self.NT_scanner_frame = tk.Frame(self.NT_scanner_canvas)
		self.NT_scanner_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)
		self.NT_scanner_canvas.create_window(0, 0, window=self.NT_scanner_frame, anchor=tk.NW)

		self.recreate_labels(self.NT_scanner_frame)


		############################### Finviz ############################################

		self.tickers_manager = tickers_manager

		self.scanner_process_manager = scanner_process

		self.setting = ttk.LabelFrame(self.tab1,text="Scanner Settings") 
		self.setting.place(relx=0.01, rely=0.01, relheight=1, width=480)

		self.refresh = ttk.Button(self.setting,  
			text ="Fetch Data",command=self.refresh).place(relx=0.8, rely=0.01, height=50, width=70)


		self.market = tk.StringVar(self.setting)
		self.choices2 = {'Nasdaq','NYSE','AMEX'}
		self.market.set('Nasdaq') 

		self.popupMenu2 = tk.OptionMenu(self.setting, self.market, *self.choices2)
		self.menu2 = ttk.Label(self.setting, text="Select Market").grid(row = 1, column = 1)
		self.popupMenu2.grid(row = 2, column =1)

		self.signal = tk.StringVar(self.setting)
		self.choices = { 'Most Active','Unusual Volume','Top Gainner','New Highs'}
		self.signal.set('Most Active') 

		self.popupMenu = tk.OptionMenu(self.setting, self.signal, *self.choices)
		self.menu1 = ttk.Label(self.setting, text="Select signal type").grid(row = 1, column = 2)
		self.popupMenu.grid(row = 2, column =2)

		self.relv = tk.StringVar(self.setting)
		self.relvc = {'0.5','1','2','3'}
		self.relv.set('2') 

		self.popupMenu3 = tk.OptionMenu(self.setting, self.relv, *self.relvc)
		self.menu3 = ttk.Label(self.setting, text="Min RelVol").grid(row = 1, column = 3)
		self.popupMenu3.grid(row = 2, column =3)

		self.markcap = tk.StringVar(self.setting)
		self.markcapchoice = {'Any','Mega','Large','Mid','Small','Large+','Mid+','Small+'}
		self.markcap.set('Any') 

		self.popupMenu4 = tk.OptionMenu(self.setting, self.markcap, *self.markcapchoice)
		self.menu4 = ttk.Label(self.setting, text="Market Cap").grid(row = 1, column = 4)
		self.popupMenu4.grid(row = 2, column =4)

		self.downloading = False

		self.status_info = ttk.Label(self.setting, text="Current Status: ")
		self.status = tk.StringVar()
		self.status.trace('w', lambda *_, var=self.status,label=self.status_info:status_change(var,label))
		self.status_info.place(x = 0, y =60)

		self.status.set("Ready")

		self.tab = ttk.LabelFrame(self.setting,text="Scanner") 
		self.tab.place(x=0, y=80, relheight=0.85, relwidth=1)

		self.scanner_canvas = tk.Canvas(self.tab)
		self.scanner_canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll = tk.Scrollbar(self.tab)
		self.scroll.config(orient=tk.VERTICAL, command=self.scanner_canvas.yview)
		self.scroll.pack(side=tk.RIGHT,fill="y")

		self.scanner_canvas.configure(yscrollcommand=self.scroll.set)
		#self.scanner_canvas.bind('<Configure>', lambda e: self.scanner_canvas.configure(scrollregion = self.scanner_canvas.bbox('all')))

		self.scanner_frame = tk.Frame(self.scanner_canvas)
		self.scanner_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)
		self.scanner_canvas.create_window(0, 0, window=self.scanner_frame, anchor=tk.NW)

		# labels = ["Symbol","Rel.V","Price","Change","Perf Week","MCap","Inst own",\
		# "Inst tran","Insi own","Insi tran","Short float","Short Ratio","Prem Low","Prem high","Prem Avg","Status"]
		# width = [8,6,6,6,8,8,8,8,8,8,10,10,10,10,10,10]

		width = [8,12,10,6,10,10]
		labels = ["Ticker","Cur.V","Avg.V","Rel.V","%"+"since close","Add to list"]

		self.info = []

		for i in range(len(labels)): #Rows
			self.b = tk.Button(self.scanner_frame, text=labels[i],width=width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=1, column=i)

		self.rebind(self.scanner_canvas,self.scanner_frame)


		# df = pd.read_csv("test.csv",index_col=0)
		# self.add_nasdaq_labels(df)

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


	def recreate_labels(self,frame):
		width = [5,12,5,8,20,5]
		labels = ["Rank","Symbol","Market","Price","Status","Add"]

		for i in range(len(labels)): #Rows
			self.b = tk.Button(frame, text=labels[i],width=width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=1, column=i)


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

	#This is the button function.
	#Take all the information needed and send it to the new process.


	#Steps1. Asychonous Version.
	#Steps2. Synchonous Version. - Just need to let it load, and then call it and sne,.d

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


	def add_nasdaq_labels_init(df):

		for index, row in df.iterrows():
			i+=1
			rank = row['rank']
			symbol = row['symbol']
			price = row['price']
			roc5 = row['rank5']
			roc10 = row['rank10']
			roc30 = row['rank30']
			status = row['status']

			market = symbol[-2:]
			
			info = [rank,index,market,price,status,symbol]
			self.nasdaq.append([])

			for j in range(len(width)):
				if j ==0 or j==2 or j==3 or j==4:
					self.nasdaq[i].append(tk.Label(self.NT_scanner_frame ,text=info[j],width=width[j]))
					self.nasdaq[i][j].grid(row=i+2, column=j,padx=0)
				elif j ==1:
					self.nasdaq[i].append(tk.Label(self.NT_scanner_frame ,text=info[j],width=width[j],background="SystemButtonFace"))
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
				elif j ==5:

					self.nasdaq[i].append(tk.Button(self.NT_scanner_frame ,text="Add",width=width[j],command= lambda k=symbol: self.tickers_manager.add_symbol_reg_list(k)))
					self.nasdaq[i][j].grid(row=i+2, column=j,padx=0)
					self.nasdaq_trader_symbols.append(symbol)

		self.nasdaq_trader_created = True
		self.rebind(self.NT_scanner_canvas,self.NT_scanner_frame)

	def add_nasdaq_labels_update(df):
		for index, row in df.iterrows():
			i+=1
			rank = row['rank']
			symbol = row['symbol']
			price = row['price']
			roc5 = row['rank5']
			roc10 = row['rank10']
			roc30 = row['rank30']
			status = row['status']
			market = symbol[-2:]
			info = [rank,index,market,price,status,symbol]

			for j in range(len(width)):
				if j ==0 or j==2 or j==3 or j==4:
					self.nasdaq[i][j]["text"] = info[j]
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
				elif j ==5:
					self.nasdaq_trader_symbols.append(symbol)
					self.nasdaq[i][j]["command"] = lambda k=symbol: self.tickers_manager.add_symbol_reg_list(k)

	def nasdaq_labels_sort(self,df):
		
		return df
		#df.sort_values(by='col1', ascending=False)


	def add_nasdaq_labels(self,df):

		width = [5,12,5,8,20,5]
		self.nasdaq_trader_symbols = []
		i = -1
		
		timestamp = df[2]
		df = df[1]

		#call the sort.
		#check if added.
		#update. 
		df = self.nasdaq_labels_sort(df)

		if self.nasdaq_trader_created == False:
			self.add_nasdaq_labels_init(df)
		else:
			self.add_nasdaq_labels_update(df)
			
		self.NT_update_time.set(timestamp)

		self.scanner_process_manager.updating_comlete()


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



# df=pd.read_csv("test.csv",index_col=0)

# df=df.sort_values(by="rank",ascending=False)


# df.loc["VIOT","status"] = ""

# df=df.sort_values(by=["rank","status"],ascending=False)

# print(df)

