from constant import *
from Symbol import *
from Triggers import *
import sys, inspect
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

class Strategy: #ABSTRACT CLASS. the beginning of a sequence, containing one or more triggers.

	def __init__(self,name):

		self.strategy_name = name
		self.current_triggers = set()
		self.symbol=None
		self.tradingplan =None
		self.timer = 0
		self.all_triggers = []

	def get_name(self):
		return self.strategy_name

	def add_initial_triggers(self,trigger):
		self.current_triggers.add(trigger)

		self.all_triggers.append(trigger)


		#change all the timers 
	def modify_all_timers(self):

		pass

	def set_symbol(self,symbol:Symbol,tradingplan):
		self.symbol=symbol
		self.tradingplan = tradingplan
		self.strategy_name = self.symbol.get_name()+" "+self.strategy_name

	def update(self):
		if self.current_triggers!= None:
			for i in self.current_triggers:
				if self.symbol!=None:
					check = False
					if i.check(self.symbol):
						#print("?opo")
						#print(i.description)
						check = True
					#print(check)
					if check:
						break
			if check:
				self.current_triggers = i.get_next_triggers() #replace the triggers. 
				if len(self.current_triggers)==0: #if there is no trigger, call the finish even.t
					self.on_finish()

		else:
			print("Strategy: nothing to trigger.")

	def on_finish(self):
		print(self.strategy_name+" completed")
		self.tradingplan.on_finish(self)	


class BreakUp(Strategy): #the parameters contains? dk. yet .  #Can make single entry, or multiple entry. 
	def __init__(self,timer=0,repeat=False):
		super().__init__("Break up")
		#subject1,type_,subject2,trigger_timer,description,trigger_limit=1
		buyTrigger = SingleEntry(ASK,">",PREMARKETHIGH,timer,"BUY BREAK UP","Long")
		self.add_initial_triggers(buyTrigger)

class BreakDown(Strategy): #the parameters contains? dk. yet .
	def __init__(self,timer=0,repeat=False):
		super().__init__("Break down")

		shortTrigger = SingleEntry(BID,"<",PREMARKETLOW,timer,"SHORT BREAK DOWN","Short")
		self.add_initial_triggers(shortTrigger)


class BreakAny(Strategy):
	def __init__(self,timer=0,repeat=False):
		super().__init__("Break Any")
		
		#subject1,type_,subject2,trigger_timer,description,trigger_limit=1
		buyTrigger = SingleEntry(ASK,">",PREMARKETHIGH,timer,"BUY BREAK UP","Long")
		self.add_initial_triggers(buyTrigger)

		shortTrigger = SingleEntry(BID,"<",PREMARKETLOW,timer,"SHORT BREAK DOWN","Short")
		self.add_initial_triggers(shortTrigger)



# clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)

# print(clsmembers)

# for i in clsmembers:
# 	print(i)