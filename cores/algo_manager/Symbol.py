from constant import *


class Symbol:

	#Symbol class tracks every data related to the symbol. Output it in a dictionary form.
	def __init__(self,symbol):

		self.symbol = symbol

		self.bid = 0
		self.ask = 0

		self.support = 0
		self.resistence = 0

		self.open = 0
		self.high = 0
		self.low = 0
		self.data = {}

		self.data[BID]= self.bid
		self.data[ASK]=	self.ask
		self.data[RESISTENCE] = self.resistence
		self.data[SUPPORT] = self.support
		self.data[OPEN] = self.open
		self.data[HIGH] = self.high
		self.data[LOW] = self.low

		# self.total_realized = 0
		# self.number_trades = 0

		# self.triggers=[]

	def update_price(self,bid,ask,ts):

		self.bid = bid
		self.ask = ask
		self.timestamp = ts

		remove = []
		for i in self.triggers:
			if i.check():
				#print(1)
				remove.append(i)

		#execute the actions on remove.
		#remove it from triggers.
		for i in remove:
			i.trigger_event()
			self.triggers.remove(i)

	def get_data(self):
		return self.data

	def get_bid(self):
		return self.bid

	def get_ask(self):
		return self.ask

	def get_time(self):
		return self.timestamp

	# def add_trigger(self,info,type_,trigger_price,timer):
	# 	self.triggers.append(trigger(self,info,type_,trigger_price,timer))
