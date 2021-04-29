from constant import *
#from Triggers import *

class Symbol:

	#Symbol class tracks every data related to the symbol. Output it in a dictionary form.
	def __init__(self,symbol):

		self.symbol = symbol

		self.init_open = False
		self.init_high_low = False

		self.data = {}

		self.data[TIMESTAMP]=0

		self.data[BID]= 0
		self.data[ASK]=	0
		self.data[RESISTENCE] = 0
		self.data[SUPPORT] = 0
		self.data[OPEN] = 0
		self.data[HIGH] =0
		self.data[LOW] = 0

		self.data[PREMARKETHIGH] = 0
		self.data[PREMARKETLOW] = 0

		# self.total_realized = 0
		# self.number_trades = 0

		self.tradingplan=None


	def get_name(self):
		return self.symbol

	def set_tradingplan(self,tradingplan):
		self.tradingplan = tradingplan

	def update_price(self,bid,ask,ts):

		# if self.data[HIGH]==0:
		# 	self.data[HIGH] = ask
		# if self.data[LOW] ==0:
		# 	self.data[LOW] = bid 

		# if self.data[ASK]>self.data[HIGH]:
		# 	self.data[HIGH] = self.data[ASK]
		# if self.data[BID]<self.data[LOW]:
		# 	self.data[LOW]= self.data[BID]

		#print("sy",self.ask,self.high,self.output)

		self.data[BID] = bid
		self.data[ASK] = ask
		self.data[TIMESTAMP] = ts
		#notify trading plan that price has changed. 

		if self.tradingplan!=None:
			self.tradingplan.update()


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

	def get_bid(self):
		return self.data[BID]

	def get_ask(self):
		return self.data[ASK]

	def get_time(self):
		return self.data[TIMESTAMP]
	# def add_trigger(self,info,type_,trigger_price,timer):
	# 	self.triggers.append(trigger(self,info,type_,trigger_price,timer))
