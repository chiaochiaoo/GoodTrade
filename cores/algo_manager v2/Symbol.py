from constant import *
import tkinter as tk
#from Triggers import *

class Symbol:

	#Symbol class tracks every data related to the symbol. Output it in a dictionary form.


	"""
	'ATR': 3.6, 'OHavg': 1.551, 'OHstd': 1.556, 'OLavg': 1.623, 'OLstd': 1.445
	"""
	def __init__(self,symbol,support,resistence,stats):

		self.symbol = symbol

		self.init_open = False
		self.init_high_low = False

		self.numeric_labels = [TIMESTAMP,BID,ASK,RESISTENCE,SUPPORT,OPEN,HIGH,LOW,PREMARKETHIGH,PREMARKETLOW,STOP]

		self.data = {}
		self.tkvars = {}

		#for false range detection
		self.seen_high =0
		self.seen_low =0
		self.count = 0
		self.last_ts = 0

		self.mind = None
		self.mind_label = None

		self.tradingplan=None
		self.init_data(support,resistence,stats)

	def init_data(self,support,resistence,stats):

		for i in self.numeric_labels:
			self.data[i] = 0
			#self.tkvars[i] = tk.DoubleVar()

		for key,value in stats.items():
			self.data[key] = value

		self.data[RESISTENCE] = resistence
		self.data[SUPPORT] = support

		
	def toggle_autorange(self,Bool):
		self.data[AUTORANGE] = Bool

	def get_name(self):
		return self.symbol

	def set_mind_object(self):
		try:
			self.mind = self.tradingplan.tkvars[MIND]
			self.mind_label = self.tradingplan.tklabels[MIND]
		except:
			pass

	def set_tradingplan(self,tradingplan):
		self.tradingplan = tradingplan

	def set_mind(self,str,color=DEFAULT):

		if self.mind==None:
			self.set_mind_object()
		if self.mind!=None:
			self.mind.set(str)
			self.mind_label["background"]=color


	def false_range_detection(self,bid,ask,ts):

		#init
		if ts !=self.last_ts and self.tradingplan.data[POSITION]=="":

			if self.seen_low==0 and self.seen_high==0:
				self.seen_low = bid
				self.seen_high = ask
				self.set_mind("FRD: InProgress",DEFAULT)

			if ask>self.seen_high:
				self.seen_high = ask
			if bid<self.seen_low:
				self.seen_low = bid 

			if self.count >=1800:
				s = ((self.seen_low-self.data[SUPPORT])/self.data[SUPPORT])
				r =  ((self.data[RESISTENCE]-self.seen_high)/self.seen_high)
				if s>0.004:
					self.set_mind("FRD: abnormal support",YELLOW)
				elif r>0.004:
					self.set_mind("FRD: abnormal resistence",YELLOW)
				elif s>0.004 and r>0.004:
					self.set_mind("FRD: abnormal both levels",YELLOW)
				else:
					self.set_mind("FRD: GOOD",VERYLIGHTGREEN)

			self.last_ts = ts
			self.count +=1

		#descrepancy. 			




	def update_price(self,bid,ask,ts,AR,pos):

		try:

			if AR==True and pos==PENDING and ts<34200:
				if ask>self.data[RESISTENCE]:
					self.data[RESISTENCE]=ask
				if self.data[SUPPORT] == 0:
					self.data[SUPPORT] = bid
				if bid<self.data[SUPPORT]:
					self.data[SUPPORT] = bid
				self.tradingplan.update_symbol_tkvar()

			#print(self.data)
			#34200 openning.

			# if self.data[HIGH]==0:
			# 	self.data[HIGH] = ask
			# if self.data[LOW] ==0:
			# 	self.data[LOW] = bid 

			# if self.data[ASK]>self.data[HIGH]:
			# 	self.data[HIGH] = self.data[ASK]
			# if self.data[BID]<self.data[LOW] or self.data[LOW]==0:
			# 	self.data[LOW]= self.data[BID]

			#print("sy",self.ask,self.high,self.output)

			self.data[BID] = bid
			self.data[ASK] = ask
			self.data[TIMESTAMP] = ts

			self.false_range_detection(bid,ask,ts)
			#notify trading plan that price has changed. 

		except Exception as e:
			print(self.get_name(),"Updating price error :",e)

	def set_phigh(self,v):
		self.data[PREMARKETHIGH]=v

	def set_plow(self,v):
		self.data[PREMARKETLOW]=v

	def set_high(self,v):
		self.data[HIGH]=v
		
	def set_low(self,v):
		self.data[LOW]=v

	def set_support(self,v):
		self.data[SUPPORT]=v

	def set_resistence(self,v):
		self.data[RESISTENCE]=v


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
