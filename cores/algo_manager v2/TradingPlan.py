from Symbol import *
from Triggers import *
from Strategy import *
from constant import*

import tkinter as tk
# MAY THE MACHINE GOD BLESS THY AIM

class TradingPlan:

	def __init__(self,symbol:Symbol,entry_plan=None,entry_type=None,manage_plan=None,risk=None,ppro_out=None):

		self.symbol = symbol

		self.symbol.set_tradingplan(self)
		self.symbol_name = symbol.get_name()

		self.current_running_strategy = None
		self.entry_strategy_start = False

		self.entry_plan = None
		self.entry_type = None

		self.ppro_out = ppro_out

		self.expect_orders = False


		self.data = {}
		self.tkvars = {}

		self.tklabels= {} ##returned by UI.

		self.hodings = []
		self.current_price_level = 0

		self.numeric_labels = [ACTRISK,ESTRISK,CURRENT_SHARE,TARGET_SHARE,AVERAGE_PRICE,STOP_LEVEL,UNREAL,UNREAL_PSHR,REALIZED,TOTAL_REALIZED,TIMER,PXT1,PXT2,PXT3]
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


		self.data[STATUS] = PENDING
		self.tkvars[STATUS].set(PENDING)

		# self.entry_plan_decoder(entry_plan,entry_type)
		# self.manage_plan_decoder(manage_plan)


	"""
	PPRO SECTIONd 
	"""


	def ppro_update_price(self,bid,ask,ts):


		self.symbol.update_price(bid,ask,ts,self.tkvars[AUTORANGE].get())
		self.update_symbol_tkvar()

		#check stop. 
		if self.data[POSITION]!="":
			self.check_stop(bid,ask)

		#check triggers
		if self.current_running_strategy!=None:
			self.current_running_strategy.update()
		#check if stop is met. OH! Facil

	def check_stop(bid,ask):

		if self.data[POSITION] == LONG:
			if bid<self.data[STOP_LEVEL]:
				print("flatten")
		elif self.data[POSITION] == SHORT:
			if ask>self.data[STOP_LEVEL]:
				print("flatten")

	def ppro_process_orders(self,price,shares,side):

		
		if self.tkvars[POSITION].get()=="": # 1. No position.

			if self.expect_orders==True:
				self.ppro_confirm_new_order(price,shares,side)
			else:
				print("unexpected orders on",self.symbol_name)
		
		else:  # 2. Have position. 

			if self.tkvars[POSITION].get()==side: #same side.
				self.ppro_orders_loadup(price,shares,side)
			else: #opposite
				self.ppro_orders_loadoff(price,shares,side)



	def ppro_confirm_new_order(self,price,shares,side):


		"""set the state as running, then load up"""
		self.mark_algo_status(RUNNING)
		self.ppro_orders_loadup(price,shares,side)


	def ppro_orders_loadup(self,price,shares,side):

		current = self.data[CURRENT_SHARE]

		self.data[CURRENT_SHARE] = self.data[CURRENT_SHARE] + shares

		if current ==0:
			self.data[AVERAGE_PRICE] = round(price,3)
		else:
			self.data[AVERAGE_PRICE]= round(((self.data[AVERAGE_PRICE]*current)+(price*shares))/self.data[CURRENT_SHARE],3)

		for i in range(shares):
			self.holdings.append(price)



	def ppro_orders_loadoff(self,price,shares,side):

		current = self.data[CURRENT_SHARE]

		self.data[CURRENT_SHARE] = current-shares	
		
		gain = 0

		if self.data[POSITION] == LONG:
			for i in range(shares):
				try:
					gain += price-self.holdings.pop()
				except:
					print("Holding calculation error,holdings are empty.")
		elif self.position[id_]=="Short":
			for i in range(shares):
				try:
					gain += self.holdings.pop() - price	
				except:
					print("Holding calculation error,holdings are empty.")	

		self.data[REALIZED]+=gain
		self.data[REALIZED]= round(self.data[REALIZED],2)

		self.adjusting_risk()

		print(self.symbol_name," sold:",shares," current shares:",self.data[CURRENT_SHARE],"realized:",self.data[REALIZED])

		#finish a trade if current share is 0.

		if self.data[CURRENT_SHARE] <= 0:
			self.data[UNREAL] = 0
			self.data[UNREAL_PSHR] = 0

			#mark it done.
			self.mark_algo_status(DONE)


	def ppro_order_rejection(self):

		self.mark_off_algo(REJECTED)


	"""
	#risk related ##
	"""

	def adjusting_risk(self):

		if self.data[POSITION] == LONG:
			self.DATA[ACTRISK] = round(((self.data[AVERAGE_PRICE]-self.data[STOP_LEVEL])*self.data[CURRENT_SHARE]),2)
		else:
			self.DATA[ACTRISK] = round(((self.data[STOP_LEVEL]-self.data[AVERAGE_PRICE])*self.data[CURRENT_SHARE]),2)

		diff = self.DATA[ACTRISK]-self.DATA[ESTRISK]
		ratio = diff/self.DATA[ESTRISK]

		##change color and change text.

		self.tklabels[RISK_RATIO] = hexcolor_green_to_red(ratio)
		self.tkvars[RISK_RATIO].set(str(self.DATA[ACTRISK])+"/"+str(self.DATA[ESTRISK]))

		if self.data[CURRENT_SHARE] == 0:
			self.tklabels[RISK_RATIO]["background"] = DEFAULT


	"""
	UI related 
	"""
	

	def update_symbol_tkvar(self):
		self.tkvars[SUPPORT].set(self.symbol.get_support())
		self.tkvars[RESISTENCE].set(self.symbol.get_resistence())

	def update_displays(self):

		self.tkvars[CURRENT_SHARE].set(str(self.data[CURRENT_SHARE])+"/"+str(self.data[TARGET_SHARE]))
		self.tkvars[REALIZED].set(str(self.data[REALIZED]))
		self.tkvars[UNREAL].set(str(self.data[UNREAL]))
		self.tkvars[UNREAL_PSHR].set(str(self.data[UNREAL_PSHR]))
		self.tkvars[AVERAGE_PRICE].set(self.data[AVERAGE_PRICE])

		#check color.f9f9f9

		self.tklabels[REALIZED]["background"]

		self.tklabels[UNREAL]["background"]

		if self.data[UNREAL_PSHR]>0:
			self.tklabels[UNREAL_PSHR]["background"] = STRONGGREEN
			self.tklabels[UNREAL]["background"] = STRONGGREEN
		elif self.unrealized_pshr[id_]<0:
			self.tklabels[UNREAL_PSHR]["background"] = STRONGRED
			self.tklabels[UNREAL]["background"] = STRONGRED
		else:
			self.tklabels[UNREAL_PSHR]["background"] = DEFAULT
			self.tklabels[UNREAL]["background"] =DEFAULT

		if self.realized[id_]==0:
			self.tklabels[REALIZED]["background"]["background"] = DEFAULT
		elif self.realized[id_]>0:
			self.tklabels[REALIZED]["background"]["background"] = STRONGGREEN
		elif self.realized[id_]<0:
			self.tklabels[REALIZED]["background"]["background"] = STRONGRED

		current_level = self.current_price_level

		self.tklabels[pxt1]
		if  current_level==1:
			self.tklabels[pxt1]["background"] = LIGHTYELLOW
			self.tklabels[pxt2]["background"] = DEFAULT
			self.tklabels[pxt3]["background"] = DEFAULT
		elif  current_level==2:
			self.tklabels[pxt1]["background"] = DEFAULT
			self.tklabels[pxt2]["background"] = LIGHTYELLOW
			self.tklabels[pxt3]["background"] = DEFAULT
		elif  current_level==3:
			self.tklabels[pxt1]["background"] = DEFAULT
			self.tklabels[pxt2]["background"] = DEFAULT
			self.tklabels[pxt3]["background"] = LIGHTYELLOW
		else:
			self.tklabels[pxt1]["background"] = DEFAULT
			self.tklabels[pxt2]["background"] = DEFAULT
			self.tklabels[pxt3]["background"] = DEFAULT	



	def mark_algo_status(self,status):

		self.data[STATUS] = status
		self.tkvars[STATUS].set(status)

		if status == REJECTED:
			self.tklabels[STATUS]["background"] = "red"

		elif status == DONE:

			self.tklabels[STATUS]["background"] = DEFAULT
			self.data[POSITION] = ""
			self.tkvars[POSITION].set("")

			#if reload is on, turn it back on.
		# elif status == CANCELED:#canceled 

		# 	if self.order_tkstring[id_]["algo_status"].get() == "Pending":
		# 		self.order_tkstring[id_]["algo_status"].set(status)

	"""
	DATA MANAGEMENT 
	"""

	
	def get_risk(self):

		return self.data[ESTRISK]

	def get_data(self):
		return self.data

	"""
	Plan Handler
	"""

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


if __name__ == '__main__':

	#TEST CASES for trigger.
	root = tk.Tk() 
	aapl = Symbol("aapl")
	TP = TradingPlan(aapl)
	aapl.set_tradingplan(TP)
	aapl.set_phigh(16)
	aapl.set_plow(15)

	b = BreakUp(0,False,aapl,TP)
	#b = BreakUp(0)
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


	root.mainloop()