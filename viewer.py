import tkinter as tk                     
from tkinter import ttk 
import pandas as pd
import numpy as np
import os 
import time
import threading

from alerts import *
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
		self.high_low_pannel = highlow(self.tab5,self.data)

		self.tm = ticker_manager(self.tab1,self.data,[self.high_low_pannel])
		
		self.scanner_pannel = scanner(root,self.tm)


		# self.Open_High_init(self.tab6)
		# self.Open_Low_init(self.tab7)

		sm = price_updater(self.data)
		sm.start()


class ticker_manager(pannel):
	def __init__(self,frame,data,alerts):
		super()

		self.alerts = alerts
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

		self.canvas = tk.Canvas(self.tm)
		self.canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)

		self.scroll2 = tk.Scrollbar(self.tm)
		self.scroll2.config(orient=tk.VERTICAL, command=self.canvas.yview)
		self.scroll2.pack(side=tk.RIGHT,fill="y")

		self.canvas.configure(yscrollcommand=self.scroll2.set)
		#self.scanner_canvas.bind('<Configure>', lambda e: self.scanner_canvas.configure(scrollregion = self.scanner_canvas.bbox('all')))

		self.frame = tk.Frame(self.canvas)
		self.frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)

		self.canvas.create_window(0, 0, window=self.frame, anchor=tk.NW)

		width = [8,10,12,10,10,12,10,10]
		labels = ["Ticker","Status","Last update","Price","Last Alert","Last Alert time","Remove"]

		#init the labels. 
		self.labels_creator(self.frame,labels, width)

		self.init_reg_list()

	def init_reg_list(self):

		ticks = self.data.get_list()
		width = [8,10,12,10,12,10,10]

		for i in range(len(ticks)):
			self.add_symbol_label(ticks[i])

		self.tickers = self.data.get_list()
		self.rebind(self.canvas,self.frame)

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

			print("index",index)
			print("ticker",len(self.tickers))
			print("labels",len(self.tickers_labels))
			print(self.tickers)
			print(self.ticker_index)
			print(index)
		#3. for rest of the items - rerange the positions. 

		self.rebind(self.canvas,self.frame)
		return True


	def add_symbol_label(self,symbol):


		self.ticker_index[symbol] = self.ticker_count 
		i = self.ticker_count

		l = self.label_count

		print("adding position:",symbol,":",i)
		width = [8,10,12,10,10,12,10,10]
		info = [symbol,\
				self.data.symbol_status[symbol],\
				self.data.symbol_update_time[symbol],\
				self.data.symbol_price[symbol],\
				self.data.symbol_last_alert[symbol],\
				self.data.symbol_last_alert_time[symbol],
				""]

		self.tickers_labels.append([])

		#add in tickers.
		for j in range(len(info)):
			if j == 0:
				self.tickers_labels[i].append(tk.Label(self.frame ,text=info[j],width=width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

			elif j == 1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=info[j],width=width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

				info[j].trace('w', lambda *_, text=info[j],label=self.tickers_labels[i][j]: self.status_change_color(text,label))
			elif j != (len(info)-1):
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=info[j],width=width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

				
			else:
				self.tickers_labels[i].append(tk.Button(self.frame ,text=info[j],width=width[j],command = lambda s=symbol: self.delete_symbol_reg_list(s)))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

		self.ticker_count +=1

		self.label_count +=1

		self.ticker_stats["text"] = "Current Registered Tickers: "+str(self.ticker_count)
		self.data.change_status(symbol, "Connecting")
		self.rebind(self.canvas,self.frame)

		for i in self.alerts:
			i.add_symbol(symbol)
		#print(self.ticker_index)

		#print(self.tickers)

	def add_symbol_reg_list(self,symbol):

		if symbol not in self.tickers:

			self.data.add(symbol)
			self.add_symbol_label(symbol)

#a seperate thread on its own. 





root = tk.Tk() 
root.title("GoodTrade") 
root.geometry("1200x700")
root.minsize(1000, 600)
root.maxsize(3000, 1500)
view = viewer(root)

root.mainloop()