from Symbol import *
from Triggers import *
from Strategy import *

# MAY THE 

class TradingPlan:

	def __init__(self,symbol:Symbol,risk=None):

		self.symbol = symbol
		self.symbol_name = symbol.get_name()

		self.risk = risk
		self.position = None
		self.current_share = 0
		self.target_share = 0

		self.trade_stage = "Pending"

		self.current_running_strategy = None

		self.entry_strategy_start = False

		self.entry_strategy = None
		self.manage_strategy = None

	def set_EntryStrategy(self,entry_strategy:Strategy):
		self.entry_strategy = entry_strategy
		self.entry_strategy.set_symbol(self.symbol,self)

	def start_EntryStrategy(self):
		self.current_running_strategy = self.entry_strategy

	def entry_strategy_done(self):
		self.current_running_strategy = self.manage_strategy

	def management_strategy_done(self):

		pass

	def on_finish(self,plan):
		
		if plan==self.entry_strategy:
			print("Trading Plan: Entry strategy complete. Management strategy begins.")
			self.entry_strategy_done()
		elif plan==self.manage_strategy:
			self.management_strategy_done()
		else:
			print("Trading Plan: UNKONW CALL FROM Strategy")

	def update(self): #let the strategy know it is updated. 

		#just coordinate between the strategy.
		if self.current_running_strategy!=None:
			self.current_running_strategy.update()



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