import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import os
import time
import threading

import sys



class entry:


	def capital_to_shares(self,capital,shares,price):
		print(capital.get(),shares.get(),price)
	def shares_to_capital(self,capital,shares):
		pass

	def deactivate_entry(self,options,entry):

		options=options.get()
		#print(options.get(),entry)

		if options == "Market":
			entry["state"]="disabled"
		elif options =="Limit":
			entry["state"]='normal'


	def int_check(self, P):
		if str.isdigit(P) or P=="":
			return True
		else:
			return False

	def float_check(self,P):
		try:
			a = float(P)
			return True
		except:
			return False

	def __init__(self,frame,entry_price=None):

		row = 1
		

		self.entry_type = tk.StringVar(frame)
		self.entry_type_choices = {'Long','Short'}
		self.entry_type.set('Long') 

		self.order_type = tk.StringVar(frame)
		self.order_type_choices = {'Market','Limit'}
		self.order_type.set('Market') 

		self.entry_price = tk.StringVar(frame)
		self.entry_price.set(entry_price)

		self.shares = tk.StringVar(frame)
		self.capital = tk.StringVar(frame)



		int_check = (frame.register(self.int_check))
		float_check =(frame.register(self.float_check))

		tk.Label(frame,text="Entry type: ").grid(row=row,column=1)
		tk.OptionMenu(frame, self.entry_type, *sorted(self.entry_type_choices)).grid(row=row,column=2)

		row+=1
		tk.Label(frame,text="Order type: ").grid(row=row,column=1)
		tk.OptionMenu(frame, self.order_type, *sorted(self.order_type_choices)).grid(row=row,column=2)
		self.price_entry=tk.Entry(frame,width=10,textvariable=self.entry_price,state="disabled",validate='all', validatecommand=(float_check, '%P'))
		self.price_entry.grid(row=row,column=3)
		self.order_type.trace('w', lambda *_, string=self.order_type,entry=self.price_entry: self.deactivate_entry(string,entry))

		row+=1

		tk.Label(frame,text="Shares: ").grid(row=row,column=1)
		tk.Entry(frame,width=10,textvariable=self.shares,validate='all', validatecommand=(int_check, '%P')).grid(row=row,column=2)
		row+=1
		tk.Label(frame,text="Capital: ").grid(row=row,column=1)
		tk.Entry(frame,width=10,textvariable=self.capital,validate='all', validatecommand=(int_check, '%P')).grid(row=row,column=2)
			

		self.capital.trace('w', lambda *_, capital=self.capital,shares=self.shares,price=self.entry_price: self.capital_to_shares(capital,shares,price))


		


		#type,ordertype,price,shares. 
		self.values = []

class algo_placer:

	def __init__(self,symbol,triggers,entry_price=None):

		root = tk.Tk() 
		root.title("Algo Placer: "+symbol) 
		root.geometry("700x400")
		#root.minsize(600, 400)
		root.maxsize(700, 400)

		self.root = root

		self.symbol = tk.Label(root,text="Symbol: "+symbol)
		self.symbol.place(x=10,y=10)

		self.symbol = tk.Label(root,text="Trigger type: "+triggers)
		self.symbol.place(x=10,y=30)


		############### ENTRY ################
		self.entryFrame = ttk.LabelFrame(root,text="Entry") 
		self.entryFrame.place(x=10,y=60,height=300,width=300)


		self.entry = entry(self.entryFrame,entry_price)


		################ STOP LOSS######################
		self.stop = ttk.LabelFrame(root,text="Stoploss") 
		self.stop.place(x=320,y=60,height=100,width=200)

		tk.Label(self.stop,text="Stoploss type: ").place(x=10, y=10)

		self.stop_type = tk.StringVar(self.stop)
		self.stop_type_choices = {'','','','','On Capital loss'}
		self.stop_type.set('Top 5') 

		self.stop_type_ui = tk.OptionMenu(self.stop, self.stop_type, *sorted(self.stop_type_choices))
		#self.menu1 = ttk.Label(self.setting, text="Country").grid(row = 1, column = 3)
		self.stop_type_ui.place(x=10, y=30) #height=25, width=70)


		######################################
		self.position_management = ttk.LabelFrame(root,text="Position Management") 
		self.position_management.place(x=440,y=60,height=100,width=200)	

		self.start()

		# sm = price_updater(self.data)
		# sm.start()


	def start(self):

		self.root.mainloop() 

# 		super().__init__(frame)

# 		self.alerts = alerts

# 		self.Entry1 = tk.Entry(frame)
# 		self.Entry1.place(x=5, y=5, height=30, width=80, bordermode='ignore')
# 		self.Entry1.configure(background="white")
# 		self.Entry1.configure(cursor="fleur")
# 		self.Entry1.configure(disabledforeground="#a3a3a3")
# 		self.Entry1.configure(font="TkFixedFont")
# 		self.Entry1.configure(foreground="#000000")
# 		self.Entry1.configure(insertbackground="black")

# 		self.symbol = tk.Button(frame,command= lambda: self.add_symbol_reg_list(self.Entry1.get().upper())) #,command=self.loadsymbol
# 		self.symbol.place(x=105, y=5, height=30, width=80, bordermode='ignore')
# 		self.symbol.configure(activebackground="#ececec")
# 		self.symbol.configure(activeforeground="#000000")
# 		self.symbol.configure(background="#d9d9d9")
# 		self.symbol.configure(disabledforeground="#a3a3a3")
# 		self.symbol.configure(foreground="#000000")
# 		self.symbol.configure(highlightbackground="#d9d9d9")
# 		self.symbol.configure(highlightcolor="black")
# 		self.symbol.configure(pady="0")
# 		self.symbol.configure(text='''Add Symbol''')

# 		#"Ppro Status: "+"Connecting"
# 		self.ppro_status = ttk.Label(frame, textvariable=data.ppro_status)
# 		self.ppro_status.place(x = 200, y =12)
# 		#data.ppro_status.set("Hello")

# 		self.ticker_stats = ttk.Label(frame, text="Current Registered Tickers: "+str(self.ticker_count))
# 		self.ticker_stats.place(x = 500, y =12)

# 		#############Registration Window ####################

# 		self.data = data


# 		self.width = [8,10,12,10,24,10,10]
# 		self.labels = ["Ticker","Status","Last update","Price","Last Alert","Last Alert time","Remove"]

# 		#init the labels. 
# 		self.labels_creator(self.frame)



algo_placer("AAPL.NQ","Breakout on Resistance on 134.45 for 60 secs",134.45)