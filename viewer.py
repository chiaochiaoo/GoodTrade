import tkinter as tk                     
from tkinter import ttk 

import pandas as pd
import numpy as np

import os 
import time
import threading
import requests 

from scanner import *
from pannel import *
from Symbol_data_manager import *

class viewer:


	def __init__(self, root=None):

		self.data = Symbol_data_manager()

		self.listening = ttk.LabelFrame(root,text="Listener") 
		self.listening.place(relx=0.41,rely=0.05,relheight=1,width=650)

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

		#self.ticker_management_init(self.tab1)

		self.tm = ticker_manager(self.tab1,self.data)
		
		self.scanner_pannel = scanner(root,self.tm)

		# self.high_low_pannel = highlow(self.tab5)
		# self.Open_High_init(self.tab6)
		# self.Open_Low_init(self.tab7)

		sm = price_updater(self.data)
		sm.start()


class ticker_manager(pannel):
	def __init__(self,frame,data):
		super()
		self.Entry1 = tk.Entry(frame)
		self.Entry1.place(x=5, y=5, height=30, width=80, bordermode='ignore')
		self.Entry1.configure(background="white")
		self.Entry1.configure(cursor="fleur")
		self.Entry1.configure(disabledforeground="#a3a3a3")
		self.Entry1.configure(font="TkFixedFont")
		self.Entry1.configure(foreground="#000000")
		self.Entry1.configure(insertbackground="black")

		self.symbol = tk.Button(frame,command= lambda: self.add_symbol_reg_list(self.Entry1.get().upper())) #,command=self.loadsymbol
		#self.Data = tk.Button(self.Labelframe1,command=lambda: self.test(2))
		self.symbol.place(x=105, y=5, height=30, width=80, bordermode='ignore')
		self.symbol.configure(activebackground="#ececec")
		self.symbol.configure(activeforeground="#000000")
		self.symbol.configure(background="#d9d9d9")
		self.symbol.configure(disabledforeground="#a3a3a3")
		self.symbol.configure(foreground="#000000")
		self.symbol.configure(highlightbackground="#d9d9d9")
		self.symbol.configure(highlightcolor="black")
		self.symbol.configure(pady="0")
		self.symbol.configure(text='''Add Symbol''')


		self.tickers = []
		self.tickers_labels = []
		self.ticker_count = 0
		self.ticker_index = {}

		self.label_count = 0

		self.ticker_stats = ttk.Label(frame, text="Current Registered Tickers: "+str(self.ticker_count))
		self.ticker_stats.place(x = 200, y =12)

		#############Registration Window ####################

		self.data = data

		self.tm = ttk.LabelFrame(frame) 
		self.tm.place(x=0, y=40, relheight=0.85, relwidth=1)

		self.tmcanvas = tk.Canvas(self.tm)
		self.tmcanvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll2 = tk.Scrollbar(self.tm)
		self.scroll2.config(orient=tk.VERTICAL, command=self.tmcanvas.yview)
		self.scroll2.pack(side=tk.RIGHT,fill="y")

		self.tmcanvas.configure(yscrollcommand=self.scroll2.set)
		#self.scanner_canvas.bind('<Configure>', lambda e: self.scanner_canvas.configure(scrollregion = self.scanner_canvas.bbox('all')))

		self.tmframe = tk.Frame(self.tmcanvas)
		self.tmframe.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)

		self.tmcanvas.create_window(0, 0, window=self.tmframe, anchor=tk.NW)

		width = [8,10,12,10,10,12,10,10]
		labels = ["Ticker","Status","Last update","Price","Last Alert","Last Alert time","Remove"]



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

	def init_reg_list(self):

		#current_count = self.ticker_count
		#self.ticker_count = self.data.get_count()
		#self.tickers_labels = []

		ticks = self.data.get_list()
		width = [8,10,12,10,12,10,10]

		#print(self.tickers)
		for i in range(len(ticks)):
			self.add_symbol_label(ticks[i])

		self.tickers = self.data.get_list()
		super().rebind(self.tmcanvas,self.tmframe)

	def delete_symbol_reg_list(self,symbol):

		print(self.ticker_index)

		if symbol in self.tickers:
			
			#1. remove it from the list.
			self.data.delete(symbol)

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
			self.ticker_stats["text"] = "Current Registered Tickers: "+str(self.ticker_count)

			# dereg = threading.Thread(target=deregister,args=(symbol,), daemon=True)
			# dereg.start()

			print("index",index)
			print("ticker",len(self.tickers))
			print("labels",len(self.tickers_labels))
			print(self.tickers)
			print(self.ticker_index)
			print(index)
		#3. for rest of the items - rerange the positions. 


		return True


	# def set_status_color(self,symbol,color):

	# 	#locate the symbol label

	# 	status = self.tickers_labels[self.ticker_index[symbol]][]
	# 	status["background"] = color



	def add_symbol_label(self,symbol):


		self.ticker_index[symbol] = self.ticker_count 
		i = self.ticker_count

		l = self.label_count

		print("adding position:",symbol,":",i)
		width = [8,10,12,10,10,12,10,10]

		info = [symbol,\
				self.data.symbol_status[symbol],\
				"",\
				"",\
				"",\
				"",
				""]

		# reg = threading.Thread(target=register,args=(symbol,), daemon=True)
		# reg.start()

		self.tickers_labels.append([])

		#add in tickers.
		for j in range(len(info)):
			if j == 0:
				self.tickers_labels[i].append(tk.Label(self.tmframe ,text=info[j],width=width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

			elif j == 1:
				self.tickers_labels[i].append(tk.Label(self.tmframe ,textvariable=info[j],width=width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

				info[j].trace('w', lambda *_, text=info[j],label=self.tickers_labels[i][j]: self.status_change_color(text,label))
			elif j != (len(info)-1):
				self.tickers_labels[i].append(tk.Label(self.tmframe ,textvariable=info[j],width=width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

				
			else:
				self.tickers_labels[i].append(tk.Button(self.tmframe ,text=info[j],width=width[j],command = lambda s=symbol: self.delete_symbol_reg_list(s)))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

		self.ticker_count +=1

		self.label_count +=1

		self.ticker_stats["text"] = "Current Registered Tickers: "+str(self.ticker_count)

		self.rebind(self.tmcanvas,self.tmframe)
		#print(self.ticker_index)

		#print(self.tickers)

	def add_symbol_reg_list(self,symbol):

		if symbol not in self.tickers:

			self.data.add(symbol)
			self.add_symbol_label(symbol)




#a seperate thread on its own. 
class price_updater:

	#A big manager. Who has access to all the corresponding grids in the labels. 
	#update each symbols per, 39 seconds? 
	#run every ten seconds. 
	def __init__(self,s: Symbol_data_manager):
		#need to track. 1 min range/ volume. 5 min range/volume.
		#self.depositLabel['text'] = 'change the value'
		#fetch this 
		self.price_list = []
		self.volume_list = []

		self.symbols = s.get_list()

		self.sdm = s

		#Won't need these no more.
		# self.symbols_labels = v.tickers_labels
		# self.symbols_index = v.ticker_index

		#time
		# self.last_update = {}
		# self.last_price = {}

		# self.lowhigh_cur = {}
		# self.openhigh_cur = {}
		# self.openlow_cur = {}

		# self.lowhigh ={}
		# self.openlow ={}
		# self.openhigh = {}

		# self.lock = {}
		# self.open = {}
		# self.high = {}
		# self.low = {}

		# self.open_high = 0
		# self.high_low = 0
		# self.open_low = 0

		self.count = 0

		self.init_info()

		#repeat this every 5 seconds.


	def init_info(self):

		for i in self.symbols:
			self.sdm.change_status(i, "Connecting")

	
	#these three functions together update the prices per second. 
	def start(self):
		print("Console (PT): Thread created, ready to start")
		t1 = threading.Thread(target=self.update_info, daemon=True)
		#t1.start()
		print("Console (PT): Thread running. Continue:")

	def update_info(self):
		#fetch every 1 minute. ?
		#better do all together. 
		while True:
			#print("symbols:",self.symbols)
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

			if symbol in self.symbols:
				if stat =="Connected":
					status["background"] = "#83FF33"
					status["text"],timestamp["text"],price["text"]= stat,time,midprice

					##Asert Alert list here? 
				else:
					status["background"] = "red"
					status["text"] = stat

			self.lock[symbol] = False

class highlow:

	def __init__(self,frame):

		self.hlframe = ttk.LabelFrame(frame) 
		self.hlframe.place(x=0, y=40, relheight=0.85, relwidth=1)

		self.hlcanvas = tk.Canvas(self.hlframe)
		self.hlcanvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.hlscroll = tk.Scrollbar(self.hlframe)
		self.hlscroll.config(orient=tk.VERTICAL, command=self.hlcanvas.yview)
		self.hlscroll.pack(side=tk.RIGHT,fill="y")

		self.hlcanvas.configure(yscrollcommand=self.hlscroll.set)
		#self.scanner_canvas.bind('<Configure>', lambda e: self.scanner_canvas.configure(scrollregion = self.scanner_canvas.bbox('all')))

		self.hlframe_ = tk.Frame(self.hlcanvas)
		self.hlframe_.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)

		self.hlcanvas.create_window(0, 0, window=self.hlframe_, anchor=tk.NW)

		width = [8,10,12,10,10,12,10,10]
		labels = ["Ticker","Status","Range","Average","Current"]

		#init the labels. 
		for i in range(len(labels)): #Rows
			self.b = tk.Button(self.hlframe_, text=labels[i],width=width[i])#command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=1, column=i)

	def add_symbol(self,symbol):
		return True
	def delete_symbol(self,symbol):
		return True


reg_count = 0
def find_between(data, first, last):
    try:
        start = data.index(first) + len(first)
        end = data.index(last, start)
        return data[start:end]
    except ValueError:
        return data

def register(symbol):
	global reg_count
	try:
		p="http://localhost:8080/Register?symbol="+symbol+"&feedtype=L1"
		r= requests.get(p)
		reg_count+=1
		print(symbol,"registerd ","total:",reg_count)
		return True
	except Exception as e:
		print(e)
		return False

def deregister(symbol):
	global reg_count
	try:
		p="http://localhost:8080/Deregister?symbol="+symbol+"&feedtype=L1"
		r= requests.get(p)
		reg_count-=1
		print(symbol,"deregister","total:",reg_count)
		return True
	except Exception as e:
		print(e)
		return False

def getinfo(symbol):
	try:
		p="http://localhost:8080/GetLv1?symbol="+symbol
		r= requests.get(p)
		if(r.text =='<Response><Content>No data available symbol</Content></Response>'):
			print("No symbol found")
			return "Unfound","time",""
		time=find_between(r.text, "MarketTime=\"", "\"")[:-4]
		Bidprice= float(find_between(r.text, "BidPrice=\"", "\""))
		Askprice= float(find_between(r.text, "AskPrice=\"", "\""))
		#print(time,price)
		return "Connected",time,round((Bidprice+Askprice)/2,4)
    # p="http://localhost:8080/Deregister?symbol="+symbol+"&feedtype=L1"
    # r= requests.get(p,allow_redirects=False,stream=True)
	except Exception as e:
		print(e)
		return "Disconnected","",""

root = tk.Tk() 
root.title("GoodTrade") 
root.geometry("1200x700")
root.minsize(1000, 600)
root.maxsize(3000, 1500)
view = viewer(root)

root.mainloop()