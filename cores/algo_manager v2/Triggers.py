from constant import *

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
	def __init__(self,subject1,type_,subject2,trigger_timer:int,description,trigger_limit=1):

		#self.symbol = symbol
		#bigger, or less than. 
		self.symbol = None
		self.d = None
		self.description = description

		
		self.s1 = subject1
		self.s2 = subject2#self.symbol.data[subject2]
		self.type = type_
		#stay above this time. 
		self.trigger_timer = trigger_timer

		self.triggered = False
		self.trigger_time = 0
		self.trigger_duration = 0

		self.trigger_count = 0
		self.trigger_limit = trigger_limit

		self.next_triggers = set()

	def set_symbol(self,symbol):
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

	def get_next_triggers(self):
		return self.next_triggers

	def check(self,symbol=None):
		if self.symbol==None:
			if symbol!=None:
				self.symbol = symbol
				self.d = symbol.get_data()

		#if it is above the price, update the time. put into is trigger 
		#print("Checking:",self.d[self.s1],self.d[self.s2])
		if self.symbol!=None:

			if self.type ==">":
				if self.d[self.s1]>=self.d[self.s2]: # I will need to find out how to form composite number.
					return self.update_trigger_duration()
				else:
					self.reset()

			elif self.type =="<":

				if self.d[self.s1]<=self.d[self.s2]:
					return self.update_trigger_duration()
				else:
					self.reset()

		return False

	def update_trigger_duration(self):

		if self.triggered == False: #first time trigger

			self.triggered = True
			self.trigger_time = self.symbol.get_time() 
			self.trigger_duration = 0

		else: #second tie trigger. update trigger duation
			self.trigger_duration = self.symbol.get_time() - self.trigger_time

		return self.is_trigger()

	def is_trigger(self):
		
		#print("Trigger:","cur time:",self.symbol.get_time(), "duration:", self.trigger_duration, "timer:",self.trigger_timer,"already occurance:",self.trigger_count,"total repeat time:",self.trigger_limit)
		if self.trigger_duration >= self.trigger_timer:

			###EVENT HAPPENS HERE.####
			self.trigger_event()
			self.trigger_count+=1
			if self.trigger_count == self.trigger_limit:
				#print("??")
				return True
			else:
				self.reset()	
		else:
			return False 

	def trigger_event(self):  #OVERRIDE
		try:
			print("Trigger:",self.description,"on", self.symbol.get_name(),"at time", self.symbol.get_time())
		except:
			print("Trigger:",self.description)
		### REPLACE the current trategy with current states. (when repeate is met.)


	def print(self):
		print("Trigger",self.description)

	def reset(self):
		self.triggered = False
		self.trigger_time = 0
		self.trigger_duration = 0

#self,subject1,type_,subject2,trigger_timer:int,description,trigger_limit=1
class SingleEntry(Trigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,subject1,type_,subject2,timer:int,description,pos):
		super().__init__(subject1,type_,subject2,timer,description)

		self.pos = pos

	#add the actual stuff here.
	def trigger_event(self):

		
		#PPRO RELATED EVENT.
		# if self.pos=="Long":
		# 	print("LONG")
		# elif self.pos =="Short":
		# 	print("SHORT")

		try:
			print("Trigger: SingleEntry PPRO EVENT: ",self.pos,"at",self.symbol.get_time())
		except:
			print("Trigger: SingleEntry PPRO EVENT: ",self.pos)

		super().trigger_event()

# s = SingleEntry(ASK,">",PREMARKETHIGH,0,"BUY BREAK UP")
# s.trigger_event()