from Symbol import *
from Triggers import *
from Strategy import *
from constant import*
# MAY THE MACHINE GOD BLESS THY AIM

class TradingPlan:

	def __init__(self,symbol:Symbol,entry_plan=None,entry_type=None,manage_plan=None,risk=None):

		self.symbol = symbol
		self.symbol_name = symbol.get_name()

		self.current_running_strategy = None

		self.entry_strategy_start = False

		self.entry_plan = None
		self.entry_type = None

		self.data = {}
		self.tkvars = {}


		self.numeric_labels = [ACTRISK,ESTRISK,CURRENT_SHARE,TARGET_SHARE,AVERAGE_PRICE,UNREAL,UNREAL_PSHR,REALIZED,TOTAL_REALIZED,TIMER]
		self.string_labels = [MIND,STATUS,POSITION,RISK_RATIO,SIZE_IN,ENTRYPLAN,ENTYPE,MANAGEMENTPLAN]

		self.bool_labels= [AUTORANGE,RELOAD]

		self.init_data(risk,entry_plan,entry_type,manage_plan)

	def init_data(self,risk,entry_plan,entry_type,manage_plan):

		
		for i in self.numeric_labels:
			self.data[i] = 0
			self.tkvars[i] = tk.DoubleVar(value=0)

		for i in self.string_labels:
			self.data[i] = ""
			self.tkvars[i] = tk.StringVar(value="")

		for i in self.symbol.numeric_labels:
			self.tkvars[i] = tk.DoubleVar(value=self.symbol.data[i])

		for i in self.bool_labels:
			self.data[i] = True
			self.tkvars[i] = tk.BooleanVar(value=True)

		#Non String, Non Numeric Value

		#Set some default values.
		
		self.data[ESTRISK] = risk
		self.tkvars[ESTRISK].set(risk)

		self.tkvars[ENTRYPLAN].set(entry_plan)
		self.tkvars[ENTYPE].set(entry_type)
		self.tkvars[MANAGEMENTPLAN].set(manage_plan)

		# self.entry_plan_decoder(entry_plan,entry_type)
		# self.manage_plan_decoder(manage_plan)


	## PPRO SECTION ###

	def ppro_update_price(self,data):

		pass
		
	def ppro_process_orders(self,price,shares,side):

		
		if self.tkvars[POSITION].get()=="": # 1. No position.

			self.ppro_confirm_new_order(price,shares,side)
		
		else:  # 2. Have position. 

			if self.tkvars[POSITION].get()==side: #same side.
				self.ppro_orders_loadup(price,shares,side)
			else: #opposite
				self.ppro_orders_loadoff(price,shares,side)

	def ppro_confirm_new_order(self,price,shares,side):

	def ppro_orders_loadup(self,price,shares,side):

	def ppro_orders_loadoff(self,price,shares,side):

	def ppro_order_rejection(self,data):

	## plan handler SECTION ###
	def entry_plan_decoder(self,entry_plan,entry_type):

		if entry_type ==None or entry_type ==INSTANT:
			instant = True 
		if entry_type ==INCREMENTAL:
			instant = False 

		self.tkvars[ENTYPE].set(entry_type)

		if entry_plan == BREAKANY:
			self.set_EntryStrategy(BreakAny(0,instant))
		elif entry_plan == BREAKUP:
			self.set_EntryStrategy(BreakUp(0,instant))
		elif entry_plan == BREAKDOWN:
			self.set_EntryStrategy(BreakDown(0,instant))
		elif entry_plan == BREAISH:
			self.set_EntryStrategy(BreakAny(0,instant))
		elif entry_plan == BULLISH:
			self.set_EntryStrategy(BreakAny(0,instant))
		else:
			print("unkown plan")

		self.tkvars[ENTRYPLAN].set(entry_plan)

	def manage_plan_decoder(self,manage_plan):

		if manage_plan ==None: self.tkvars[MANAGEMENTPLAN].set(NONE)

	def set_EntryStrategy(self,entry_plan:Strategy):
		self.entry_plan = entry_plan
		self.entry_plan.set_symbol(self.symbol,self)

		self.data[ENTRYPLAN] = entry_plan.get_name()
		self.tkvars[ENTRYPLAN].set(entry_plan.get_name())

	def set_ManagementStrategy(self,management_plan:Strategy):
		self.management_plan = management_plan
		self.management_plan.set_symbol(self.symbol,self)		

		self.data[MANAGEMENTPLAN] = management_plan.get_name()
		self.tkvars[MANAGEMENTPLAN].set(management_plan.get_name())

	def start_EntryStrategy(self):
		self.current_running_strategy = self.entry_plan

	def entry_strategy_done(self):
		self.current_running_strategy = self.management_plan

	def management_strategy_done(self):

		pass

	def on_finish(self,plan):
		
		if plan==self.entry_plan:
			print("Trading Plan: Entry strategy complete. Management strategy begins.")
			self.entry_strategy_done()
		elif plan==self.management_plan:
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
	b = BreakAny(3)
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