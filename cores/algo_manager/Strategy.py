from Symbol import *


class Strategy: #ABSTRACT CLASS. the beginning of a sequence, containing one or more triggers.

	def __init__(self):

		self.activated = False
		self.current_triggers = set()
		self.symbol=None
		self.tradingplan =None

	def add_initial_triggers(self,trigger):
		self.current_triggers.add(trigger)

	def set_symbol(self,symbol:Symbol,tradingplan):
		self.symbol=symbol
		self.tradingplan = tradingplan

	def update(self):
		if self.current_triggers!= None:
			for i in self.current_triggers:
				if self.symbol!=None:
					check = False
					if i.check(self.symbol):
						print(i.description)
						check = True

					if check:
						break
		if check:
			self.current_triggers = i.get_next_triggers() #replace the triggers. 
			if len(self.current_triggers)==0: #if there is no trigger, call the finish even.t
				self.on_finish()

	def on_finish(self):
		self.tradingplan.on_finish(self)				

class BreakUp(Strategy): #the parameters contains? dk. yet .
	def __init__(self):
		super().__init__()

		buyTrigger = SingleEntry(ASK,">",HIGH,0,"BUY BREAK OUT")
		self.add_initial_triggers(buyTrigger)

class AnyLevel(Strategy):
	def __init__(self):
		super().__init__()
