import tkinter as tk                     
from tkinter import ttk 
from finviz.screener import Screener
import pandas as pd
import numpy as np
from os import path
import os 
import time
import threading
import requests 

def getinfo(symbol):
	try:
		p="http://localhost:8080/Register?symbol="+symbol+"&feedtype=L1"
		r= requests.get(p,allow_redirects=False,stream=True)

		p="http://localhost:8080/GetLv1?symbol="+symbol
		r= requests.get(p,allow_redirects=False,stream=True)

		time=find_between(r.text, "MarketTime=\"", "\"")[:-4]
		Bidprice= float(find_between(r.text, "BidPrice=\"", "\""))
		Askprice= float(find_between(r.text, "AskPrice=\"", "\""))
		#print(time,price)
		return "Connected",time,round((Bidprice+Askprice)/2,3)
    # p="http://localhost:8080/Deregister?symbol="+symbol+"&feedtype=L1"
    # r= requests.get(p,allow_redirects=False,stream=True)
	except:
		return "Disconnected","",""



def find_between(data, first, last):
    try:
        start = data.index(first) + len(first)
        end = data.index(last, start)
        return data[start:end]
    except ValueError:
        return data

class list_manager:	

	#if file does not exist, create an empty file. 
	def __init__(self):

		if not path.exists("list.txt"):
			self.list = []
		else:
			self.list = np.array(np.loadtxt('list.txt',dtype="str")).tolist()

			if type(self.list) is str:
				self.list = [self.list]

		print("LM initilize:",self.list)

	def save(self):
		#print(self.list)
		np.savetxt('list.txt',self.list, delimiter=",", fmt="%s")   
		

	def add(self,symbol):
		self.list.append(symbol)
		self.save()
		#print(self.list)

	def delete(self,symbol):
		if symbol in self.list:
			self.list.remove(symbol)
		self.save()

	def get_list(self):
		return self.list

	def get_count(self):
		return len(self.list)

