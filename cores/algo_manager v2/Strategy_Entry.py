from constant import *
from Symbol import *
from Triggers import *
from Util_functions import *

#from Strategy_Management import *
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


"""ENTRY PLAN"""
class BreakUp(EntryStrategy): #the parameters contains? dk. yet .  #Can make single entry, or multiple entry.
	def __init__(self,timer,repeat,symbol,tradingplan):
		super().__init__("Entry : Break up",symbol,tradingplan)

		self.timer = timer
		self.repeat = repeat
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		self.buyTrigger = EDGX_break_Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",timer,repeat,LONG,self.ppro_out)

		self.add_initial_triggers(self.buyTrigger)

	def on_redeploying(self):

		if not self.buyTrigger.pre_deploying_check():
			self.buyTrigger.total_reset()
			self.restart()
		else:

			self.tradingplan.mark_algo_status(DONE)
			# self.transitional_trigger = AbstractTrigger("transition to below pH.",[[SYMBOL_DATA,BID,"<",SYMBOL_DATA,RESISTENCE]],0,1,"REACTIVATE")
			# self.buyTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",self.timer,self.repeat,LONG,self.ppro_out)
			# self.transitional_trigger.add_next_trigger(self.buyTrigger)

			# ###Where continuation trigger goes.#####
			# self.symbol.data[EXIT] = self.tradingplan.data[FIBLEVEL2]
			# self.symbol.data[ENTRY] = self.symbol.data[HIGH]

			# self.cont_buyTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,ENTRY]],EXIT,self.risk,"Break Up contituation",0,1,LONG,self.ppro_out)
			# log_print(self.symbol_name,"setting contituation on ",round(self.symbol.data[ENTRY],2),"stop:",round(self.symbol.data[EXIT],2),0,1)

			# self.set_initial_trigger(self.transitional_trigger)
			# self.add_initial_triggers(self.cont_buyTrigger)
			# self.restart()



class BreakDown(EntryStrategy): #the parameters contains? dk. yet .  #Can make single entry, or multiple entry.
	def __init__(self,timer,repeat,symbol,tradingplan):
		super().__init__("Entry : Break up",symbol,tradingplan)
		self.timer = timer
		self.repeat = repeat
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		self.sellTrigger = EDGX_break_Purchase_trigger([[SYMBOL_DATA,BID,"<",SYMBOL_DATA,SUPPORT]],RESISTENCE,self.risk,"break down",timer,repeat,SHORT,self.ppro_out)

		self.add_initial_triggers(self.sellTrigger)


	def on_redeploying(self):

		if not self.sellTrigger.pre_deploying_check():
			self.sellTrigger.total_reset()
			self.restart()
		else:

			self.tradingplan.mark_algo_status(DONE)

			# self.transitional_trigger = AbstractTrigger("transition to below pH.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],0,1,"REACTIVATE")
			# self.sellTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,SUPPORT]],RESISTENCE,self.risk,"break down",self.timer,self.repeat,SHORT,self.ppro_out)
			# self.transitional_trigger.add_next_trigger(self.sellTrigger)


			# self.symbol.data[EXIT] = self.tradingplan.data[FIBLEVEL2]
			# self.symbol.data[ENTRY] = self.symbol.data[LOW]

			# self.cont_sellTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,BID,"<",SYMBOL_DATA,ENTRY]],EXIT,self.risk,"break down contituation",0,1,SHORT,self.ppro_out)
			# log_print(self.symbol_name,"setting contituation on ",round(self.symbol.data[ENTRY],2),"stop:",round(self.symbol.data[EXIT],2),0,1)

			# self.set_initial_trigger(self.transitional_trigger)
			# self.add_initial_triggers(self.cont_sellTrigger)
			
