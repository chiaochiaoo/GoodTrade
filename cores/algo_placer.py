import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import os
import time
import threading

import sys



class entry:

	def get_all_infos(self):
		return self.entry_type.get(),self.entry_price.get(),self.shares.get()

	def capital_to_shares(self,capital,shares,price):

		if (self.sync_lock==False) and capital.get()!="" and price.get()!="":

			self.sync_lock = True

			try:
				amount = str(int(int(capital.get())//float(price.get())))
				#print(amount)
				shares.set(amount)
			except:
				pass
			# capital.get()
			# shares.get()
			self.sync_lock = False

	def shares_to_capital(self,capital,shares,price):
		if (self.sync_lock==False) and shares.get()!="" and price.get()!="":

			self.sync_lock = True

			try:
				amount = str(round(int(shares.get())*float(price.get()),2))
				#print(amount)
				capital.set(amount)
			except:
				pass
			# capital.get()
			# shares.get()
			self.sync_lock = False

	def price_to_capital(self,capital,shares,price):

		if (self.sync_lock==False) and price.get()!="" and shares.get()!="":

			self.sync_lock = True
			try:
				amount = str(round(int(shares.get())*float(price.get()),2))
				#print(amount)
				capital.set(amount)
			except:
				pass
			# capital.get()
			# shares.get()
			self.sync_lock = False

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

	def set_stop_pannel(self,stop):
		self.stop = stop

	def __init__(self,frame,entry_price=None):

		row = 1
			
		self.sync_lock = False

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
			

		self.entry_price.trace('w', lambda *_, capital=self.capital,shares=self.shares,price=self.entry_price: self.price_to_capital(capital,shares,price))
		self.shares.trace('w', lambda *_, capital=self.capital,shares=self.shares,price=self.entry_price: self.shares_to_capital(capital,shares,price))
		self.capital.trace('w', lambda *_, capital=self.capital,shares=self.shares,price=self.entry_price: self.capital_to_shares(capital,shares,price))

		#type,ordertype,price,shares. 
		self.values = []


class stop:


	def stoplevel_to_per_risk(self,stoplevel,perrisk,totalrisk):

		entry_type,entry,shares = self.entry.get_all_infos()

		if (self.sync_lock==False) and entry!="" and shares!="":

			self.sync_lock = True
			if entry_type =="Long":
				amount = str(round(float(entry)-float(stoplevel.get()),2))
			else:
				amount = str(round(float(stoplevel.get())-entry),2)
				

			total = round(float(amount)*int(shares),2)
			perrisk.set(amount)
			totalrisk.set(total)

			print(totalrisk.get())

			self.sync_lock = False

	def perrisk_to_stoplevel(self,stoplevel,perrisk,totalrisk):
		if (self.sync_lock==False) and shares.get()!="" and price.get()!="":

			self.sync_lock = True

			amount = str(round(int(shares.get())*float(price.get()),2))
			print(amount)
			capital.set(amount)
			# capital.get()
			# shares.get()
			self.sync_lock = False

	############ THIS ONE CHANGES the entry column
	def total_risk_to_shares(self,stoplevel,perrisk,totalrisk):

		if (self.sync_lock==False) and price.get()!="" and shares.get()!="":

			self.sync_lock = True

			amount = str(round(int(shares.get())*float(price.get()),2))
			print(amount)
			capital.set(amount)
			# capital.get()
			# shares.get()
			self.sync_lock = False

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

	def set_entry_pannel(self,entry):
		self.entry = entry

	def __init__(self,frame,entry_price=None):

		row = 1
			
		self.sync_lock = False

		self.stop_type = tk.StringVar(frame)
		self.stop_type_choices = {'Mid','Ask','Bid','Trailing'}
		self.stop_type.set('Mid') 


		self.stop_level = tk.StringVar(frame)
		self.stop_level.set(entry_price)

		self.risk_per_share =  tk.StringVar(frame)
		self.total_risk  =  tk.StringVar(frame)


		int_check = (frame.register(self.int_check))
		float_check =(frame.register(self.float_check))


		tk.Label(frame,text="Stop type: ").grid(row=row,column=1)
		tk.OptionMenu(frame, self.stop_type, *sorted(self.stop_type_choices)).grid(row=row,column=2)

		row+=1
		tk.Label(frame,text="Stop Level: ").grid(row=row,column=1)

		self.stop_level_entry=tk.Entry(frame,width=10,textvariable=self.stop_level,validate='all', validatecommand=(float_check, '%P'))
		self.stop_level_entry.grid(row=row,column=2) #

		row+=1
		tk.Label(frame,text="Risk per share: ").grid(row=row,column=1)

		self.Riskpershare_entry=tk.Entry(frame,width=10,textvariable=self.risk_per_share,validate='all', validatecommand=(float_check, '%P'))
		self.Riskpershare_entry.grid(row=row,column=2)

		row+=1
		tk.Label(frame,text="Total risk: ").grid(row=row,column=1)

		self.Totalrisk_entry=tk.Entry(frame,width=10,textvariable=self.total_risk,validate='all', validatecommand=(float_check, '%P'))
		self.Totalrisk_entry.grid(row=row,column=2)


		#self.order_type.trace('w', lambda *_, string=self.order_type,entry=self.price_entry: self.deactivate_entry(string,entry))

		self.stop_level.trace('w', lambda *_, stoplevel=self.stop_level,perrisk=self.risk_per_share,totalrisk=self.total_risk: self.stoplevel_to_per_risk(stoplevel,perrisk,totalrisk))
		self.risk_per_share.trace('w', lambda *_, stoplevel=self.stop_level,perrisk=self.risk_per_share,totalrisk=self.total_risk: self.perrisk_to_stoplevel(stoplevel,perrisk,totalrisk))
		self.total_risk.trace('w', lambda *_, stoplevel=self.stop_level,perrisk=self.risk_per_share,totalrisk=self.total_risk: self.total_risk_to_shares(stoplevel,perrisk,totalrisk))
		# self.shares.trace('w', lambda *_, capital=self.capital,shares=self.shares,price=self.entry_price: self.shares_to_capital(capital,shares,price))
		# self.capital.trace('w', lambda *_, capital=self.capital,shares=self.shares,price=self.entry_price: self.capital_to_shares(capital,shares,price))

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
		self.entryFrame.place(x=10,y=60,height=300,width=250)


		self.stopFrame = ttk.LabelFrame(root,text="Stop") 
		self.stopFrame.place(x=260,y=60,height=300,width=250)


		self.entry = entry(self.entryFrame,entry_price)



		self.stop = stop(self.stopFrame,entry_price)
		self.stop.set_entry_pannel(self.entry)


		######################################
		# self.position_management = ttk.LabelFrame(root,text="Position Management") 
		# self.position_management.place(x=440,y=60,height=100,width=200)	

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