class viewer:


	#only run the first time.
	def init_reg_list(self):

		
		#current_count = self.ticker_count
		#self.ticker_count = self.lm.get_count()
		#self.tickers_labels = []

		ticks = self.lm.get_list()
		width = [8,10,12,10,12,10,10]

		#print(self.tickers)
		for i in range(len(ticks)):
			self.add_symbol_label(ticks[i])

		self.tickers = self.lm.get_list()
		self.rebind_lm()
		#print(self.ticker_index)


	def delete_symbol_reg_list(self,symbol):

		print(self.ticker_index)

		if symbol in self.tickers:
			
			#1. remove it from the list.
			self.lm.delete(symbol)

			#2. get the index. Destory it.
			index = self.ticker_index[symbol]

			for i in self.tickers_labels[index]:
				i.destroy()

			self.tickers_labels.pop(index)
			self.ticker_index.pop(symbol)

			#update the rest of them.
			if index <= (len(self.tickers)-1):
				for i in self.tickers[index:]:
					self.ticker_index[i] -=1


			self.ticker_count -= 1
			print("index",index)
			print("ticker",len(self.tickers))
			print("labels",len(self.tickers_labels))
			print(self.tickers)
			print(self.ticker_index)
			print(index)
		#3. for rest of the items - rerange the positions. 


		return True

	###Checking: 1. Symbol exist. 2. Symbol repeat. 

	def add_symbol_label(self,symbol):

		self.ticker_index[symbol] = self.ticker_count 

		i = self.ticker_count

		width = [8,10,12,10,10,12,10,10]
		info = [symbol,"Connecting","","","","",""]

		self.tickers_labels.append([])
		for j in range(len(info)):
			if j != (len(info)-1):
				self.tickers_labels[i].append(tk.Label(self.tmframe ,text=info[j],width=width[j]))
				self.tickers_labels[i][j].configure(activebackground="#f9f9f9")
				self.tickers_labels[i][j].configure(activeforeground="black")
				self.tickers_labels[i][j].configure(background="#d9d9d9")
				self.tickers_labels[i][j].configure(disabledforeground="#a3a3a3")
				self.tickers_labels[i][j].configure(relief="ridge")
				self.tickers_labels[i][j].configure(foreground="#000000")
				self.tickers_labels[i][j].configure(highlightbackground="#d9d9d9")
				self.tickers_labels[i][j].configure(highlightcolor="black")
				self.tickers_labels[i][j].grid(row= i+2, column=j,padx=0)
			else:
				self.tickers_labels[i].append(tk.Button(self.tmframe ,text=info[j],width=width[j],command = lambda s=symbol: self.delete_symbol_reg_list(s)))
				self.tickers_labels[i][j].configure(activebackground="#f9f9f9")
				self.tickers_labels[i][j].configure(activeforeground="black")
				self.tickers_labels[i][j].configure(background="#d9d9d9")
				self.tickers_labels[i][j].configure(disabledforeground="#a3a3a3")
				self.tickers_labels[i][j].configure(relief="ridge")
				self.tickers_labels[i][j].configure(foreground="#000000")
				self.tickers_labels[i][j].configure(highlightbackground="#d9d9d9")
				self.tickers_labels[i][j].configure(highlightcolor="black")
				self.tickers_labels[i][j].grid(row= i+2, column=j,padx=0)

		self.ticker_count +=1

		self.rebind_lm()
		#print(self.ticker_index)

		#print(self.tickers)

	def add_symbol_reg_list(self,symbol):

		if symbol not in self.tickers:

			self.lm.add(symbol)
			self.add_symbol_label(symbol)

	def add_symbol(self,symbol):

		#1. add it to our lm. 
		#2. add it to our list. 
		#3. refresh_display? 
		return True



	def __init__(self, root=None):

		self.listening = ttk.LabelFrame(root,text="Listener") 
		self.listening.place(relx=0.05,rely=0.05,relheight=0.4,relwidth=.9)

		self.tabControl = ttk.Notebook(self.listening) 

		self.tab1 = tk.Canvas(self.tabControl) 
		self.tab2 = tk.Canvas(self.tabControl) 
		self.tab3 = tk.Canvas(self.tabControl)
		self.tab4 = tk.Canvas(self.tabControl) 
		self.tab5 = tk.Canvas(self.tabControl)
		self.tab6 = tk.Canvas(self.tabControl)
		self.tab7 = tk.Canvas(self.tabControl)

		self.tabControl.add(self.tab1, text ='Tickers Management') 
		self.tabControl.add(self.tab2, text ='Extreme Range') 
		self.tabControl.add(self.tab3, text ='Extreme Volume') 
		self.tabControl.add(self.tab4, text ='First five minutes')
		self.tabControl.add(self.tab5, text ='High-Low')
		self.tabControl.add(self.tab6, text ='Open-High')
		self.tabControl.add(self.tab7, text ='Open-Low')
		self.tabControl.pack(expand = 1, fill ="both") 

		#Ticker Management.
		#add a new symbol.
		#symbol list.
		self.Entry1 = tk.Entry(self.tab1)
		self.Entry1.place(relx=0.005, rely=0.05, relheight=0.08, relwidth=0.1, bordermode='ignore')
		self.Entry1.configure(background="white")
		self.Entry1.configure(cursor="fleur")
		self.Entry1.configure(disabledforeground="#a3a3a3")
		self.Entry1.configure(font="TkFixedFont")
		self.Entry1.configure(foreground="#000000")
		self.Entry1.configure(insertbackground="black")

		self.symbol = tk.Button(self.tab1,command= lambda: self.add_symbol_reg_list(self.Entry1.get().upper())) #,command=self.loadsymbol
		#self.Data = tk.Button(self.Labelframe1,command=lambda: self.test(2))
		self.symbol.place(relx=0.12, rely=0.05, relheight=0.08, width=80, bordermode='ignore')
		self.symbol.configure(activebackground="#ececec")
		self.symbol.configure(activeforeground="#000000")
		self.symbol.configure(background="#d9d9d9")
		self.symbol.configure(disabledforeground="#a3a3a3")
		self.symbol.configure(foreground="#000000")
		self.symbol.configure(highlightbackground="#d9d9d9")
		self.symbol.configure(highlightcolor="black")
		self.symbol.configure(pady="0")
		self.symbol.configure(text='''Add Symbol''')



		#############Registration Window ####################

		self.lock = False
		self.lm = list_manager()

		self.tm = ttk.LabelFrame(self.tab1) 
		self.tm.place(relx=0, rely=0.15, relheight=0.85, relwidth=1)

		self.tmcanvas = tk.Canvas(self.tm)
		self.tmcanvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll2 = tk.Scrollbar(self.tm)
		self.scroll2.config(orient=tk.VERTICAL, command=self.tmcanvas.yview)
		self.scroll2.pack(side=tk.RIGHT,fill="y")

		self.tmcanvas.configure(yscrollcommand=self.scroll2.set)
		#self.mycanvas.bind('<Configure>', lambda e: self.mycanvas.configure(scrollregion = self.mycanvas.bbox('all')))

		self.tmframe = tk.Frame(self.tmcanvas)
		self.tmframe.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)

		self.tmcanvas.create_window(0, 0, window=self.tmframe, anchor=tk.NW)

		width = [8,10,12,10,10,12,10,10]
		labels = ["Ticker","Status","Last update","Price","Last Alert","Last Alert time","Remove"]

		self.tickers = []
		self.tickers_labels = []
		self.ticker_count = 0
		self.ticker_index = {}

		#init the labels. 
		for i in range(len(labels)): #Rows
			self.b = tk.Button(self.tmframe, text=labels[i],width=width[i])#command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=1, column=i)

		self.init_reg_list()



		#############################  SCANNER  ################################################

		self.setting = ttk.LabelFrame(root,text="Settings") 
		self.setting.place(relx=0.05, rely=0.45, relheight=0.55, relwidth=0.9)

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

		self.tab = ttk.LabelFrame(self.setting,text="Scanner") 

		self.tab.place(relx=0, rely=0.15, relheight=0.85, relwidth=1)

		self.mycanvas = tk.Canvas(self.tab)
		self.mycanvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll = tk.Scrollbar(self.tab)
		self.scroll.config(orient=tk.VERTICAL, command=self.mycanvas.yview)
		self.scroll.pack(side=tk.RIGHT,fill="y")

		self.mycanvas.configure(yscrollcommand=self.scroll.set)
		#self.mycanvas.bind('<Configure>', lambda e: self.mycanvas.configure(scrollregion = self.mycanvas.bbox('all')))

		self.tab2 = tk.Frame(self.mycanvas)
		self.tab2.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)

		self.mycanvas.create_window(0, 0, window=self.tab2, anchor=tk.NW)

		labels = ["Symbol","Rel.V","Price","Change","Perf Week","MCap","Inst own",\
		"Inst tran","Insi own","Insi tran","Short float","Short Ratio","Prem Low","Prem high","Prem Avg","Status"]
		width = [8,6,6,6,8,8,8,8,8,8,10,10,10,10,10,10]

		width = [8,12,10,6,10,10]
		labels = ["Ticker","Cur.V","Avg.V","Rel.V","%"+"since close","Add to list"]

		self.info = []

		for i in range(len(labels)): #Rows
			self.b = tk.Button(self.tab2, text=labels[i],width=width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=1, column=i)


	def rebind(self):
		self.mycanvas.update_idletasks()
		self.mycanvas.config(scrollregion=self.tab2.bbox())

	def rebind_lm(self):
		self.tmcanvas.update_idletasks()
		self.tmcanvas.config(scrollregion=self.tmframe.bbox())


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

	def refresh(self):

		d = self.refreshstocks()

		#d= readstocks()
		#read the corresponding list. 

		width = [8,12,10,6,10,10]
		labels = ["Ticker","Cur.V","Avg.V","Rel.V","%"+"since close","Add to list"]
		#append it to the view.
		if len(self.info)>0:
			for i in self.info:
				for j in i:
					j.destroy()

		self.info = []

		suffix = self.market_suffix()



		for i in range(len(d)):
			#info = [d.iloc[i]["Ticker"],d.iloc[i]["Volume"],d.iloc[i]["Avg Volume"],d.iloc[i]["Rel Volume"],\d.iloc[i]["Change"],"","","",""]
			info = [d[i]["Ticker"],d[i]["Volume"],d[i]["Avg Volume"],d[i]["Rel Volume"],\
			d[i]["Change"],"","","",""]
			self.info.append([])
			for j in range(len(labels)):
				if j!= len(labels)-1:
					self.info[i].append(tk.Label(self.tab2 ,text=info[j],width=width[j]))
					self.info[i][j].configure(activebackground="#f9f9f9")
					self.info[i][j].configure(activeforeground="black")
					self.info[i][j].configure(background="#d9d9d9")
					self.info[i][j].configure(disabledforeground="#a3a3a3")
					self.info[i][j].configure(relief="ridge")
					self.info[i][j].configure(foreground="#000000")
					self.info[i][j].configure(highlightbackground="#d9d9d9")
					self.info[i][j].configure(highlightcolor="black")
					self.info[i][j].grid(row=i+2, column=j,padx=0)
				else:
					self.info[i].append(tk.Button(self.tab2 ,text=info[j],width=width[j],command= lambda k=i: self.add_symbol_reg_list(d[k]["Ticker"]+suffix)))
					self.info[i][j].configure(activebackground="#f9f9f9")
					self.info[i][j].configure(activeforeground="black")
					self.info[i][j].configure(background="#d9d9d9")
					self.info[i][j].configure(disabledforeground="#a3a3a3")
					self.info[i][j].configure(relief="ridge")
					self.info[i][j].configure(foreground="#000000")
					self.info[i][j].configure(highlightbackground="#d9d9d9")
					self.info[i][j].configure(highlightcolor="black")
					self.info[i][j].grid(row=i+2, column=j,padx=0)

		self.rebind()
		self.rebind_lm()


					# labels = ["Symbol","Rel.V","Price","Change","Perf Week","MCap","Inst own",\
		# "Inst tran","Insi own","Insi tran","Short float","Short Ratio","Prem Low","Prem high","Prem Avg","Status"]
		# width = [8,6,6,6,8,8,8,8,8,8,10,10,10,10,10,10]


	def rank(self):
		for i in range(len(self.info_nas)):
			for j in range(len(self.info_nas[i])):
				self.info_nas[i][j].grid(row=len(self.info_nas)-i+1, column=j,padx=0)



	#add it to it .


	def refreshstocks(self):


		market = ''
		cond = "sh_relvol_o"+self.relv.get()
		cond2 = ''
		signal = ''

		market_ = self.market.get()
		type_ = self.signal.get()

		cap = self.markcap.get() 

		if market_ == 'Nasdaq':
			market = 'exch_nasd'
			#cond = 'sh_relvol_o2'

		elif market_ =='NYSE':
			market = 'exch_nyse'
			#cond = 'sh_relvol_o1'

		elif market_ =='AMEX':
			market = 'exch_amex'
			#cond = 'sh_relvol_o1'

		if type_ == 'Most Active':
			signal = 'ta_mostactive'

		elif type_ =='Top Gainner':
			signal = 'ta_topgainers'

		elif type_ =='New Highs':
			signal = 'ta_newhigh'

		elif type_ =='Unusual Volume':
			signal = 'ta_unusualvolume'

		#'Any','Mega','Large','Mid','Small','Mega+','Large+','Mid+','Small+'}

		if cap =='Any':
			cond2 = ''
		elif cap == 'Mega':
			cond2 = 'cap_mega'
		elif cap =='Large':
			cond2 = 'cap_large'
		elif cap == 'Mid':
			cond2 = 'cap_mid'
		elif cap =='Small':
			cond2 = 'cap_small'
		elif cap =='Large+':
			cond2 = 'cap_largeover'
		elif cap =='Mid+':
			cond2 = 'cap_midover'
		elif cap =='Small+':
			cond2 = 'cap_smallover'

		#self.markcap.set('Any') 



		filters = [market,cond,cond2]  # Shows companies in NASDAQ which are in the S&P500

		stock_list = Screener(filters=filters, table='Performance', signal=signal)  # Get the performance table and sort it by price ascending

		print(len(stock_list))
		return stock_list
	  	# Export the screener results to .csv
		#stock_list.to_csv("temp.csv")

	  	# stock_list2 = Screener(filters=filters, table='Ownership', signal=signal) #,order='-relativevolume'
	  	# stock_list2.to_csv("NASDAQ_stock_own.csv")


