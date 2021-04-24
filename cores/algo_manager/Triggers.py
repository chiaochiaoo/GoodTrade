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
	def __init__(self,symbol:Symbol,subject1,type_,subject2,timer:int,description,next_trigger:None):

		self.symbol = symbol
		if self.error_checking(subject1,type_,subject2,timer):
			print("Trigger creation error on ",subject1,type_,subject2)

		#bigger, or less than. 

		self.description = description

		self.data = self.symbol.get_data()
		self.subject1 = self.data[subject1]
		self.subject2 = self.data[subject2]
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
		if self.type ==">":

			if self.symbol.get_bid()>=self.trigger_price:
				return self.check_trigger()
			else:
				self.reset()

		elif self.type =="<":

			if self.symbol.get_bid()<=self.trigger_price:
				self.check_trigger()
			else:
				return self.reset()

		return False
	def check_trigger(self):

		if self.triggered == False: #first time trigger

			self.triggered = True
			self.trigger_time = self.symbol.get_time() 
		
		else: #second tie trigger. update trigger duation
			self.trigger_duration = self.symbol.get_time() - self.trigger_time

		#check the trigger thingy. 
		return self.is_trigger()

	def is_trigger(self):
		
		if self.triggered==True and self.trigger_duration >= self.trigger_timer:
			return True
		else:
			return False 


	def trigger_event(self):  #once it's fired, it is gone.
		print(self.description,"at time happened")

	def reset(self):
		self.triggered = False
		self.trigger_time = 0
		self.trigger_duration = 0


class SingleEntry(Trigger):

	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self):

		super.init()

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

	def __init__(self,symbol:Symbol,tradingplan):

		self.symbol = symbol

		self.risk = tradingplan["risk"]
		self.current_share = 0
		self.target_share = 0

		#using the parameters from the tradingplan, create the associated triggers, and trigger sequence. 



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