#class BreakUpEDGX(EntryStrategy): #the parameters contains? dk. yet .  #Can make single entry, or multiple entry.
	def __init__(self,timer,repeat,symbol,tradingplan):
		super().__init__("Entry : Break up",symbol,tradingplan)

		self.timer = timer
		self.repeat = repeat
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		self.buyTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",timer,repeat,LONG,self.ppro_out)

		self.add_initial_triggers(self.buyTrigger)

	def on_redeploying(self):

		if not self.buyTrigger.pre_deploying_check():
			self.buyTrigger.total_reset()
			self.restart()
		else:

			self.tradingplan.mark_algo_status(DONE)
			# self.transitional_trigger = AbstractTrigger("transition to below pH.",[[SYMBOL_DATA,BID,"<",SYMBOL_DATA,RESISTENCE]],0,1,"REACTIVATE")
			# self.buyTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",self.timer,self.repeat,LONG,self.ppro_out)
			# self.transitional_trigger.add_next_trigger(self.buyTrigger)

			# ###Where continuation trigger goes.#####
			# self.symbol.data[EXIT] = self.tradingplan.data[FIBLEVEL2]
			# self.symbol.data[ENTRY] = self.symbol.data[HIGH]

			# self.cont_buyTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,ENTRY]],EXIT,self.risk,"Break Up contituation",0,1,LONG,self.ppro_out)
			# log_print(self.symbol_name,"setting contituation on ",round(self.symbol.data[ENTRY],2),"stop:",round(self.symbol.data[EXIT],2),0,1)

			# self.set_initial_trigger(self.transitional_trigger)
			# self.add_initial_triggers(self.cont_buyTrigger)
			# self.restart()



#Continuation trigger relies on FIBLEVEl. 
class BreakAny(EntryStrategy):
	def __init__(self,timer,repeat,symbol,tradingplan):

		super().__init__("Entry : Break Any",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		self.buyTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",timer,repeat,LONG,self.ppro_out)
		self.sellTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,BID,"<",SYMBOL_DATA,SUPPORT]],RESISTENCE,self.risk,"break down",timer,repeat,SHORT,self.ppro_out)

		self.timer = timer
		self.repeat = repeat

		self.add_initial_triggers(self.buyTrigger)
		self.add_initial_triggers(self.sellTrigger)


	"""ignore what was there. generic re-set. facing all senarios."""
	def on_redeploying(self):

		self.clear_initial_triggers()

		if self.buyTrigger.get_trigger_state()==False and not self.buyTrigger.pre_deploying_check(): #below the premarket high.

			self.add_initial_triggers(self.buyTrigger)
			self.add_initial_triggers(self.sellTrigger)
				#print(1)
			# else:    #above the premarket high.
			# 	self.transitional_trigger = AbstractTrigger("transition trigger to below Res.",[[SYMBOL_DATA,BID,"<",SYMBOL_DATA,RESISTENCE]],0,1,"REACTIVATE")
			# 	self.transitional_trigger.add_next_trigger(self.buyTrigger)
			# 	self.transitional_trigger.add_next_trigger(self.sellTrigger)
			# 	self.set_initial_trigger(self.transitional_trigger)
			# 	#print(2)
			self.buyTrigger.total_reset()
			self.restart()
		elif self.sellTrigger.get_trigger_state()==False and not self.sellTrigger.pre_deploying_check():

			self.add_initial_triggers(self.buyTrigger)
			self.add_initial_triggers(self.sellTrigger)
				#print(3)
			# else:	#below the premarket low.
			# 	self.transitional_trigger = AbstractTrigger("transitional trigger to above Sus.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],0,1,"REACTIVATE")
			# 	self.transitional_trigger.add_next_trigger(self.buyTrigger)
			# 	self.transitional_trigger.add_next_trigger(self.sellTrigger)
			# 	self.set_initial_trigger(self.transitional_trigger)
			# 	#print(4)
			self.sellTrigger.total_reset()

			self.restart()
		else:
			self.tradingplan.mark_algo_status(DONE)


		# if not self.sellTrigger.pre_deploying_check() and not self.buyTrigger.pre_deploying_check(): #fit in both conditions.

		# elif self.sellTrigger.pre_deploying_check() and not self.buyTrigger.pre_deploying_check(): #below premarket low.

		# 	self.transitional_trigger = AbstractTrigger("transitional trigger to above pL.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],0,1,"REACTIVATE")
		# 	self.transitional_trigger.add_next_trigger(self.buyTrigger)
		# 	self.transitional_trigger.add_next_trigger(self.sellTrigger)

		# 	self.set_initial_trigger(self.transitional_trigger)

		# elif not self.sellTrigger.pre_deploying_check() and self.buyTrigger.pre_deploying_check(): #above premarket high.

		# 	self.transitional_trigger = AbstractTrigger("transition trigger to below pH.",[[SYMBOL_DATA,BID,"<",SYMBOL_DATA,RESISTENCE]],0,1,"REACTIVATE")
		# 	self.transitional_trigger.add_next_trigger(self.buyTrigger)
		# 	self.transitional_trigger.add_next_trigger(self.sellTrigger)

		# 	self.set_initial_trigger(self.transitional_trigger)

		# else:
		# 	print("BREAK ANY Trigger: unidentified redeploying conditions.")

	# def on_redeploying(self):

	# 	""" if one is used and does not vilate the entry condition (failed trade) reset it."""

	# 	self.clear_initial_triggers()

	# 	if not self.sellTrigger.pre_deploying_check():
	# 		self.sellTrigger.total_reset()
	# 		self.add_initial_triggers(self.sellTrigger)

	# 	else:
	# 		self.transitional_trigger = AbstractTrigger("transition to below pH.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],0,1,"REACTIVATE")
	# 		self.transitional_trigger.add_next_trigger(self.sellTrigger)

	# 		self.add_initial_triggers(self.transitional_trigger)
	# 		#self.sellTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,SUPPORT]],RESISTENCE,self.risk,"break down",self.timer,self.repeat,SHORT,self.ppro_out)

	# 	if not self.buyTrigger.pre_deploying_check():
	# 		self.buyTrigger.total_reset()
	# 		self.add_initial_triggers(self.buyTrigger)
	# 	else:

	# 		self.transitional_trigger = AbstractTrigger("transition to below pH.",[[SYMBOL_DATA,BID,"<",SYMBOL_DATA,RESISTENCE]],0,1,"REACTIVATE")
	# 		self.transitional_trigger.add_next_trigger(self.buyTrigger)

	# 		self.add_initial_triggers(self.transitional_trigger)
	# 		#self.buyTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",self.timer,self.repeat,LONG,self.ppro_out)
	# 	self.restart()