#a seperate thread on its own. 
class symbol_manager:

	#A big manager. Who has access to all the corresponding grids in the labels. 
	#update each symbols per, 39 seconds? 


	#run every ten seconds. 
	def __init__(self,v: viewer):
		#need to track. 1 min range/ volume. 5 min range/volume.

		#self.depositLabel['text'] = 'change the value'
		#fetch this 
		self.price_list = []
		self.volume_list = []

		self.symbols = v.tickers
		self.symbols_labels = v.tickers_labels
		self.symbols_index = v.ticker_index

		#time
		self.last_update = {}
		self.last_price = {}


		self.lock = {}

		# self.price = 0
		# self.volume = 
		self.open = {}
		self.high = {}
		self.low = {}

		self.open_high = 0
		self.high_low = 0
		self.open_low = 0

		self.count = 0

		self.init_info()


		#repeat this every 5 seconds.


	def init_info(self):
		info = ["Connecting","/","/","/","/"]
		for i in range(len(self.symbols_labels)):
			for j in range(1,len(self.symbols_labels[i])-1):
				self.symbols_labels[i][j]["text"]= info[j-1]

	def add_symbol():
		return True 
	def delete_symbol():
		return True
	
	def start(self):

		print("Console (PT): Thread created, ready to start")
		t1 = threading.Thread(target=self.update_info, daemon=True)
		t1.start()
		print("Console (PT): Thread running. Continue:")

	def update_info(self):
		#fetch every 1 minute. ?
		#better do all together. 

		while True:
			print("symbols:",self.symbols)
			self.count+=1
			for i in range(len(self.symbols_labels)):
				for j in range(1,len(self.symbols_labels[i])-1):

					status = self.symbols_labels[i][1]
					timestamp = self.symbols_labels[i][2]
					price = self.symbols_labels[i][3]
					#self.symbols_labels[i][j]["text"]= self.count
					
					#self.update_symbol(self.symbols[i],status,timestamp,price)
					fetch = threading.Thread(target=self.update_symbol, args=(self.symbols[i],status,timestamp,price,), daemon=True)
					#only start when the last one has returned. 
					fetch.start()
			time.sleep(1)


	#a single thread 
	def update_symbol(self,symbol,status,timestamp,price):

		#get the info. and, update!!!
		if symbol not in self.lock:
			 self.lock[symbol] = False
		if self.lock[symbol]==False:
			self.lock[symbol] = True

			stat,time,midprice = getinfo(symbol)

			#I need to make sure that label still exist. 
			#status["text"],timestamp["text"],price["text"]= self.count,self.count,self.count
			if stat =="Connected":
				status["background"] = "#83FF33"
				status["text"],timestamp["text"],price["text"]= "connected",time,midprice
			else:
				status["background"] = "red"
				status["text"] = "Disconnected"

			self.lock[symbol] = False



# test = ["SPY.AM","QQQ.NQ"]
# test = np.array(test)
# np.savetxt('list.txt',test, delimiter=",", fmt="%s")  





root = tk.Tk() 
root.title("GoodTrade") 
root.geometry("500x700")
root.minsize(800, 700)
root.maxsize(1500, 800)
view = viewer(root)

sm = symbol_manager(view)
sm.start()

root.mainloop()