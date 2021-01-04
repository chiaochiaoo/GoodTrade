import tkinter as tk                     
from tkinter import ttk 
import pandas as pd
import numpy as np
import os 
import time
import threading

from alerts import *
from pannel import *
from Symbol_data_manager import *

from scanner import *
from scanner_process_manager import *

from database_process_manager import *
#from database_functions import *

from ppro_process_manager import *




class viewer:

	def __init__(self,root,scanner_process,database_process,ppro_process):
		
		self.data = Symbol_data_manager()

		self.db = database_process
		self.db.set_symbols_manager(self.data)

		self.ppro = ppro_process
		self.ppro.set_symbols_manager(self.data)


		self.data.set_database_manager(self.db)
		self.data.set_ppro_manager(self.ppro)


		self.listening = ttk.LabelFrame(root,text="Listener") 
		self.listening.place(x=500,rely=0.05,relheight=1,width=900)

		self.tabControl = ttk.Notebook(self.listening) 
		self.tab1 = tk.Canvas(self.tabControl) 
		self.tab2 = tk.Canvas(self.tabControl) 
		self.tab3 = tk.Canvas(self.tabControl)
		self.tab4 = tk.Canvas(self.tabControl) 
		self.tab5 = tk.Canvas(self.tabControl)
		self.tab6 = tk.Canvas(self.tabControl)
		self.tab7 = tk.Canvas(self.tabControl)
		self.tab8 = tk.Canvas(self.tabControl)
		self.tab9 = tk.Canvas(self.tabControl)

		self.tabControl.add(self.tab1, text ='Tickers Manager') 
		self.tabControl.add(self.tab8, text ='All alerts') 
		self.tabControl.add(self.tab5, text ='High-Low')
		self.tabControl.add(self.tab6, text ='Open-High')
		self.tabControl.add(self.tab7, text ='Open-Low')
		self.tabControl.add(self.tab2, text ='Extreme Range') 
		self.tabControl.add(self.tab3, text ='Extreme Volume') 
		self.tabControl.add(self.tab4, text ='First five minutes')
		self.tabControl.add(self.tab9, text ='Breakout')
		self.tabControl.pack(expand = 1, fill ="both") 

		#self.ticker_management_init(self.tab1)
		self.all_alerts = all_alerts(self.tab8)
		
		self.open_high_pannel = openhigh(self.tab6,self.data,self.all_alerts)

		self.high_low_pannel = highlow(self.tab5,self.data,self.all_alerts)
		self.open_low_pannel = openlow(self.tab7,self.data,self.all_alerts)

		self.first_5 = firstfive(self.tab4,self.data,self.all_alerts)
		self.er = extremrange(self.tab2,self.data,self.all_alerts)
		self.ev = extremevolume(self.tab3,self.data,self.all_alerts)

		self.br = breakout(self.tab9,self.data,self.all_alerts)

		#alerts  =[self.open_high_pannel]
		alerts = [self.high_low_pannel,self.open_high_pannel,self.open_low_pannel,self.first_5,self.er,self.ev,self.br]

		self.tm = ticker_manager(self.tab1,self.data,alerts)
		

		self.scanner_pannel = scanner(root,self.tm,scanner_process)

		scanner_process.set_pannel(self.scanner_pannel)


		# sm = price_updater(self.data)
		# sm.start()



class ticker_manager(pannel):
	def __init__(self,frame,data,alerts):
		super().__init__(frame)

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

		self.ticker_stats = ttk.Label(frame, text="Current Registered Tickers: "+str(self.ticker_count))
		self.ticker_stats.place(x = 200, y =12)

		#############Registration Window ####################

		self.data = data


		self.width = [8,10,12,10,24,10,10]
		self.labels = ["Ticker","Status","Last update","Price","Last Alert","Last Alert time","Remove"]

		#init the labels. 
		self.labels_creator(self.frame)

		self.init_reg_list()

	def init_reg_list(self):

		ticks = self.data.get_list()

		for i in range(len(ticks)):
			self.add_symbol_label(ticks[i])

		self.tickers = self.data.get_list()
		self.rebind(self.canvas,self.frame)

	def delete_symbol_reg_list(self,symbol):

		if symbol in self.tickers:
			
			#1. remove it from the list.
			self.data.delete(symbol)


			for i in self.tickers_labels[symbol]:
				i.destroy()

			self.tickers_labels.pop(symbol,None)


			self.ticker_count -= 1
			self.ticker_stats["text"] = "Current Registered Tickers: "+str(self.ticker_count)

			self.rebind(self.canvas,self.frame)

		for i in self.alerts:
			i.delete_symbol(symbol)
		return True


	def add_symbol_label(self,symbol):

		# data = threading.Thread(target=self.data.data_request(symbol), daemon=True)
		# data.start()

		i = symbol
		l = self.label_count

		info = [symbol,\
				self.data.symbol_status[symbol],\
				self.data.symbol_update_time[symbol],\
				self.data.symbol_price[symbol],\
				self.data.symbol_last_alert[symbol],\
				self.data.symbol_last_alert_time[symbol],
				""]

		self.tickers_labels[i]=[]

		#add in tickers.
		for j in range(len(info)):
			if j == 0:
				self.tickers_labels[i].append(tk.Label(self.frame ,text=info[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

			elif j == 1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=info[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				info[j].trace('w', lambda *_, text=info[j],label=self.tickers_labels[i][j]: self.status_change_color(text,label))
			elif j != (len(info)-1):
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=info[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

				
			else:
				self.tickers_labels[i].append(tk.Button(self.frame ,text=info[j],width=self.width[j],command = lambda s=symbol: self.delete_symbol_reg_list(s)))
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



if __name__ == '__main__':

	multiprocessing.freeze_support()


	#### SCANNER SUB PROCESS####
	request_scanner, receive_pipe = multiprocessing.Pipe()
	p = multiprocessing.Process(target=multi_processing_scanner, args=(receive_pipe,),daemon=True)
	p.daemon=True
	p.start()

	s = scanner_process_manager(request_scanner)

	#### DATABASE SUB PROCESS####

	request_database, receive_database = multiprocessing.Pipe()
	d = multiprocessing.Process(target=multi_processing_database, args=(receive_database,),daemon=True)
	d.daemon=True
	d.start()

	d = database_process_manager(request_database)

	### INFO FETCH SUB PROCESS####

	request_pipe, receive_pipe = multiprocessing.Pipe()
	p2 = multiprocessing.Process(target=multi_processing_price, args=(receive_pipe,),daemon=True)
	p2.daemon=True
	p2.start()

	ppro = ppro_process_manager(request_pipe)

	### scanner pannel needs the manager. 
	
	root = tk.Tk() 
	root.title("GoodTrade") 
	root.geometry("1400x700")
	root.minsize(1200, 600)
	root.maxsize(3000, 1500)

	view = viewer(root,s,d,ppro)
	root.mainloop()