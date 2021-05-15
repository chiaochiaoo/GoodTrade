from constant import *
from Symbol import *
from Triggers import *
import sys, inspect
from Util_functions import *

# "Omnissiah, Omnissiah.

# From the Bleakness of the mind
# Omnissiah save us
# From the lies of the Antipath
# Circuit preserve us
# From the Rage of the Beast
# Iron protect us
# From the temptations of the Fleshlord
# Silica cleanse us
# From the Ravages of the Destroyer
# Anima Shield us

# Machine God Set Us Free
# Omnissiah, Omnissiah."

class Strategy: 

	"""
	ABSTRACT CLASS. the beginning of a sequence, containing one or more triggers.

	function:

	update : for each trigger.
		   -  Can be used for updating itself too (when overwrite.) 
	initialize : 
	"""
	def __init__(self,name,symbol:Symbol,tradingplan):

		self.strategy_name = name
		self.current_triggers = set()
		self.initial_triggers = set()
		self.symbol=None
		self.tradingplan =None
		self.ppro_out = None
		self.timer = 0
		self.all_triggers = []

		self.mind = None
		self.mind_label = None

		self.risk = 0

		self.set_symbol(symbol,tradingplan)

	def get_name(self):
		return self.strategy_name

	def add_initial_triggers(self,trigger):
		self.current_triggers.add(trigger)
		self.initial_triggers.add(trigger)
		trigger.set_symbol(self.symbol, self.tradingplan, self.ppro_out)


	def set_symbol(self,symbol:Symbol,tradingplan):
		self.symbol=symbol
		self.symbol_name = symbol.get_name()
		self.tradingplan = tradingplan
		self.ppro_out = self.tradingplan.ppro_out
		self.risk = self.tradingplan.get_risk()

	def restart(self):

		self.current_triggers = set()
		for i in self.initial_triggers:
			self.current_triggers.add(i)

	def update(self):

		if len(self.current_triggers)>0:
			check = False
			for i in self.current_triggers:
				if self.symbol!=None:
					check = False
					if i.check_conditions():
						check = True
					if check:
						break
			if check:
				self.current_triggers = i.get_next_triggers() #replace the triggers. 
				#log_print(self.current_triggers)
				for i in self.current_triggers:
					i.set_symbol(self.symbol,self.tradingplan,self.ppro_out)

				if len(self.current_triggers)==0: #if there is no trigger, call the finish even.t
					self.on_finish()

		else:
			log_print("Strategy: nothing to trigger.")

	def on_finish(self):
		log_print(self.strategy_name+" completed")
		self.tradingplan.on_finish(self)	
		self.restart()

	def set_mind(self,str,color=DEFAULT):

		if self.mind==None:
			self.set_mind_object()
		if self.mind!=None:
			self.mind.set(str)
			self.mind_label["background"]=color

	def clear_mind(self):
		self.set_mind(" ",DEFAULT)

	def set_mind_object(self):
		try:
			self.mind = self.tradingplan.tkvars[MIND]
			self.mind_label = self.tradingplan.tklabels[MIND]
		except:
			pass

	def update_on_pricechanging(self):
		pass

	def update_on_loadingup(self):
		pass

	def update_on_start(self):
		pass


