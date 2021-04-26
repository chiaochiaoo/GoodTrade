from Symbol import *
from Tradingplan import *



class Trigger:

	#This is a generic trigger class.
	#differen type of specicial trigger all inheirit the property of a trigger.
	#Trigger solely operates on the data from symbol.
	#needs:
	#1. symbol's data
	#2. who to compare with who
	#3. type
	#5. Actions.
	#4. next trigger / trigger layer
	#trigger don't know who it serves until it's activated. 
	def __init__(self,subject1,type_,subject2,timer:int,description,trigger_limit=1):

		#self.symbol = symbol
		#bigger, or less than. 
		self.symbol = None
		self.d = None
		self.description = description

		
		self.s1 = subject1
		self.s2 = subject2#self.symbol.data[subject2]
		self.type = type_
		#stay above this time. 
		self.trigger_timer = timer

		self.triggered = False
		self.trigger_time = 0
		self.trigger_duration = 0

		self.trigger_count = 0
		self.trigger_limit = trigger_limit

		self.next_triggers = set()

	def set_symbol(self,symbol:Symbol):
		self.symbol = symbol
		self.d = self.symbol.get_data()
		if self.error_checking(subject1,type_,subject2,timer):
			print("Trigger creation error on ",subject1,type_,subject2)

	def error_checking(self,subject1,type_,subject2,timer):

		checker = True

		data = self.symbol.get_data()
		if subject1 not in data or subject2 not in data:
			checker = False
		if type_!=">" or type_!="<":
			checker = False
		if timer<0:
			checker = False

		return checker

	def add_next_trigger(self,next_trigger):
		self.next_triggers.add(next_trigger)

	def check(self,symbol=None):
		if self.symbol==None:
			if symbol!=None:
				self.symbol = symbol
				self.d = symbol.get_data()

		#if it is above the price, update the time. put into is trigger 
		#print("Trigger:",self.d[self.subject1],self.d[self.subject2])
		#print("Checking:",self.d[self.s1],self.d[self.s2])
		if self.symbol!=None:

			if self.type ==">":
				if self.d[self.s1]>=self.d[self.s2]: # I will need to find out how to form composite number.
					return self.check_trigger()
				else:
					self.reset()

			elif self.type =="<":

				if self.d[self.s1]<=self.d[self.s2]:
					self.check_trigger()
				else:
					self.reset()

		return False

	def check_trigger(self):

		if self.triggered == False: #first time trigger

			self.triggered = True
			self.trigger_time = self.symbol.get_time() 
		
		else: #second tie trigger. update trigger duation
			self.trigger_duration = self.symbol.get_time() - self.trigger_time

		#print(self.trigger_duration)
		#check the trigger thingy. 
		return self.is_trigger()

	def is_trigger(self):
		
		if self.triggered==True and self.trigger_duration >= self.trigger_timer:
			print("Trigger:",self.description,"on", self.symbol.get_name(),"at time", self.symbol.get_time())
			self.trigger_count+=1
			if self.trigger_count == self.trigger_limit:
				print("Trigger",self.description,"Finished,","next:",self.next_triggers)
				return True
			else:
				self.reset()	
		else:
			return False 

	def trigger_event(self):  #once it's fired, it is gone.
		print("Trigger:",self.description,"on", self.symbol.get_name(),"at time", self.symbol.get_time())

		self.trigger_count+=1

		if self.trigger_count == self.trigger_limit:
			self.final_event()
		else:
			self.reset()	
		### REPLACE the current trategy with current states. (when repeate is met.)


	def print(self):
		print("Trigger",self.description)

	def reset(self):
		self.triggered = False
		self.trigger_time = 0
		self.trigger_duration = 0

class SingleEntry(Trigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,subject1,type_,subject2,timer:int,description,next_trigger=None):
		super().__init__(subject1,type_,subject2,timer,description,next_trigger)

	#add the actual stuff here.
	def trigger_event(self):

		super().trigger_event()
		#PPRO RELATED EVENT.
		print("PPRO EVENT:",self.symbol.get_time())


# USE LESS. 
#two things. 1. I need it be able to have multiple initial triggers. 2. Mark begin. 3. Mark finished.
#OR - I have the plan for multiple Trigger Sequence? That's...hmm... dumb. 
class TriggerSequence:

	def __init__(Self,name):
		self.name = name
		self.main = None
		self.last = None

	def add_trigger(self,trigger:Trigger):

		#the very first one.
		if self.main ==None and self.last ==None:
			self.main = Trigger

		#the second one.
		if self.main!=None and self.last==None:
			self.last = Trigger
			self.main.set_next_trigger(self.last)

		elif self.main!=None and self.last!=None:
			self.last.set_next_trigger(Trigger)
			self.last = Trigger
		else:
			print("Tactic Sequence add trigger errors.")

	def add_constant_trigger(self,trigger:Trigger):

		if self.constant!=None:
			print("Already exist a constant")
		else:
			self.constant = trigger 



class Strategy: #ABSTRACT CLASS. the beginning of a sequence, containing one or more triggers.

	def __init__(self):

		self.activated = False
		self.current_triggers = set()
		self.symbol=None

	def add_initial_triggers(self,trigger):
		self.current_triggers.add(trigger)

	def set_symbol(self,symbol:Symbol):
		self.symbol=symbol

	def update(self):
		if self.current_triggers!= None:
			for i in self.current_triggers:
				if self.symbol!=None:
					if i.check(self.symbol):
						print(i.description)
					
					#replace the triggers. 
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

class BreakUp(Strategy): #the parameters contains? dk. yet .
	def __init__(self):
		super().__init__()

		buyTrigger = SingleEntry(ASK,">",HIGH,0,"BUY BREAK OUT")
		self.add_initial_triggers(buyTrigger)

class AnyLevel(Strategy):
	def __init__(self):
		super().__init__()


#### Trading plan is where all the triggers, conditions are.###
#### Orders on a symbol create a basic trading plan. and modifying it chainging the plan.


if __name__ == '__main__':

	#TEST CASES for trigger.
	
	aapl = Symbol("aapl")
	TP = TradingPlan(aapl)
	aapl.set_tradingplan(TP)
	aapl.set_high(12)
	aapl.set_low(10)


	b = BreakUp()
	TP.set_EntryStrategy(b)
	TP.start_EntryStrategy()

	#TP.add_trigger(buyTrigger)
	
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
# class Trade:
# 	def __init__(self,symbol,position,shares,price=None,rationale=None):

# 		self.matured = False
# 		self.activation = False
# 		self.symbol = symbol
# 		self.position = position
# 		self.shares = shares
# 		self.price = None

# 		self.stop_order = False
# 		self.stop_order_id = None

# 	def place_trade(self): #ask ppro to place orders.
# 		pas

