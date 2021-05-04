from constant import *
import tkinter as tk
#from Triggers import *

class Symbol:

	#Symbol class tracks every data related to the symbol. Output it in a dictionary form.
	def __init__(self,symbol,support=0,resistence=0):

		self.symbol = symbol

		self.init_open = False
		self.init_high_low = False

		self.numeric_labels = [TIMESTAMP,BID,ASK,RESISTENCE,SUPPORT,OPEN,HIGH,LOW,PREMARKETHIGH,PREMARKETLOW,STOP]

		self.data = {}
		self.tkvars = {}

		self.tradingplan=None
		self.init_data(support,resistence)

	def init_data(self,support,resistence):

		for i in self.numeric_labels:
			self.data[i] = 0
			#self.tkvars[i] = tk.DoubleVar()

		self.data[RESISTENCE] = resistence
		self.data[SUPPORT] = support

		
	def toggle_autorange(self,Bool):
		self.data[AUTORANGE] = Bool

	def get_name(self):
		return self.symbol

	def set_tradingplan(self,tradingplan):
		self.tradingplan = tradingplan

	def update_price(self,bid,ask,ts,AR,pos):

		if AR==True and pos=="": #and ts<34200:
			if ask>self.data[RESISTENCE]:
				self.data[RESISTENCE]=ask
			if self.data[SUPPORT] == 0:
				self.data[SUPPORT] = bid
			if bid<self.data[SUPPORT]:
				self.data[SUPPORT] = bid

		#34200 openning.

		# if self.data[HIGH]==0:
		# 	self.data[HIGH] = ask
		# if self.data[LOW] ==0:
		# 	self.data[LOW] = bid 

		if self.data[ASK]>self.data[HIGH]:
			self.data[HIGH] = self.data[ASK]
		if self.data[BID]<self.data[LOW] or self.data[LOW]==0:
			self.data[LOW]= self.data[BID]

		#print("sy",self.ask,self.high,self.output)

		self.data[BID] = bid
		self.data[ASK] = ask
		self.data[TIMESTAMP] = ts

		self.tradingplan.update_symbol_tkvar()
		#notify trading plan that price has changed. 


	def set_phigh(self,v):
		self.data[PREMARKETHIGH]=v

	def set_plow(self,v):
		self.data[PREMARKETLOW]=v

	def set_high(self,v):
		self.data[HIGH]=v
		
	def set_low(self,v):
		self.data[LOW]=v

	def get_data(self):
		return self.data

	def get_support(self):
		return self.data[SUPPORT]

	def get_resistence(self):
		return self.data[RESISTENCE]

	def get_bid(self):
		return self.data[BID]

	def get_ask(self):
		return self.data[ASK]

	def get_time(self):
		return self.data[TIMESTAMP]
	# def add_trigger(self,info,type_,trigger_price,timer):
	# 	self.triggers.append(trigger(self,info,type_,trigger_price,timer))