class BreakFirst(EntryStrategy):
	def __init__(self,timer,repeat,symbol,tradingplan):

		super().__init__("Entry : BreakFirst",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		self.timer = timer
		self.repeat = repeat
		self.buyTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",timer,repeat,LONG,self.ppro_out)
		self.sellTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,BID,"<",SYMBOL_DATA,SUPPORT]],RESISTENCE,self.risk,"break down",timer,repeat,SHORT,self.ppro_out)

		self.add_initial_triggers(self.buyTrigger)
		self.add_initial_triggers(self.sellTrigger)

	def on_redeploying(self):


		if self.buyTrigger.get_trigger_state()==False:
			self.sellTrigger.deactivate()

			if not self.buyTrigger.pre_deploying_check():
				self.buyTrigger.total_reset()
			# else:

			# 	self.transitional_trigger = AbstractTrigger("transition to below pH.",[[SYMBOL_DATA,BID,"<",SYMBOL_DATA,RESISTENCE]],0,1,"REACTIVATE")
			# 	self.buyTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",self.timer,self.repeat,LONG,self.ppro_out)
			# 	self.transitional_trigger.add_next_trigger(self.buyTrigger)

			# 	###Where continuation trigger goes.#####
			# 	# self.symbol.data[EXIT] = self.tradingplan.data[FIBLEVEL2]
			# 	# self.symbol.data[ENTRY] = self.symbol.data[HIGH]

			# 	# self.cont_buyTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,ENTRY]],EXIT,self.risk/2,"Break Up contituation",0,1,LONG,self.ppro_out)
			# 	# log_print(self.symbol_name,"setting contituation on ",round(self.symbol.data[ENTRY],2),"stop:",round(self.symbol.data[EXIT],2),0,1)

			# 	self.add_initial_triggers(self.transitional_trigger)
			# 	#self.add_initial_triggers(self.cont_buyTrigger)
				self.restart()
			else:
				self.tradingplan.mark_algo_status(DONE)

		elif self.sellTrigger.get_trigger_state()==False:
			self.buyTrigger.deactivate()

			if not self.sellTrigger.pre_deploying_check():
				self.sellTrigger.total_reset()
			# else:
			# 	self.transitional_trigger = AbstractTrigger("transition to below pH.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],0,1,"REACTIVATE")
			# 	self.sellTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,SUPPORT]],RESISTENCE,self.risk,"break down",self.timer,self.repeat,SHORT,self.ppro_out)
			# 	self.transitional_trigger.add_next_trigger(self.sellTrigger)

			# 	# self.symbol.data[EXIT] = self.tradingplan.data[FIBLEVEL2]
			# 	# self.symbol.data[ENTRY] = self.symbol.data[LOW]

			# 	# self.cont_sellTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,BID,"<",SYMBOL_DATA,ENTRY]],EXIT,self.risk/2,"break down contituation",0,1,SHORT,self.ppro_out)
			# 	# log_print(self.symbol_name,"setting contituation on ",round(self.symbol.data[ENTRY],2),"stop:",round(self.symbol.data[EXIT],2),0,1)

			# 	self.add_initial_triggers(self.transitional_trigger)
			# 	#self.add_initial_triggers(self.cont_sellTrigger)
				self.restart()
			else:
				self.tradingplan.mark_algo_status(DONE)


