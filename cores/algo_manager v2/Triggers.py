from constant import *

class AbstractTrigger:

	"""
	All trigger class basically have functons of.

	1. check_conditions.
	2. Triggers events.
	3. Set next triggers
	4. Return next triggers. 

	"""
	def __init__(self,description,trigger_timer:int,trigger_limit=1):

		#self.symbol = symbol
		#bigger, or less than. 
		self.symbol = None
		self.symbol_name = None
		self.symbol_data = None
		self.description = description

		#How long it need sto trigger it.
		self.trigger_timer = trigger_timer

		self.triggered = False
		self.trigger_time = 0
		self.trigger_duration = 0

		#How many times it can be triggered. 
		self.trigger_count = 0
		self.trigger_limit = trigger_limit

		self.conditions = []

		self.next_triggers = set()


	def add_conditions(subject1,d_type1,subject2,d_type2,type_):
		self.conditions.append([subject1,d_type1,subject2,d_type2,type_])

	def decode_conditions(self,i):

		#print(i)
		#['symbol_data', 'ask', '>', 'symbol_data', 'phigh']
		s1 =i[0]
		t1= i[1]

		type_ = i[2]


		s2= i[3]
		t2= i[4]
		

		s1_=None
		s2_=None

		if s1 == SYMBOL_DATA:
			s1_ = self.symbol_data
		elif s1 == TP_DATA:
			s1_ = self.tp_data
		else:
			print("Trigger decoding error on ",s1,self.description)

		if s2 == SYMBOL_DATA:
			s2_ = self.symbol_data
		elif s2 == TP_DATA:
			s2_ = self.tp_data
		else:
			print("Trigger decoding error on ",s2,self.description)

		return s1_,s2_,t1,t2,type_

	def check_conditions(self):
		
		eval = True
		"""
		1. Check if all conditions are met.
		2. If so, take note of time. If time trigger is 0, immediatly trigger event. 
		3. If time trigger is above 0. Check if it is already triggered. 
		"""

		if 1:
			for i in self.conditions:
				s1,s2,t1,t2,type_= self.decode_conditions(i)

				if type_ ==">":
					if not s1[t1] >= s2[t2]:
						eval = False	
				elif type_ =="<":
					if not s1[t1] <= s2[t2]:
						eval = False

			if eval ==True:

				if self.trigger_timer == 0:
					return self.is_trigger()

				else:
					if not self.triggered:
						self.triggered = True
						self.trigger_time = self.symbol.get_time() 
						self.trigger_duration = 0

					else:
						self.trigger_duration = self.symbol.get_time() - self.trigger_time
						if self.trigger_duration >= self.self.trigger_timer:
							return self.is_trigger()
		# except Exception as e:
		# 	print("Trigger error on ",self.description,e)

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

		self.trigger_event()
		self.trigger_count+=1
		if self.trigger_count == self.trigger_limit:
			return True
		else:
			return False 	

	def trigger_event(self):  #OVERRIDEn n 

		try:
			print("Trigger:",self.description,"on", self.symbol.get_name(),"at time", self.symbol.get_time())
		except:
			print("Trigger:",self.description)
		### REPLACE the current trategy with current states. (when repeate is met.)


	def set_symbol(self,symbol,tradingplan,ppro_out):
		self.symbol = symbol
		self.symbol_name = symbol.get_name()
		self.symbol_data = self.symbol.get_data()
		self.ppro_out = ppro_out

		self.tradingplan = tradingplan 
		self.tp_data = self.tradingplan.get_data()

	def add_next_trigger(self,next_trigger):
		self.next_triggers.add(next_trigger)

	def get_next_triggers(self):
		return self.next_triggers

	def print(self):
		print("Trigger",self.description)

	def reset(self):
		self.triggered = False
		self.trigger_time = 0
		self.trigger_duration = 0


#self,subject1,type_,subject2,trigger_timer:int,description,trigger_limit=1

class Purchase_trigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out):
		super().__init__(description,trigger_timer,trigger_limit)

		self.pos = pos
		self.stop = stop
		self.ppro_out =ppro_out
		self.risk = risk 
		self.conditions = conditions 

		checker = False
		for i in conditions:
			if len(i)!=5:
				checker = True
				break

		if checker:
			print("Trigger problem on purchase_trigger,conditions:",conditions)
	#add the actual stuff here.
	def trigger_event(self):

		share = self.shares_calculator()

		if self.pos == LONG:

			#set pos to long ,and stop to a value.

			self.tradingplan.data[POSITION]=LONG
			self.tradingplan.tkvars[POSITION].set(LONG)

			self.tradingplan.data[STOP_LEVEL]=self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.symbol_data[self.stop])

			self.ppro_out.send(["Buy",self.symbol_name,share,self.description])
			print("Trigger: SingleEntry PPRO EVENT: ",self.pos,"at",self.symbol.get_time())
		elif self.pos ==SHORT:

			self.tradingplan.data[POSITION]=SHORT
			self.tradingplan.tkvars[POSITION].set(SHORT)

			self.tradingplan.data[STOP_LEVEL]=self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.symbol_data[self.stop])

			self.ppro_out.send(["Sell",self.symbol_name,share,self.description])
		else:
			print("unidentified side. ")

		self.tradingplan.update_displays()

	def shares_calculator(self):


		if self.pos ==LONG:
			risk_per_share =  abs(self.symbol_data[self.stop]-self.symbol_data[ASK])
		else:
			risk_per_share =  abs(self.symbol_data[self.stop]-self.symbol_data[BID])

		shares = int(self.risk//risk_per_share)

		self.tradingplan.data[TARGET_SHARE]=shares

		return shares



# s = SingleEntry(ASK,">",PREMARKETHIGH,0,"BUY BREAK UP")
# s.trigger_event()