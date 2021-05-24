from constant import *
from Symbol import *
from Triggers import *

from Util_functions import *

#import sys, inspect
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

	def set_symbol(self,symbol:Symbol,tradingplan):
		self.symbol=symbol
		self.symbol_name = symbol.get_name()
		self.tradingplan = tradingplan
		self.ppro_out = self.tradingplan.ppro_out
		self.risk = self.tradingplan.get_risk()

	def get_name(self):
		return self.strategy_name

	def add_initial_triggers(self,trigger):
		self.initial_triggers.add(trigger)
		trigger.set_symbol(self.symbol, self.tradingplan, self.ppro_out)

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
		self.tradingplan.on_finish(self)	
		self.restart()

	def restart(self):
		self.current_triggers = set()
		for i in self.initial_triggers:
			self.current_triggers.add(i)

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


	def print_current_triggers(self):

		st = self.symbol_name +" Triggers sets: "+self.strategy_name
		for i in self.current_triggers:
			if i.get_trigger_state()==True:
				st += " " +i.description
		log_print(st)

	""" for entry plan only """


class EntryStrategy(Strategy):

	def __init__(self,name,symbol:Symbol,tradingplan):
		super().__init__(name,symbol,tradingplan)

		self.deployed = False

	def on_loading_up(self):
		pass

	def on_start(self):
		self.manaTrigger.total_reset()
		self.tradingplan.current_price_level = 1
		self.set_mind("")


	""" REQUIRED: Fill in the conditions for each type of triggers. 
	   Will determine what triggers to use should the system decides to reload. """

	def reload_triggers(self):
		pass

	""" don't total reset here. """
	def on_deploying(self):

		self.current_triggers = set()

		for i in self.initial_triggers:
			self.current_triggers.add(i)

		if self.deployed:
			self.on_redeploying()

		self.print_current_triggers()
		self.deployed = True


	def on_redeploying(self):
		pass

	def on_finish(self):

		super().on_finish()
		#self.reload_triggers()

		"""depending on the conditions, refresh the used triggers."""

""" PLANS : seperate management plan and entry plan"""

