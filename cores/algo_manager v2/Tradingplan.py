from Symbol import *
from Triggers import *
from Strategy import *
from constant import*
# MAY THE MACHINE GOD BLESS THY AIM

class TradingPlan:

	def __init__(self,symbol:Symbol,risk=None):

		self.symbol = symbol
		self.symbol_name = symbol.get_name()


		self.current_running_strategy = None

		self.entry_strategy_start = False

		self.entry_strategy = None
		self.manage_strategy = None

		self.entry_startegy_name = None
		self.manage_startegy_name = None 

		self.data = {}
		self.tkvars = {}

		self.numeric_labels = [ACTRISK,ESTRISK,CURRENT_SHARE,TARGET_SHARE,AVERAGE_PRICE,UNREAL,UNREAL_PSHR,REALIZED,TOTAL_REALIZED,TIMER]
		self.string_labels = [MIND,STATUS,POSITION,MANASTRAT,ENSTRAT,RISK_RATIO,SIZE_IN]

		self.init_data(risk)

	def init_data(self,risk):

		for i in self.numeric_labels:
			self.data[i] = 0
			self.tkvars[i] = tk.DoubleVar(value=0)

		for i in self.string_labels:
			self.data[i] = ""
			self.tkvars[i] = tk.StringVar(value=" ")

		for i in self.symbol.numeric_labels:
			self.data[i] = 0
			self.tkvars[i] = tk.DoubleVar(value=0)

		#Non String, Non Numeric Value

		self.tkvars[AUTORANGE] = tk.BooleanVar(value=True)
		
		self.data[ESTRISK] = risk
		self.tkvars[ESTRISK].set(risk)

	def set_EntryStrategy(self,entry_strategy:Strategy):
		self.entry_strategy = entry_strategy
		self.entry_strategy.set_symbol(self.symbol,self)

		self.data[ENSTRAT] = entry_strategy.get_name()
		self.tkvars[ENSTRAT].set(entry_strategy.get_name())


	def set_ManagementStrategy(self,manage_strategy:Strategy):
		self.manage_strategy = manage_strategy
		self.manage_strategy.set_symbol(self.symbol,self)		

		self.data[MANASTRAT] = manage_strategy.get_name()
		self.tkvars[MANASTRAT].set(manage_strategy.get_name())

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
	aapl.set_phigh(16)
	aapl.set_plow(15)

	b = BreakDown(0)
	#b = BreakUp(0)
	b = AnyLevel(3)
	TP.set_EntryStrategy(b)
	TP.start_EntryStrategy()

	
	aapl.update_price(10,10,0)
	aapl.update_price(11,11,1)
	aapl.update_price(12,12,2)
	aapl.update_price(13,13,3)
	aapl.update_price(14,14,4)
	aapl.update_price(15,15,5)
	##### DECRESE#######
	aapl.update_price(5,5,6)
	aapl.update_price(13,13,7)

	aapl.update_price(10,10,8)
	###### INCREASE #############
	aapl.update_price(11,11,9)
	aapl.update_price(12,12,10)
	aapl.update_price(13,13,11)
	aapl.update_price(14,14,12)
	aapl.update_price(15,15,13)
	aapl.update_price(16,16,14)
	aapl.update_price(17,17,15)
	aapl.update_price(18,18,16)
	aapl.update_price(19,19,17)