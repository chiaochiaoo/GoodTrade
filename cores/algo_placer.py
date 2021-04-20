import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime
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

		self.entry_price = tk.DoubleVar(frame)
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
			#self.entry_choice["state"]="disabled"

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


	def get_shares(self):

		try:
			m = int(self.shares.get())
			return m
		except:
			return 0

	def set_share(self,value):

		self.shares.set(value)


	def get_all_infos(self):
		print(self.entry_type.get(),self.order_type.get(),self.entry_price.get(),self.shares.get())
		return self.entry_type.get(),self.order_type.get(),self.entry_price.get(),self.shares.get()

	def capital_to_shares(self,capital,shares,price):

		if (self.sync_lock==False) and capital.get()!="" and price.get()!="":

			self.sync_lock = True

			try:
				amount = str(int(int_plus(capital.get())//float_plus(price.get())))
			except:
				amount = 0
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

			entry_type,order_type,entry,shares = self.entry.get_all_infos()

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
			entry_type,order_type,entry,shares = self.entry.get_all_infos()

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

			try:
				share = int(float_plus(totalrisk.get())//float_plus(perrisk.get()))
			except:
				share=0

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

	def get_stoplevel(self):

		try:
			m = float(self.stop_level.get())

			return m
		except:
			return 0

	def get_totalrisk(self):

		try:
			m = float(self.total_risk.get())

			return m
		except:
			return 0



class algo_window:

	def __init__(self,root,type_,symbol,description,entry_price,stop_price,position,capital,total_risk,data_list):

		self.id = None
		self.symbol = symbol
		self.description = description
		self.type = type_
		self.position = position
		self.data_list = data_list
		self.root=root

		tk.Label(self.root,text="Symbol: "+symbol).place(x=10,y=10)
		tk.Label(self.root,text="Trigger type: "+description).place(x=10,y=30)

		############### ENTRY ################
		self.entryFrame = ttk.LabelFrame(self.root,text="Entry") 
		self.entryFrame.place(x=10,y=60,height=150,width=250)


		self.stopFrame = ttk.LabelFrame(self.root,text="Stop") 
		self.stopFrame.place(x=260,y=60,height=150,width=250)

		self.positionManager = ttk.LabelFrame(self.root,text="Position Management") 
		self.positionManager.place(x=510,y=60,height=150,width=250)

		self.entry = entry(self.entryFrame,entry_price,position,capital)
		self.stop = stop(self.stopFrame,stop_price,total_risk)


		self.ManagementStrategy = tk.StringVar(self.positionManager)
		self.ManagementStrategy_choice = {'None','Opening BreakOut','ATR envelop'}
		self.ManagementStrategy.set('Opening BreakOut')

		tk.Label(self.positionManager ,text="Managment Strategy Select: ").grid(row=1,column=1)
		self.entry_choice=tk.OptionMenu(self.positionManager , self.ManagementStrategy, *sorted(self.ManagementStrategy_choice))
		self.entry_choice.grid(row=2,column=1)



		self.entry.set_stop_pannel(self.stop)
		self.stop.set_entry_pannel(self.entry)

	def get_info(self):

		#symbol, descrptipn,position,shares,risk. 

		entry_type,order_type,entry_price,shares = self.entry.get_all_infos()
		info = [self.symbol,self.type,"Pending",self.description,self.position,order_type,entry_price,shares,self.stop.get_totalrisk(),self.stop.get_stoplevel(),self.data_list]

		#if any of them is not set. or 0. false. 
		valid = True
		for i in info:
			if i is None or i==0:
				valid = False
				break

		return valid,info

class algo_placer:

	def on_close(self):
		self.root.destroy()

	def on_send(self):
		#print("sending information")

		#id,symbol,type,position,shares,total_risk.

		for i in self.orders_book:
			valid,info = i.get_info()

			if not valid:
				print("Not good.",info)
			else:
				#create an id. 
				id_ =info[0]+ info[1]+str(time.time())[-7:]
				info.insert(0,id_)

				info.insert(0,"New order")
				#print(info)

				if self.commlink!= None:
					self.commlink.send(info)

		#id, symbol, type, status, description, position, shares, risk$

		#in the future. wait for confirmation.
		self.root.destroy()

	#if the entry type is given. lock it. 
	def __init__(self,commlink,orders,deploy=False):

		#self.algo_commlink,type_,symbol,description,entry,stop,position,None,risk

		block = len(orders)

		root = tk.Toplevel(width=780,height=250*block+60)
		self.root = root
		self.commlink = commlink

		self.orders_book = []

		k = 0
		for i in orders:
			type_,symbol,description,entry_price,stop_price,position,capital,total_risk,datalist = i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8]
			self.frame= tk.LabelFrame(self.root)
			self.frame.place(x=0,y=250*k,height=250,width=780)
			self.orders_book.append(algo_window(self.frame,type_,symbol,description,entry_price,stop_price,position,capital,total_risk,datalist))
			k+=1

		self.place= tk.Button(root ,text="Place algo",width=10,bg="#5BFF80",command=self.on_send)
		self.place.place(x=110,y=250*block+10,height=40,width=80)

		self.place= tk.Button(root ,text="Cancel",width=10,command=self.on_close)
		self.place.place(x=310,y=250*block+10,height=40,width=80)

		if deploy:
			self.on_send()


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

#symbol, break out discription. 
	root = tk.Tk()


	#symbol,description,entry_price=None,stop_price=None,position=None,capital=None,total_risk=None)
	#algo_placer(symbol,description,entry,stop,position,None,risk)
	#algo_placer("AAPL.NQ","Breakout on Resistance on 134.45 for 60 secs",134.45,133.45,"Long",None,10.0)

#	def __init__(self,commlink,type_,symbol,description,entry_price=None,stop_price=None,position=None,capital=None,total_risk=None):
	
	algo_placer(None,[["Break up",'QQQ.NQ','Breakout on Resistance on 338.85 for 0 sec', 338.85, 336.45, 'Long', None, 5050.0],["Break down",'QQQ.NQ','Breakout on Support on 338.85 for 0 sec', 338.85, 336.45, 'Long', None, 5050.0]])
	root.mainloop()