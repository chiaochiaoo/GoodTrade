from Symbol import *
from Triggers import *
#### Trading plan is where all the triggers, conditions are.###
#### Orders on a symbol create a basic trading plan. and modifying it chainging the plan.




class TradingPlan:

	def __init__(self,symbol:Symbol,risk=None):

		self.symbol = symbol
		self.symbol_name = symbol.get_name()

		### TRADING RELATED INFO ###
		self.risk = risk
		
		self.position = None
		self.current_share = 0
		self.target_share = 0

		self.matured = False
		self.activation = False
		#using the parameters from the tradingplan, create the associated triggers, and trigger sequence. 
		# self.current_triggers=[]

		self.trage_stage = "Pending"

		self.stop_order = False
		self.stop_order_id = None
		self.current_running_strategy = None

		self.init_stop = False
		self.stop_trigger = None
		self.entry_strategy_start = False

		#using the parameters from the tradingplan, create the associated triggers, and trigger sequence. 
		self.current_triggers=[]

	def update(self):
		remove = []
		for i in self.current_triggers:
			if i.check():
				#print(1)
				remove.append(i)
		#execute the actions on remove.
		#remove it from triggers.
		for i in remove:
			i.trigger_event()
			self.current_triggers.remove(i)
		self.entry_strategy = None
		self.manage_strategy = None

	def set_EntryStrategy(self,entry_strategy:Strategy):
		self.entry_strategy = entry_strategy
		self.entry_strategy.set_symbol(self.symbol)

	def start_EntryStrategy(self):
		self.current_running_strategy = self.entry_strategy

	def update(self): #let the strategy know it is updated. 

		#just coordinate between the strategy.
		if self.current_running_strategy!=None:
			self.current_running_strategy.update()

	def entry_strategy_done(self):
		self.current_running_strategy = self.manage_strategy
		

	def add_trigger(self,t:Trigger):
		self.current_triggers.append(t)

if __name__ == '__main__':

	#TEST CASES for trigger.
	aapl = Symbol("aapl")

	TP = TradingPlan(aapl)
	aapl.set_tradingplan(TP)
	aapl.set_high(15)
	buyTrigger = SingleEntry(aapl,ASK,">",HIGH,0,"BUY HIGH")

	TP.add_trigger(buyTrigger)
	
	aapl.update_price(10,10,0)
	aapl.update_price(11,11,1)
	aapl.update_price(12,12,2)
	aapl.update_price(13,13,3)
	aapl.update_price(14,14,4)
	aapl.update_price(15,15,5)
	##### DECRESE#######
	aapl.update_price(14,14,6)
	aapl.update_price(13,13,7)
	aapl.update_price(12,12,6)
	aapl.update_price(11,11,7)
	aapl.update_price(10,10,8)
	###### INCREASE #############
	aapl.update_price(11,11,9)
	aapl.update_price(12,12,10)
	aapl.update_price(13,13,11)
	aapl.update_price(14,14,11)
	aapl.update_price(15,15,12)
	aapl.update_price(16,16,13)
	aapl.update_price(17,17,14)
	aapl.update_price(18,18,15)
	aapl.update_price(19,19,16)
### EVENT CLASS. TRIGGER EVENT. ###
# class Trade:
# 	def __init__(self,symbol,position,shares,price=None,rationale=None):

# 		self.matured = False
# 		self.activation = False
# 		self.symbol = symbol
# 		self.position = position
# 		self.shares = shares
# 		self.price = None

# 		self.stop_order = False
# 		self.stop_order_id = None

# 	def place_trade(self): #ask ppro to place orders.
# 		pas