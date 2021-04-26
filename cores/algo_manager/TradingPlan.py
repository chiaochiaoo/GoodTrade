from Symbol import *
from Triggers import *




class TradingPlan:

	def __init__(self,symbol:Symbol,risk=None):

		self.symbol = symbol

		self.risk = risk
		self.current_share = 0
		self.target_share = 0

		#using the parameters from the tradingplan, create the associated triggers, and trigger sequence. 
		# self.current_triggers=[]

		self.trage_stage = "Pending"

		self.current_running_strategy = None

		self.entry_strategy_start = False

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