"""ENTRY PLAN"""
class BreakUp(Strategy): #the parameters contains? dk. yet .  #Can make single entry, or multiple entry. 
	def __init__(self,timer,repeat,symbol,tradingplan):
		super().__init__("Entry : Break up",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		buyTrigger = Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",timer,repeat,LONG,self.ppro_out)

		self.add_initial_triggers(buyTrigger)

class BreakDown(Strategy): #the parameters contains? dk. yet .  #Can make single entry, or multiple entry. 
	def __init__(self,timer,repeat,symbol,tradingplan):
		super().__init__("Entry : Break up",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		sellTrigger = Purchase_trigger([[SYMBOL_DATA,BID,"<",SYMBOL_DATA,SUPPORT]],RESISTENCE,self.risk,"break down",timer,repeat,SHORT,self.ppro_out)

		self.add_initial_triggers(sellTrigger)

class BreakAny(Strategy):
	def __init__(self,timer,repeat,symbol,tradingplan):

		super().__init__("Entry : Break Any",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		buyTrigger = Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",timer,repeat,LONG,self.ppro_out)
		sellTrigger = Purchase_trigger([[SYMBOL_DATA,BID,"<",SYMBOL_DATA,SUPPORT]],RESISTENCE,self.risk,"break down",timer,repeat,SHORT,self.ppro_out)

		self.add_initial_triggers(buyTrigger)
		self.add_initial_triggers(sellTrigger)

class Bullish(Strategy):
	def __init__(self,timer,repeat,symbol,tradingplan):

		super().__init__("Entry :Bullish",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		buyTrigger = Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",timer,repeat,LONG,self.ppro_out)


		#self,description,trigger_timer:int,trigger_limit
		transitional_trigger = AbstractTrigger("transitional trigger to long.",[[SYMBOL_DATA,BID,"<",SYMBOL_DATA,SUPPORT]],0,1,"Waiting for long reversal")
		buyreversalTrigger = Purchase_trigger([[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],LOW,self.risk,"buy reversal",timer,repeat,LONG,self.ppro_out)
		
		transitional_trigger.add_next_trigger(buyreversalTrigger)

		self.add_initial_triggers(buyTrigger)
		self.add_initial_triggers(transitional_trigger)

class DipBuyer(Strategy):
	def __init__(self,timer,repeat,symbol,tradingplan):

		super().__init__("Entry :Bullish",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		buyTrigger = Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",timer,repeat,LONG,self.ppro_out)
		sellTrigger = Purchase_trigger([[SYMBOL_DATA,BID,"<",SYMBOL_DATA,SUPPORT]],RESISTENCE,self.risk,"break down",timer,repeat,SHORT,self.ppro_out)

		self.add_initial_triggers(buyTrigger)
		self.add_initial_triggers(sellTrigger)

""" MANAGEMENT PLAN"""
class ThreePriceTargets(Strategy):

	def __init__(self,symbol,tradingplan):

		super().__init__("Management: Three pxt targets",symbol,tradingplan)

		self.manaTrigger = Three_price_trigger("manage",self.ppro_out)

		self.add_initial_triggers(self.manaTrigger)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		###upon activating, reset all parameters. 

	def update_on_loadingup(self): #call this whenever the break at price changes. 

		price = self.tradingplan.data[AVERAGE_PRICE]
		coefficient = 1
		good = False

		if self.tradingplan.data[POSITION]==LONG:
			ohv = self.symbol.data[OHAVG]
			ohs =  self.symbol.data[OHSTD]
			#log_print(self.data_list[id_],type(ohv),ohs,type(price))
			if ohv!=0:
				#self.tradingplan[id_][0] = price
				self.tradingplan.data[PXT1] = round(price+ohv*0.2*coefficient,2)
				self.tradingplan.data[PXT2] = round(price+ohv*0.5*coefficient,2) #round(self.tradingplan.data[PXT1]+0.02,2) 
				self.tradingplan.data[PXT3] = round(price+ohv*0.8*coefficient,2) #round(self.tradingplan.data[PXT2]+0.02,2) #
				good = True
		elif self.tradingplan.data[POSITION]==SHORT:
			olv = self.symbol.data[OLAVG]
			ols = self.symbol.data[OLSTD]
			if olv!=0:
				#self.price_levels[id_][0] = price
				self.tradingplan.data[PXT1] = round(price-olv*0.2*coefficient,2)
				self.tradingplan.data[PXT2] = round(price-olv*0.5*coefficient,2) #round(self.tradingplan.data[PXT1]-0.02,2)  #
				self.tradingplan.data[PXT3] = round(price-olv*0.8*coefficient,2) #round(self.tradingplan.data[PXT2]-0.02,2) #
				good = True
				
		#set the price levels. 
		#log_print(id_,"updating price levels.",price,self.price_levels[id_][1],self.price_levels[id_][2],self.price_levels[id_][3])
		if good:
			self.tradingplan.tkvars[AUTOMANAGE].set(True)
			self.tradingplan.tkvars[PXT1].set(self.tradingplan.data[PXT1])
			self.tradingplan.tkvars[PXT2].set(self.tradingplan.data[PXT2])
			self.tradingplan.tkvars[PXT3].set(self.tradingplan.data[PXT3])

			log_print(self.symbol_name,"price target adjusted:",self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])
		else:
			self.tradingplan.tkvars[AUTOMANAGE].set(False)


		#log_print(self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])
	def update_on_start(self):
		self.manaTrigger.total_reset()
		self.tradingplan.current_price_level = 1
		self.set_mind("")
# clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)

# log_print(clsmembers)

# for i in clsmembers:
# 	log_print(i)