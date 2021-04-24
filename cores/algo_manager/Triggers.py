from Symbol import *




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
	def __init__(self,symbol:Symbol,subject1,type_,subject2,timer:int,description,next_trigger=None):

		self.symbol = symbol
		if self.error_checking(subject1,type_,subject2,timer):
			print("Trigger creation error on ",subject1,type_,subject2)

		#bigger, or less than. 

		self.description = description

		self.d = self.symbol.get_data()
		self.s1 = subject1
		self.s2 = subject2#self.symbol.data[subject2]
		self.type = type_
		#stay above this time. 
		self.trigger_timer = timer

		self.triggered = False
		self.trigger_time = 0
		self.trigger_duration = 0

		self.next_trigger = next_trigger

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


	def set_next_trigger(self,next_trigger):
		self.next_trigger=next_trigger

	def check(self):

		#if it is above the price, update the time. put into is trigger 
		#print("Trigger:",self.d[self.subject1],self.d[self.subject2])
		#print("Checking:",self.d[self.s1],self.d[self.s2])
		if self.type ==">":

			if self.d[self.s1]>=self.d[self.s2]:
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
			return True
		else:
			return False 

	def trigger_event(self):  #once it's fired, it is gone.
		print("Trigger:",self.description,"on", self.symbol.get_name(),"at time", self.symbol.get_time())

	def reset(self):
		self.triggered = False
		self.trigger_time = 0
		self.trigger_duration = 0

class SingleEntry(Trigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,symbol:Symbol,subject1,type_,subject2,timer:int,description,next_trigger=None):
		super().__init__(symbol,subject1,type_,subject2,timer,description,next_trigger)

	#add the actual stuff here.
	def trigger_event(self):

		super().trigger_event()
		#PPRO RELATED EVENT.
		print("PPRO EVENT:",self.symbol.get_time())


class TriggerSequence:

	def __init__(Self,name):
		self.name = name
		self.main = None
		self.last = None

		#normally use for stops.
		self.constant = None

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



#### Trading plan is where all the triggers, conditions are.###
#### Orders on a symbol create a basic trading plan. and modifying it chainging the plan.
class TradingPlan:

	def __init__(self,symbol:Symbol,risk=None):

		self.symbol = symbol

		self.risk = risk
		self.current_share = 0
		self.target_share = 0

		#using the parameters from the tradingplan, create the associated triggers, and trigger sequence. 
		self.current_triggers=[]

	def update(self):
		remove = []
		for i in self.current_triggers:
			if i.check():
				#print(1)
				remove.append(i)
		#execute the actions on remove.
		#remove it from triggers.
		for i in remove:
			i.trigger_event()
			self.current_triggers.remove(i)

	def add_trigger(self,t:Trigger):
		self.current_triggers.append(t)

if __name__ == '__main__':

	#TEST CASES for trigger.
	aapl = Symbol("aapl")

	TP = TradingPlan(aapl)
	aapl.set_tradingplan(TP)
	aapl.set_high(15)
	buyTrigger = SingleEntry(aapl,ASK,">",HIGH,0,"BUY HIGH")

	TP.add_trigger(buyTrigger)
	
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