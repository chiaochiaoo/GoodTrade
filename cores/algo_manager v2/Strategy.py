from constant import *
from Symbol import *
from Triggers import *
from Util_functions import *
from Strategy_Entry import *
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


	def clear_initial_triggers(self):
		self.initial_triggers = set()

	def set_initial_trigger(self,trigger):
		self.initial_triggers = set()
		self.initial_triggers.add(trigger)
		trigger.set_symbol(self.symbol, self.tradingplan, self.ppro_out)

	def add_initial_triggers(self,trigger):
		self.initial_triggers.add(trigger)
		trigger.set_symbol(self.symbol, self.tradingplan, self.ppro_out)

	def update(self):

		if len(self.current_triggers)>0:
			check = False
			triggered = None
			for i in self.current_triggers:
				if self.symbol!=None:
					check = False
					if i.check_conditions():
						check = True
					if check:
						break
			if check:
				self.current_triggers = i.get_next_triggers() #replace the triggers.  CHANGE: ADD THE TRIGGERS INSTEAD OF REPLACE.
				# for j in i.get_next_triggers():
				# 	self.current_triggers.add(j)
				#self.current_triggers.remove(i)
				#self.print_current_triggers()
				#log_print(self.current_triggers)
				for i in self.current_triggers:
					i.set_symbol(self.symbol,self.tradingplan,self.ppro_out)

				if len(self.current_triggers)==0: #if there is no trigger, call the finish even.t
					self.on_finish()

		else:
			log_print(self.strategy_name,": nothing to trigger.")

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