"""ENTRY PLAN"""
class BreakUp(EntryStrategy): #the parameters contains? dk. yet .  #Can make single entry, or multiple entry. 
	def __init__(self,timer,repeat,symbol,tradingplan):
		super().__init__("Entry : Break up",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		self.buyTrigger = Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",timer,repeat,LONG,self.ppro_out)

		self.add_initial_triggers(self.buyTrigger)

	def on_redeploying(self):

		if not self.buyTrigger.pre_deploying_check():
			self.buyTrigger.total_reset()



class BreakDown(EntryStrategy): #the parameters contains? dk. yet .  #Can make single entry, or multiple entry. 
	def __init__(self,timer,repeat,symbol,tradingplan):
		super().__init__("Entry : Break up",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		self.sellTrigger = Purchase_trigger([[SYMBOL_DATA,BID,"<",SYMBOL_DATA,SUPPORT]],RESISTENCE,self.risk,"break down",timer,repeat,SHORT,self.ppro_out)

		self.add_initial_triggers(self.sellTrigger)


	def on_redeploying(self):

		if not self.sellTrigger.pre_deploying_check():
			self.sellTrigger.total_reset()


class BreakAny(EntryStrategy):
	def __init__(self,timer,repeat,symbol,tradingplan):

		super().__init__("Entry : Break Any",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		self.buyTrigger = Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",timer,repeat,LONG,self.ppro_out)
		self.sellTrigger = Purchase_trigger([[SYMBOL_DATA,BID,"<",SYMBOL_DATA,SUPPORT]],RESISTENCE,self.risk,"break down",timer,repeat,SHORT,self.ppro_out)

		self.add_initial_triggers(self.buyTrigger)
		self.add_initial_triggers(self.sellTrigger)

	def on_redeploying(self):

		""" if one is used and does not vilate the entry condition (failed trade) reset it."""
		if self.sellTrigger.get_trigger_state()==False and not self.sellTrigger.pre_deploying_check():
			self.sellTrigger.total_reset()

		if self.buyTrigger.get_trigger_state()==False and not self.buyTrigger.pre_deploying_check():
			self.buyTrigger.total_reset()

class Bullish(EntryStrategy):
	def __init__(self,timer,repeat,symbol,tradingplan):

		super().__init__("Entry :Bullish",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		self.buyTrigger = Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",timer,repeat,LONG,self.ppro_out)
		self.add_initial_triggers(self.buyTrigger)

		self.transitional_trigger = AbstractTrigger("transitional trigger to long.",[[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,SUPPORT]],0,1,"Waiting for recross")
		self.transitional_trigger2 = AbstractTrigger("transitional trigger to long.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],25,1,"Waiting for recross")
		self.buyreversalTrigger = Purchase_trigger([[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],LOW,self.risk,"long reversal",timer,repeat,LONG,self.ppro_out)
		

		self.transitional_trigger.add_next_trigger(self.transitional_trigger2)
		self.transitional_trigger2.add_next_trigger(self.buyreversalTrigger)

		self.add_initial_triggers(self.transitional_trigger)


	def on_redeploying(self):

		""" whicheer gets used gets re-deploy """

		if self.buyTrigger.get_trigger_state()==False and not self.buyTrigger.pre_deploying_check():
			self.buyTrigger.total_reset()


		if self.buyreversalTrigger.get_trigger_state()==False: ### if its rip sell used 

			if not self.buyreversalTrigger.pre_deploying_check():  ## if it's a not successful run. 
				self.transitional_trigger.total_reset()
				self.transitional_trigger2.total_reset()
				self.buyreversalTrigger.total_reset()
			else:
				if not self.buyTrigger.pre_deploying_check():
					self.buyTrigger.total_reset()
				else:
					self.buyTrigger.deactivate()  #it's a successful run. deactive the other one. 



class Bearish(EntryStrategy):
	def __init__(self,timer,repeat,symbol,tradingplan):

		super().__init__("Entry :Bearish",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		#buyTrigger = Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",timer,repeat,LONG,self.ppro_out)

		self.sellTrigger = Purchase_trigger([[SYMBOL_DATA,BID,"<",SYMBOL_DATA,SUPPORT]],RESISTENCE,self.risk,"break down",timer,repeat,SHORT,self.ppro_out)
		self.add_initial_triggers(self.sellTrigger)


		self.transitional_trigger = AbstractTrigger("transitional trigger to short.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,RESISTENCE]],0,1,"Waiting for recross")
		self.transitional_trigger2 = AbstractTrigger("transitional trigger to short.",[[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,RESISTENCE]],25,1,"Waiting for recross")
		self.sellreversalTrigger = Purchase_trigger([[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,RESISTENCE]],HIGH,self.risk,"short reversal",timer,repeat,SHORT,self.ppro_out)

		self.transitional_trigger.add_next_trigger(self.transitional_trigger2)
		self.transitional_trigger2.add_next_trigger(self.sellreversalTrigger)


		self.add_initial_triggers(self.transitional_trigger)

	def on_redeploying(self):

		""" whicheer gets used gets re-deploy """

		if self.sellTrigger.get_trigger_state()==False and not self.sellTrigger.pre_deploying_check():
			self.sellTrigger.total_reset()


		if self.sellreversalTrigger.get_trigger_state()==False: ### if its rip sell used 

			if not self.sellreversalTrigger.pre_deploying_check():  ## if it's a not successful run. 
				self.transitional_trigger.total_reset()
				self.transitional_trigger2.total_reset()
				self.sellreversalTrigger.total_reset()
			else:
				if not self.sellTrigger.pre_deploying_check():
					self.sellTrigger.total_reset()
				else:
					self.sellTrigger.deactivate()  #it's a successful run. deactive the other one. 





class Ripsell(EntryStrategy):
	def __init__(self,timer,repeat,symbol,tradingplan):

		super().__init__("Entry :Ripsell",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out

		#self,description,trigger_timer:int,trigger_limit
		self.transitional_trigger = AbstractTrigger("transitional trigger to short.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,RESISTENCE]],0,1,"Waiting for recross")
		self.transitional_trigger2 = AbstractTrigger("transitional trigger to short.",[[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,RESISTENCE]],25,1,"Waiting for recross")
		self.sellreversalTrigger = Purchase_trigger([[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,RESISTENCE]],HIGH,self.risk,"short reversal",30,repeat,SHORT,self.ppro_out)

		self.transitional_trigger.add_next_trigger(self.transitional_trigger2)
		self.transitional_trigger2.add_next_trigger(self.sellreversalTrigger)

		self.add_initial_triggers(self.transitional_trigger)

	def on_redeploying(self):

		""" if the current price did not stay above the break price. reset the second half triggers. """
		if not self.sellreversalTrigger.pre_deploying_check():
			self.transitional_trigger.total_reset()
			self.transitional_trigger2.total_reset()
			self.sellreversalTrigger.total_reset()


class Dipbuy(EntryStrategy):
	def __init__(self,timer,repeat,symbol,tradingplan):

		super().__init__("Entry :DipBuy",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out

		self.transitional_trigger = AbstractTrigger("transitional trigger to long.",[[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,SUPPORT]],0,1,"Waiting for recross ")
		self.transitional_trigger2 = AbstractTrigger("transitional trigger to long.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],25,1,"Waiting for recross ")
		self.buyreversalTrigger = Purchase_trigger([[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],LOW,self.risk,"long reversal",timer,repeat,LONG,self.ppro_out)
		

		self.transitional_trigger.add_next_trigger(self.transitional_trigger2)
		self.transitional_trigger2.add_next_trigger(self.buyreversalTrigger)

		self.add_initial_triggers(self.transitional_trigger)

	def on_redeploying(self):

		""" if the current price did not stay above the break price. reset the second half triggers. """
		if not self.buyreversalTrigger.pre_deploying_check():
			self.transitional_trigger.total_reset()
			self.transitional_trigger2.total_reset()
			self.buyreversalTrigger.total_reset()


class Fadeany(EntryStrategy):
	def __init__(self,timer,repeat,symbol,tradingplan):

		super().__init__("Entry :Fadeany",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out

		self.transitional_trigger_buy = AbstractTrigger("transitional trigger to long.",[[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,SUPPORT]],0,1,"Waiting for recross ")
		self.transitional_trigger_buy_2 = AbstractTrigger("transitional trigger to long.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],25,1,"Waiting for recross ")
		self.buyreversalTrigger = Purchase_trigger([[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],LOW,self.risk,"long reversal",timer,repeat,LONG,self.ppro_out)
		
		self.transitional_trigger_buy.add_next_trigger(self.transitional_trigger_buy_2)
		self.transitional_trigger_buy_2.add_next_trigger(self.buyreversalTrigger)
		self.add_initial_triggers(self.transitional_trigger_buy)



		self.transitional_trigger_sell = AbstractTrigger("transitional trigger to short.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,RESISTENCE]],0,1,"Waiting for recross")
		self.transitional_trigger_sell_2 = AbstractTrigger("transitional trigger to short.",[[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,RESISTENCE]],25,1,"Waiting for recross")
		self.sellreversalTrigger = Purchase_trigger([[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,RESISTENCE]],HIGH,self.risk,"short reversal",timer,repeat,SHORT,self.ppro_out)
		
		self.transitional_trigger_sell.add_next_trigger(self.transitional_trigger_sell_2)
		self.transitional_trigger_sell_2.add_next_trigger(self.sellreversalTrigger)
		self.add_initial_triggers(self.transitional_trigger_sell)


	def on_redeploying(self):

		""" whicheer gets used gets re-deploy """
		if  self.buyreversalTrigger.get_trigger_state()==False and not self.buyreversalTrigger.pre_deploying_check():
			self.transitional_trigger_buy.total_reset()
			self.transitional_trigger_buy_2.total_reset()
			self.buyreversalTrigger.total_reset()

		if  self.sellreversalTrigger.get_trigger_state()==False and not self.sellreversalTrigger.pre_deploying_check():
			self.transitional_trigger_sell.total_reset()
			self.transitional_trigger_sell_2.total_reset()
			self.buyreversalTrigger.total_reset()






""" MANAGEMENT PLAN"""

class ManagementStrategy(Strategy):

	def __init__(self,name,symbol:Symbol,tradingplan):
		super().__init__(name,symbol,tradingplan)
		
	""" for management plan only """
	def on_loading_up(self):
		pass

	""" for management plan only """
	def on_start(self):
		self.manaTrigger.total_reset()
		self.tradingplan.current_price_level = 1
		self.set_mind("")


	""" for management plan only """
	def on_deploying(self):
		self.current_triggers = set()
		for i in self.initial_triggers:
			self.current_triggers.add(i)

class ThreePriceTargets(ManagementStrategy):

	def __init__(self,symbol,tradingplan):

		super().__init__("Management: Three pxt targets",symbol,tradingplan)

		self.manaTrigger = Three_price_trigger("manage",self.ppro_out)

		self.add_initial_triggers(self.manaTrigger)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		###upon activating, reset all parameters. 

	def on_loading_up(self): #call this whenever the break at price changes. 

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

			log_print(self.symbol_name,"Management price target adjusted:",self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])
		else:
			self.tradingplan.tkvars[AUTOMANAGE].set(False)


		#log_print(self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])
	def on_start(self):
		self.manaTrigger.total_reset()
		self.tradingplan.current_price_level = 1
		self.set_mind("")

class OneToTWORiskReward(ManagementStrategy):

	def __init__(self,symbol,tradingplan):

		super().__init__("Management: 1-to-2 risk-reward ",symbol,tradingplan)

		self.manaTrigger = TwoToOneTrigger("manage",self.ppro_out)

		self.add_initial_triggers(self.manaTrigger)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		###upon activating, reset all parameters. 

	def on_loading_up(self): #call this whenever the break at price changes. 

		price = self.tradingplan.data[AVERAGE_PRICE]
		stop = self.tradingplan.data[STOP_LEVEL]

		gap = abs(price-stop)
		coefficient = 1
		good = False

		if self.tradingplan.data[POSITION]==LONG:

			#log_print(self.data_list[id_],type(ohv),ohs,type(price))
	
			#self.tradingplan[id_][0] = price
			self.tradingplan.data[PXT1] = round(price+gap,2)
			self.tradingplan.data[PXT2] = round(price+gap*2,2) #round(self.tradingplan.data[PXT1]+0.02,2) 
			self.tradingplan.data[PXT3] = round(price+gap*3,2) #round(self.tradingplan.data[PXT2]+0.02,2) #

		elif self.tradingplan.data[POSITION]==SHORT:

	
			#self.price_levels[id_][0] = price
			self.tradingplan.data[PXT1] = round(price-gap,2)
			self.tradingplan.data[PXT2] = round(price-gap*2,2) #round(self.tradingplan.data[PXT1]-0.02,2)  #
			self.tradingplan.data[PXT3] = round(price-gap*3,2) #round(self.tradingplan.data[PXT2]-0.02,2) #

			
		#set the price levels. 
		#log_print(id_,"updating price levels.",price,self.price_levels[id_][1],self.price_levels[id_][2],self.price_levels[id_][3])
	
		self.tradingplan.tkvars[AUTOMANAGE].set(True)
		self.tradingplan.tkvars[PXT1].set(self.tradingplan.data[PXT1])
		self.tradingplan.tkvars[PXT2].set(self.tradingplan.data[PXT2])
		self.tradingplan.tkvars[PXT3].set(self.tradingplan.data[PXT3])

		log_print(self.symbol_name,"Management price target adjusted:",self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])



		#log_print(self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])


class AncartMethod(ManagementStrategy):


	def __init__(self,symbol,tradingplan):

		super().__init__("Management: ANCART METHODOLOGY",symbol,tradingplan)

		self.manaTrigger = ANCART_trigger("ANCART method manage",self.ppro_out)

		self.add_initial_triggers(self.manaTrigger)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		###upon activating, reset all parameters. 

		### CALCULATE THE STOP HERE.? NO .

	def on_loading_up(self): #call this whenever the break at price changes. 

		price = self.tradingplan.data[AVERAGE_PRICE]
		coefficient = 1
		good = False

		if self.tradingplan.data[POSITION]==LONG:

			#self.tradingplan[id_][0] = price
			self.tradingplan.data[PXT1] = round(self.tradingplan.data[AVERAGE_PRICE] +self.tradingplan.data[RISK_PER_SHARE],2)
			self.tradingplan.data[PXT2] = round(self.tradingplan.data[AVERAGE_PRICE] +self.tradingplan.data[RISK_PER_SHARE]*2,2)
			self.tradingplan.data[PXT3] = round(self.tradingplan.data[AVERAGE_PRICE] +self.tradingplan.data[RISK_PER_SHARE]*3,2)

		elif self.tradingplan.data[POSITION]==SHORT:

			#self.price_levels[id_][0] = price
			self.tradingplan.data[PXT1] = round(self.tradingplan.data[AVERAGE_PRICE] -self.tradingplan.data[RISK_PER_SHARE],2)
			self.tradingplan.data[PXT2] = round(self.tradingplan.data[AVERAGE_PRICE] -self.tradingplan.data[RISK_PER_SHARE]*2,2)
			self.tradingplan.data[PXT3] = round(self.tradingplan.data[AVERAGE_PRICE] -self.tradingplan.data[RISK_PER_SHARE]*3,2)
			
		#set the price levels. 
		#log_print(id_,"updating price levels.",price,self.price_levels[id_][1],self.price_levels[id_][2],self.price_levels[id_][3])
		
		self.tradingplan.tkvars[AUTOMANAGE].set(True)
		self.tradingplan.tkvars[PXT1].set(self.tradingplan.data[PXT1])
		self.tradingplan.tkvars[PXT2].set(self.tradingplan.data[PXT2])
		self.tradingplan.tkvars[PXT3].set(self.tradingplan.data[PXT3])

		
		log_print(self.symbol_name,"Management price target adjusted:",self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])


		#log_print(self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])

	def on_deploying(self):

		super().on_deploying()

		try:
			self.tradingplan.data[TARGET_SHARE] = int(self.tradingplan.tkvars[INPUT_TARGET_SHARE].get())
			self.tradingplan.data[RISK_PER_SHARE] = float(self.tradingplan.tkvars[RISK_PER_SHARE].get())
			self.tradingplan.data[ESTRISK] = round(self.tradingplan.data[TARGET_SHARE]*self.tradingplan.data[RISK_PER_SHARE],2)
		except:
			print("ANCART RISK INITIALIZATION ERROR, WRONG INPUT.")
			self.tradingplan.tkvars[AUTOMANAGE].set(False)

		#self.tradingplan.data[ANCART_OVERRIDE] = True
		self.tradingplan.adjusting_risk()
		self.tradingplan.update_displays()
		self.tradingplan.tklabels[RISK_RATIO].grid()
		self.tradingplan.tklabels['SzIn'].grid()


class SmartTrail(ManagementStrategy):

	def __init__(self,symbol,tradingplan):

		super().__init__("Management: Smart Trail",symbol,tradingplan)

		#####
		self.current_high = 0
		self.current_low = 0
		self.distance = 0

		self.manaTrigger = SmartTrailing_trigger("SmartTrail Trigger",self)

		self.add_initial_triggers(self.manaTrigger)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		###upon activating, reset all parameters. 

	def update(self):

		super().update()

		if self.tradingplan.current_price_level == 3 and self.distance!=0:

			#print("I AM HERE!")

			change = False
			### update STOP level ###

			if self.tradingplan.data[POSITION]==LONG:

				new_stop = round(self.symbol.get_bid() - self.distance,2)
				if new_stop > self.tradingplan.data[STOP_LEVEL]:
					self.tradingplan.data[STOP_LEVEL]=new_stop
					self.tradingplan.tkvars[STOP_LEVEL].set(new_stop)
					change = True

			elif self.tradingplan.data[POSITION]==SHORT:

				new_stop = round(self.symbol.get_ask() + self.distance,2)
				if new_stop < self.tradingplan.data[STOP_LEVEL]:
					self.tradingplan.data[STOP_LEVEL]=new_stop
					self.tradingplan.tkvars[STOP_LEVEL].set(new_stop)
					change = True

			### calculate new lock-in profit ###
			if change:
				lock_in = round(abs(self.tradingplan.data[STOP_LEVEL] -self.tradingplan.data[AVERAGE_PRICE])*self.tradingplan.data[CURRENT_SHARE],2)
				self.tradingplan.adjusting_risk()
				self.set_mind("$ lock-in: "+str(lock_in),GREEN)

	def on_loading_up(self): #call this whenever the break at price changes. 

		price = self.tradingplan.data[AVERAGE_PRICE]
		coefficient = 1
		good = False

		if self.tradingplan.data[POSITION]==LONG:
			ohv = self.symbol.data[OHAVG]
			ohs =  self.symbol.data[OHSTD]
			#log_print(self.data_list[id_],type(ohv),ohs,type(price))
			if ohv!=0:
				#self.tradingplan[id_][0] = price
				self.tradingplan.data[PXT1] = round(price+ohv*0.15*coefficient,2)
				self.tradingplan.data[PXT2] = round(price+ohv*0.4*coefficient,2) #round(self.tradingplan.data[PXT1]+0.02,2) 
				self.tradingplan.data[PXT3] = round(price+ohv*10*coefficient,2) #round(self.tradingplan.data[PXT2]+0.02,2) #
				good = True
		elif self.tradingplan.data[POSITION]==SHORT:
			olv = self.symbol.data[OLAVG]
			ols = self.symbol.data[OLSTD]
			if olv!=0:
				#self.price_levels[id_][0] = price
				self.tradingplan.data[PXT1] = round(price-olv*0.15*coefficient,2)
				self.tradingplan.data[PXT2] = round(price-olv*0.4*coefficient,2) #round(self.tradingplan.data[PXT1]-0.02,2)  #
				self.tradingplan.data[PXT3] = round(price-olv*10*coefficient,2) #round(self.tradingplan.data[PXT2]-0.02,2) #
				good = True
				
		#set the price levels. 
		#log_print(id_,"updating price levels.",price,self.price_levels[id_][1],self.price_levels[id_][2],self.price_levels[id_][3])
		if good:
			self.tradingplan.tkvars[AUTOMANAGE].set(True)
			self.tradingplan.tkvars[PXT1].set(self.tradingplan.data[PXT1])
			self.tradingplan.tkvars[PXT2].set(self.tradingplan.data[PXT2])
			self.tradingplan.tkvars[PXT3].set(self.tradingplan.data[PXT3])

			log_print(self.symbol_name,"Smart trailing price target adjusted:",self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])
		else:
			self.tradingplan.tkvars[AUTOMANAGE].set(False)

		#log_print(self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])

# clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)

# log_print(clsmembers)

# for i in clsmembers:
# 	log_print(i)