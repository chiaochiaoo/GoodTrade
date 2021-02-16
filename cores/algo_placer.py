import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import os
import time
import threading

import sys


def float_plus(f):
	try:
		return float(f)
	except:
		return 0

def int_plus(i):
	try:
		return int(i)
	except:
		return 0

class entry:

	def __init__(self,frame,entry_price=None,position=None,capital=None):

		row = 1
			
		self.sync_lock = False

		self.capital_limit = capital

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
		self.entry_choice=tk.OptionMenu(frame, self.entry_type, *sorted(self.entry_type_choices))
		self.entry_choice.grid(row=row,column=2)

		if position != None:
			self.entry_type.set(position)
			self.entry_choice["state"]="disabled"

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


	def set_share(self,value):

		self.shares.set(value)


	def get_all_infos(self):
		return self.entry_type.get(),self.entry_price.get(),self.shares.get()

	def capital_to_shares(self,capital,shares,price):

		if (self.sync_lock==False) and capital.get()!="" and price.get()!="":

			self.sync_lock = True

	
			amount = str(int(int_plus(capital.get())//float_plus(price.get())))
			#print(amount)
			shares.set(amount)
			self.stop.entry_to_stop(amount)

			self.sync_lock = False

	def shares_to_capital(self,capital,shares,price):
		if (self.sync_lock==False) and shares.get()!="" and price.get()!="":

			self.sync_lock = True

			amount = str(round(int_plus(shares.get())*float_plus(price.get()),2))

			capital.set(amount)

			#broadcast to shares. 
			self.stop.entry_to_stop(shares.get())

			self.sync_lock = False

	def price_to_capital(self,capital,shares,price):

		if (self.sync_lock==False) and price.get()!="" and shares.get()!="":

			self.sync_lock = True
	
			amount = str(round(int_plus(shares.get())*float_plus(price.get()),2))
			#print(amount)
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

	def set_stop_pannel(self,stop):
		self.stop = stop
		#self.shares.set("10")
		if self.capital_limit!=None:
			self.capital.set(self.capital_limit)

class stop:

	def __init__(self,frame,stop_price=None,total_risk=None):

		row = 1
			

		self.stop_price=stop_price

		self.totalrisk = total_risk

		self.entry = None
		self.sync_lock = False

		self.stop_type = tk.StringVar(frame)
		self.stop_type_choices = {'Mid','Ask','Bid','Trailing'}
		self.stop_type.set('Mid') 


		self.stop_level = tk.StringVar(frame)
		

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

		self.stop_level_status = tk.Label(frame,text="")
		self.stop_level_status.grid(row=row,column=3)

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

		#type,ordertype,price,shares. 




		#finalize the value

		


		self.values = []

	def entry_to_stop(self,shares):

		if (self.sync_lock==False) and self.risk_per_share.get()!="":
			self.sync_lock = True

			total = round(float_plus(self.risk_per_share.get())*int_plus(shares),2)

			self.total_risk.set(str(total))
			self.sync_lock = False


	def stoplevel_to_per_risk(self,stoplevel,perrisk,totalrisk):

		if self.entry != None:

			entry_type,entry,shares = self.entry.get_all_infos()

			if (self.sync_lock==False) and entry!="":

				self.sync_lock = True

				
				if entry_type =="Long":

					amount = round(float_plus(entry)-float_plus(stoplevel.get()),2)
				else:
					amount = round(float_plus(stoplevel.get())-float_plus(entry),2)
					

				if amount <0:
					self.stop_level_status["text"]="invalid level"
				else:
					self.stop_level_status["text"]=""
					total = round(amount*int_plus(shares),2)
					perrisk.set(amount)
					totalrisk.set(total)


					#print(totalrisk.get())

				self.sync_lock = False

	def perrisk_to_stoplevel(self,stoplevel,perrisk,totalrisk):

		if self.entry != None:
			entry_type,entry,shares = self.entry.get_all_infos()

			if (self.sync_lock==False) and entry!="":

				self.sync_lock = True
				if entry_type =="Long":
					#stop level.
					amount = str(round(float_plus(entry)-float_plus(perrisk.get()),2))
				else:
					amount = str(round(float_plus(perrisk.get())-float_plus(entry),2))
					
				total = round(float_plus(perrisk.get())*int_plus(shares),2)
				stoplevel.set(amount)
				totalrisk.set(total)

				#print(totalrisk.get())

				self.sync_lock = False

	############ THIS ONE CHANGES the entry column
	def total_risk_to_shares(self,stoplevel,perrisk,totalrisk):


		if (self.sync_lock==False) and perrisk.get()!="" and totalrisk.get()!="":

			self.sync_lock = True

			share = int(float_plus(totalrisk.get())//float_plus(perrisk.get()))

			self.entry.set_share(str(share))

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
		if P=="":
			return True
		else:
			try:
				a = float(P)
				return True
			except:
				return False

	def set_entry_pannel(self,entry):
		self.entry = entry
		self.stop_level.set(self.stop_price)

		if self.totalrisk!= None:
			self.total_risk.set(self.totalrisk)



class algo_placer:

	#if the entry type is given. lock it. 
	def __init__(self,symbol,description,entry_price=None,stop_price=None,position=None,capital=None,total_risk=None):


		#print(position,capital,total_risk)

		# root = tk.Tk() 
		# root.title("Algo Placer: "+symbol) 
		# root.geometry("780x280")
		#root.minsize(600, 400)
		#root.maxsize(900, 280)
		root = tk.Toplevel(width=780,height=280)
		self.root = root

		self.symbol = tk.Label(root,text="Symbol: "+symbol)
		self.symbol.place(x=10,y=10)

		self.symbol = tk.Label(root,text="Trigger type: "+description)
		self.symbol.place(x=10,y=30)


		############### ENTRY ################
		self.entryFrame = ttk.LabelFrame(root,text="Entry") 
		self.entryFrame.place(x=10,y=60,height=150,width=250)


		self.stopFrame = ttk.LabelFrame(root,text="Stop") 
		self.stopFrame.place(x=260,y=60,height=150,width=250)

		self.positionManager = ttk.LabelFrame(root,text="Position Management") 
		self.positionManager.place(x=510,y=60,height=150,width=250)


		self.entry = entry(self.entryFrame,entry_price,position,capital)
		self.stop = stop(self.stopFrame,stop_price,total_risk)


		self.entry.set_stop_pannel(self.stop)
		self.stop.set_entry_pannel(self.entry)

		######################################
		# self.position_management = ttk.LabelFrame(root,text="Position Management") 
		# self.position_management.place(x=440,y=60,height=100,width=200)	


		self.place= tk.Button(root ,text="Place algo",width=10,bg="#5BFF80")
		self.place.place(x=110,y=220,height=40,width=80)

		self.place= tk.Button(root ,text="Cancel",width=10)
		self.place.place(x=310,y=220,height=40,width=80)

		#self.start()

		# sm = price_updater(self.data)
		# sm.start()


	# def start(self):

	# 	self.root.mainloop() 


import tkinter as tk

class Demo1:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.button1 = tk.Button(self.frame, text = 'New Window', width = 25, command = self.new_window)
        self.button1.pack()
        self.frame.pack()

    def new_window(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = Demo2(self.newWindow)

class Demo2:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.quitButton = tk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.pack()
        self.frame.pack()

    def close_windows(self):
        self.master.destroy()

def main(): 
    root = tk.Tk()
    app = Demo1(root)
    root.mainloop()

if __name__ == '__main__':
    #main()
#symbol, break out discription. 
	algo_placer("AAPL.NQ","Breakout on Resistance on 134.45 for 60 secs",134.45,133.45,None,100)