class Bullish(EntryStrategy):
	def __init__(self,timer,repeat,symbol,tradingplan):

		super().__init__("Entry :Bullish",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		self.buyTrigger = Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",timer,repeat,LONG,self.ppro_out)
		self.add_initial_triggers(self.buyTrigger)

		self.transitional_trigger = AbstractTrigger("transitional trigger to long.",[[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,SUPPORT]],0,1,"Waiting for recross")
		self.transitional_trigger2 = AbstractTrigger("transitional trigger to long.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],45,1,"Waiting for recross")
		self.buyreversalTrigger = WideStop_trigger([[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],LOW,self.risk,"long reversal",timer,repeat,LONG,self.ppro_out)
		

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
		self.transitional_trigger2 = AbstractTrigger("transitional trigger to short.",[[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,RESISTENCE]],45,1,"Waiting for recross")
		self.sellreversalTrigger = WideStop_trigger([[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,RESISTENCE]],HIGH,self.risk,"short reversal",timer,repeat,SHORT,self.ppro_out)

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
		self.transitional_trigger2 = AbstractTrigger("transitional trigger to short.",[[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,RESISTENCE]],45,1,"Waiting for recross")
		self.sellreversalTrigger = WideStop_trigger([[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,RESISTENCE]],HIGH,self.risk,"short reversal",30,repeat,SHORT,self.ppro_out)

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
		self.transitional_trigger2 = AbstractTrigger("transitional trigger to long.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],45,1,"Waiting for recross ")
		self.buyreversalTrigger = WideStop_trigger([[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],LOW,self.risk,"long reversal",timer,repeat,LONG,self.ppro_out)
		

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
		self.timer = timer
		self.repeat = repeat

		super().__init__("Entry :Fadeany",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out

		self.transitional_trigger_buy = AbstractTrigger("transitional trigger to long.",[[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,SUPPORT]],0,1,"Waiting for recross ")
		self.transitional_trigger_buy_2 = AbstractTrigger("transitional trigger to long.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],45,1,"Waiting for recross ")
		self.buyreversalTrigger = WideStop_trigger([[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],LOW,self.risk,"long reversal",timer,repeat,LONG,self.ppro_out)

		self.transitional_trigger_buy.add_next_trigger(self.transitional_trigger_buy_2)
		self.transitional_trigger_buy_2.add_next_trigger(self.buyreversalTrigger)
		self.add_initial_triggers(self.transitional_trigger_buy)



		self.transitional_trigger_sell = AbstractTrigger("transitional trigger to short.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,RESISTENCE]],0,1,"Waiting for recross")
		self.transitional_trigger_sell_2 = AbstractTrigger("transitional trigger to short.",[[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,RESISTENCE]],45,1,"Waiting for recross")
		self.sellreversalTrigger = WideStop_trigger([[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,RESISTENCE]],HIGH,self.risk,"short reversal",timer,repeat,SHORT,self.ppro_out)

		self.transitional_trigger_sell.add_next_trigger(self.transitional_trigger_sell_2)
		self.transitional_trigger_sell_2.add_next_trigger(self.sellreversalTrigger)
		self.add_initial_triggers(self.transitional_trigger_sell)


	def on_redeploying(self):

		""" whicheer gets used gets re-deploy """
		if  self.buyreversalTrigger.get_trigger_state()==False:
			if not self.buyreversalTrigger.pre_deploying_check():
				self.buyreversalTrigger = WideStop_trigger([[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],LOW,self.risk,"long reversal",self.timer,self.repeat,LONG,self.ppro_out)
				self.set_initial_trigger(self.buyreversalTrigger)

			else:
				self.transitional_trigger_buy.total_reset()
				self.transitional_trigger_buy_2.total_reset()
				self.buyreversalTrigger.total_reset()

				self.symbol.data[EXIT] = self.tradingplan.data[FIBLEVEL2]
				self.symbol.data[ENTRY] = self.symbol.data[HIGH]

				self.cont_buyTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,ENTRY]],EXIT,self.risk,"fade Up contituation",0,1,LONG,self.ppro_out)
				log_print(self.symbol_name,"setting contituation on ",round(self.symbol.data[ENTRY],2),"stop:",round(self.symbol.data[EXIT],2),self.timer,self.repeat)

				self.set_initial_trigger(self.transitional_trigger_buy)
				self.add_initial_triggers(self.cont_buyTrigger)

				#just cross the resistence. short.

		if  self.sellreversalTrigger.get_trigger_state()==False:
			if not self.sellreversalTrigger.pre_deploying_check():
				 #just cross the support.  long
				self.sellreversalTrigger = WideStop_trigger([[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,RESISTENCE]],HIGH,self.risk,"short reversal",self.timer,self.repeat,SHORT,self.ppro_out)
				self.set_initial_trigger(self.sellreversalTrigger)
			else:
				self.transitional_trigger_sell.total_reset()
				self.transitional_trigger_sell_2.total_reset()
				self.sellreversalTrigger.total_reset()

				self.symbol.data[EXIT] = self.tradingplan.data[FIBLEVEL2]
				self.symbol.data[ENTRY] = self.symbol.data[LOW]

				self.cont_sellTrigger = Break_any_Purchase_trigger([[SYMBOL_DATA,BID,"<",SYMBOL_DATA,ENTRY]],EXIT,self.risk,"fade down contituation",0,1,SHORT,self.ppro_out)
				log_print(self.symbol_name,"setting contituation on ",round(self.symbol.data[ENTRY],2),"stop:",round(self.symbol.data[EXIT],2),self.timer,self.repeat)

				self.set_initial_trigger(self.transitional_trigger_sell)
				self.add_initial_triggers(self.cont_sellTrigger)
				
		self.restart()
class Fadeany_cont(EntryStrategy):
	def __init__(self,timer,repeat,symbol,tradingplan):

		super().__init__("Entry :Fadeany",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out

		self.transitional_trigger_buy = AbstractTrigger("transitional trigger to long.",[[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,SUPPORT]],0,1,"Waiting for recross ")
		self.transitional_trigger_buy_2 = AbstractTrigger("transitional trigger to long.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],45,1,"Waiting for recross ")
		self.buyreversalTrigger = WideStop_trigger([[SYMBOL_DATA,BID,">",SYMBOL_DATA,SUPPORT]],LOW,self.risk,"long reversal",timer,repeat,LONG,self.ppro_out)

		self.transitional_trigger_buy.add_next_trigger(self.transitional_trigger_buy_2)
		self.transitional_trigger_buy_2.add_next_trigger(self.buyreversalTrigger)
		self.add_initial_triggers(self.transitional_trigger_buy)



		self.transitional_trigger_sell = AbstractTrigger("transitional trigger to short.",[[SYMBOL_DATA,BID,">",SYMBOL_DATA,RESISTENCE]],0,1,"Waiting for recross")
		self.transitional_trigger_sell_2 = AbstractTrigger("transitional trigger to short.",[[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,RESISTENCE]],45,1,"Waiting for recross")
		self.sellreversalTrigger = WideStop_trigger([[SYMBOL_DATA,ASK,"<",SYMBOL_DATA,RESISTENCE]],HIGH,self.risk,"short reversal",timer,repeat,SHORT,self.ppro_out)

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

class FreeControl(EntryStrategy):

	def __init__(self,timer,repeat,symbol,tradingplan):

		super().__init__("empty",symbol,tradingplan)
		super().on_finish()


	def update(self):
		super().on_finish()
		