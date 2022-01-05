from constant import *
from Util_functions import *

class AbstractTrigger:

	"""
	All trigger class basically have functons of.

	1. check_conditions.
	2. Triggers events.
	3. Set next triggers
	4. Return next triggers. 

	"""
	def __init__(self,description,conditions,trigger_timer:int,trigger_limit,mind_string=None):

		#self.symbol = symbol
		#bigger, or less than. 
		self.symbol = None
		self.symbol_name = None
		self.symbol_data = None
		self.description = description

		self.mind = None
		self.mind_label = None
		#How long it need sto trigger it.
		self.trigger_timer = trigger_timer

		self.activation = True
		self.triggered = False
		self.trigger_time = 0
		self.trigger_duration = 0

		#How many times it can be triggered. 
		self.trigger_count = 0
		self.trigger_limit = trigger_limit


		self.mind_string = mind_string

		if conditions!=None:
			self.conditions = conditions 
		else:
			self.conditions = []

		self.next_triggers = set()

	def add_conditions(subject1,d_type1,subject2,d_type2,type_):
		self.conditions.append([subject1,d_type1,subject2,d_type2,type_])

	def decode_conditions(self,i):

		#log_print(i)
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
			log_print("Trigger decoding error on ",s1,self.description)

		if s2 == SYMBOL_DATA:
			s2_ = self.symbol_data
		elif s2 == TP_DATA:
			s2_ = self.tp_data
		else:
			log_print("Trigger decoding error on ",s2,self.description)

		#log_print(s1_,s2_,t1,t2,type_)
		return s1_,s2_,t1,t2,type_

	""" return True if a trade is succesful.(in the entry range). else False"""
	def pre_deploying_check(self):

		eval = True

		for i in self.conditions:
			s1,s2,t1,t2,type_= self.decode_conditions(i)

			if type_ ==">":
				if not s1[t1] > s2[t2]:
					eval = False	
			elif type_ =="<":
				if not s1[t1] < s2[t2]:
					eval = False
			#print(s1[t1],type_,s2[t2],eval)
		return eval

	def deactivate(self):
		self.activation = False

	def check_conditions(self):
		
		eval = True
		"""
		1. Check if all conditions are met.
		2. If so, take note of time. If time trigger is 0, immediatly trigger event. 
		3. If time trigger is above 0. Check if it is already triggered. 
		"""
		if self.activation:
			#print(self.conditions)
			for i in self.conditions:
				s1,s2,t1,t2,type_= self.decode_conditions(i)

				try:
					if type_ ==">":
						if not s1[t1] > s2[t2]:
							eval = False	
					elif type_ =="<":
						if not s1[t1] < s2[t2]:
							eval = False
				except Exception as e:
					log_print("Error",self.symbol_name,e,self.description)

			if eval ==True:

				if self.trigger_timer == 0:
					return self.is_trigger()
				###add a special case for the new incremental.###				
				elif self.trigger_count == 0 and self.trigger_limit == 5:
					return self.is_trigger()
				else:
					if not self.triggered:
						self.triggered = True
						self.trigger_time = self.symbol.get_time() 
						self.trigger_duration = 0
						self.set_mind(str(int(self.trigger_timer)) +" s to trigger")
					else:
						self.trigger_duration = self.symbol.get_time() - self.trigger_time
						self.set_mind(str(int(self.trigger_timer - self.trigger_duration)) +" s to trigger")
						if self.trigger_duration >= self.trigger_timer:
							return self.is_trigger()

			else:
				if self.triggered:
					self.set_mind("Trigger breaks. reset.")
				self.reset()
		# except Exception as e:
		# 	log_print("Trigger error on ",self.description,e)

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

		self.trigger_count+=1
		self.trigger_event()
		if self.trigger_count == self.trigger_limit:
			self.trigger_count = 0
			self.activation = False
			return True
		else:
			self.reset()
			return False 	

	def trigger_event(self):  #OVERRIDEn n 

		if self.mind_string!=None:
			self.set_mind(self.mind_string) 
		try:
			log_print("Trigger:",self.description,"on", self.symbol.get_name(),"at time", self.symbol.get_time())
		except:
			log_print("Trigger:",self.description)
		### REPLACE the current trategy with current states. (when repeate is met.)

	def set_symbol(self,symbol,tradingplan,ppro_out):
		self.symbol = symbol
		self.symbol_name = symbol.get_name()
		self.symbol_data = self.symbol.get_data()
		self.ppro_out = ppro_out

		self.tradingplan = tradingplan 
		self.tp_data = self.tradingplan.get_data()

		#log_print(self.symbol_name,self.description,self.trigger_timer,self.trigger_limit)

		self.set_mind_object()

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

	def add_next_trigger(self,next_trigger):
		self.next_triggers.add(next_trigger)

	def get_next_triggers(self):
		return self.next_triggers

	def get_trigger_state(self):
		""" if true: still useful 
		    if false: already used """
		return self.activation

	def log_print(self):
		log_print("Trigger",self.description)

	def reactivate(self):
		self.activation = True
		self.trigger_count = 0

	def reset(self):
		self.triggered = False
		self.trigger_time = 0
		self.trigger_duration = 0
		
		#self.clear_mind()
	def total_reset(self):
		self.reactivate()
		self.reset()

#self,subject1,type_,subject2,trigger_timer:int,description,trigger_limit=1

class Purchase_trigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out):
		super().__init__(description,conditions,trigger_timer,trigger_limit)

		#log_print("purchase_trigger,",self.trigger_timer,self.trigger_limit)
		self.pos = pos

		self.entry = conditions[0][4]

		self.stop = stop
		self.ppro_out =ppro_out
		self.risk = risk 
		#self.conditions = conditions 

		self.entry_text =""
		self.trigger_text = ""

		self.entry_price = 0
		self.stop_price = 0

		checker = False
		for i in conditions:
			if len(i)!=5:
				checker = True
				break

		if checker:
			log_print("Trigger problem on purchase_trigger,conditions:",conditions)
	#add the actual stuff here.


	def trigger_event(self):

		"""
		HERE I NEED TO SEPERATE BY CASES.
		IF IT IS OVERRIDDEN.
		THEN, 1. PUNCH IN DIRECTLY BY # AMOUNT OF SHARES
			  2. DON"T OVERRIDE STOP VALUE.(ANCARTMANAGE WILL DO IT)
		IF NOT, PROCEED AS USUAL. 
		"""

		share = self.shares_calculator()

		self.entry_price = self.symbol_data[self.entry]
		
		log_print(self.symbol_name,"Trigger: ",self.pos,share,"stop :",self.stop,self.symbol_data[self.stop],self.symbol.get_time())

		if self.pos!="":
			self.tradingplan.expect_orders = self.pos
			if self.trigger_count!= self.trigger_limit:
				self.set_mind("Entry: "+str(self.trigger_count)+"/"+str(self.trigger_limit),DEFAULT)
			else:
				self.set_mind("Entry: Complete",GREEN)

		if self.pos == LONG:

			self.tradingplan.data[STOP_LEVEL]=self.stop_price#self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.stop_price)

			self.tradingplan.data[BREAKPRICE]=self.entry_price#self.symbol_data[self.stop]
			#self.tradingplan.tkvars[BREAKPRICE].set(self.entry_price)
			#self.tradingplan.expect_orders = True
			#log_print("Trigger: Purchase: ",self.symbol_name,self.pos,share,"at",self.symbol.get_time())
		
			if share>0:
				self.ppro_out.send([IOCSELL,self.symbol_name,share,self.symbol_data[ASK]])
				
		elif self.pos ==SHORT:

			self.tradingplan.data[STOP_LEVEL]=self.stop_price#self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.stop_price)

			self.tradingplan.data[BREAKPRICE]=self.entry_price#self.symbol_data[self.stop]
			#self.tradingplan.tkvars[BREAKPRICE].set(self.entry_price)

			if share>0:
				self.ppro_out.send([IOCSELL,self.symbol_name,share,self.symbol_data[BID]])
		else:
			log_print("unidentified side. ")


		self.tradingplan.update_displays()

	def shares_calculator(self):

		if self.pos ==LONG:
			risk_per_share = abs(self.symbol_data[ASK]-self.symbol_data[self.stop])
			self.stop_price = self.symbol_data[self.stop]


			if risk_per_share < self.symbol_data[ASK]*0.0006:
				log_print(self.symbol_name,": stop too close:",round(risk_per_share,2)," adjusted to",str(round(self.symbol_data[ASK]*0.0006,2)))
				risk_per_share = self.symbol_data[ASK]*0.0006

				#overwrite the stop price here 
				self.stop_price = round(self.symbol_data[BID] - risk_per_share,2)

		elif self.pos ==SHORT:
			risk_per_share = abs(self.symbol_data[self.stop]-self.symbol_data[BID])
			self.stop_price = self.symbol_data[self.stop]

			if risk_per_share < self.symbol_data[ASK]*0.0006:
				log_print(self.symbol_name,": stop too close:",round(risk_per_share,2)," adjusted to",str(round(self.symbol_data[ASK]*0.0006,2)))
				risk_per_share = self.symbol_data[ASK]*0.0006
				self.stop_price = round(self.symbol_data[ASK] + risk_per_share,2)

		if self.symbol_data[ASK]>100 and risk_per_share <0.12:
			risk_per_share = 0.12

		if self.symbol_data[ASK]<100 and self.symbol_data[ASK]>5 and risk_per_share <0.1:
			risk_per_share = 0.1

		if self.symbol_data[ASK]<5 and risk_per_share <0.02:
			risk_per_share = 0.02

		shares = int((self.risk)/risk_per_share)

		if self.tradingplan.data[TARGET_SHARE]==0:
			self.tradingplan.data[TARGET_SHARE]=shares

		return int(shares/self.trigger_limit)


class NoStop_trigger(AbstractTrigger):

	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out):
		super().__init__(description,conditions,trigger_timer,trigger_limit)

		#log_print("purchase_trigger,",self.trigger_timer,self.trigger_limit)
		self.pos = pos

		self.entry = conditions[0][4]

		self.stop = stop
		self.ppro_out =ppro_out
		self.risk = risk 
		#self.conditions = conditions 

		self.entry_text =""
		self.trigger_text = ""

		self.entry_price = 0
		self.stop_price = 0

		checker = False
		for i in conditions:
			if len(i)!=5:
				checker = True
				break

		if checker:
			log_print("Trigger problem on purchase_trigger,conditions:",conditions)
	#add the actual stuff here.


	def trigger_event(self):

		"""
		HERE I NEED TO SEPERATE BY CASES.
		IF IT IS OVERRIDDEN.
		THEN, 1. PUNCH IN DIRECTLY BY # AMOUNT OF SHARES
			  2. DON"T OVERRIDE STOP VALUE.(ANCARTMANAGE WILL DO IT)
		IF NOT, PROCEED AS USUAL. 
		"""

		share = self.shares_calculator()

		self.entry_price = self.symbol_data[self.entry]
		
		log_print(self.symbol_name,"Trigger: ",self.pos,share,"stop :",self.stop,self.symbol_data[self.stop],self.symbol.get_time())

		if self.pos!="":
			self.tradingplan.expect_orders = self.pos
			if self.trigger_count!= self.trigger_limit:
				self.set_mind("Entry: "+str(self.trigger_count)+"/"+str(self.trigger_limit),DEFAULT)
			else:
				self.set_mind("STOP BYPASSING: ON")
				#self.set_mind("Entry: Complete",GREEN)

		if self.pos == LONG:

			self.tradingplan.data[STOP_LEVEL]=self.stop_price#self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.stop_price)

			self.tradingplan.data[BREAKPRICE]=self.entry_price#self.symbol_data[self.stop]
			#self.tradingplan.tkvars[BREAKPRICE].set(self.entry_price)
			#self.tradingplan.expect_orders = True
			#log_print("Trigger: Purchase: ",self.symbol_name,self.pos,share,"at",self.symbol.get_time())
			self.tradingplan.data[USING_STOP] = False
			self.set_mind("STOP BYPASSING: ON")
			
			if share>0:
				self.ppro_out.send(["Buy",self.symbol_name,share,self.description])
				
		elif self.pos ==SHORT:

			self.tradingplan.data[STOP_LEVEL]=self.stop_price#self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.stop_price)

			self.tradingplan.data[BREAKPRICE]=self.entry_price#self.symbol_data[self.stop]
			#self.tradingplan.tkvars[BREAKPRICE].set(self.entry_price)
			self.tradingplan.data[USING_STOP] = False
			self.set_mind("STOP BYPASSING: ON")
			#self.set_mind("STOP BYPASSING: ON")
			if share>0:
				self.ppro_out.send(["Sell",self.symbol_name,share,self.description])
		else:
			log_print("unidentified side. ")


		self.tradingplan.update_displays()

	def shares_calculator(self):

		if self.pos ==LONG:
			risk_per_share = abs(self.symbol_data[ASK]-self.symbol_data[self.stop])
			self.stop_price = self.symbol_data[self.stop]


			if risk_per_share < self.symbol_data[ASK]*0.0006:
				log_print(self.symbol_name,": stop too close:",round(risk_per_share,2)," adjusted to",str(round(self.symbol_data[ASK]*0.0006,2)))
				risk_per_share = self.symbol_data[ASK]*0.0006

				#overwrite the stop price here 
				self.stop_price = round(self.symbol_data[BID] - risk_per_share,2)

		elif self.pos ==SHORT:
			risk_per_share = abs(self.symbol_data[self.stop]-self.symbol_data[BID])
			self.stop_price = self.symbol_data[self.stop]

			if risk_per_share < self.symbol_data[ASK]*0.0006:
				log_print(self.symbol_name,": stop too close:",round(risk_per_share,2)," adjusted to",str(round(self.symbol_data[ASK]*0.0006,2)))
				risk_per_share = self.symbol_data[ASK]*0.0006
				self.stop_price = round(self.symbol_data[ASK] + risk_per_share,2)

		if self.symbol_data[ASK]>100 and risk_per_share <0.12:
			risk_per_share = 0.12

		if self.symbol_data[ASK]<100 and self.symbol_data[ASK]>5 and risk_per_share <0.1:
			risk_per_share = 0.1

		if self.symbol_data[ASK]<5 and risk_per_share <0.02:
			risk_per_share = 0.02

		shares = int((self.risk)/risk_per_share)

		if self.tradingplan.data[TARGET_SHARE]==0:
			self.tradingplan.data[TARGET_SHARE]=shares

		return int(shares/self.trigger_limit)

class WideStop_trigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out):
		super().__init__(description,conditions,trigger_timer,trigger_limit)

		#log_print("purchase_trigger,",self.trigger_timer,self.trigger_limit)
		self.pos = pos

		self.entry = conditions[0][4]

		self.stop = stop
		self.ppro_out =ppro_out
		self.risk = risk 
		#self.conditions = conditions 

		self.entry_text =""
		self.trigger_text = ""

		self.entry_price = 0
		self.stop_price = 0

		checker = False
		for i in conditions:
			if len(i)!=5:
				checker = True
				break

		if checker:
			log_print("Trigger problem on purchase_trigger,conditions:",conditions)
	#add the actual stuff here.


	def trigger_event(self):

		"""
		HERE I NEED TO SEPERATE BY CASES.
		IF IT IS OVERRIDDEN.
		THEN, 1. PUNCH IN DIRECTLY BY # AMOUNT OF SHARES
			  2. DON"T OVERRIDE STOP VALUE.(ANCARTMANAGE WILL DO IT)
		IF NOT, PROCEED AS USUAL. 
		"""

		share = self.shares_calculator()

		self.entry_price = self.symbol_data[self.entry]
		
		log_print(self.symbol_name,"Trigger: ",self.pos,share,"stop :",self.stop,self.symbol_data[self.stop],self.symbol.get_time())

		if self.pos!="":
			self.tradingplan.expect_orders = self.pos
			if self.trigger_count!= self.trigger_limit:
				self.set_mind("Entry: "+str(self.trigger_count)+"/"+str(self.trigger_limit),DEFAULT)
			else:
				self.set_mind("Entry: Complete",GREEN)

		if self.pos == LONG:

			self.tradingplan.data[STOP_LEVEL]=self.stop_price#self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.stop_price)

			self.tradingplan.data[BREAKPRICE]=self.entry_price#self.symbol_data[self.stop]
			#self.tradingplan.tkvars[BREAKPRICE].set(self.entry_price)
			#self.tradingplan.expect_orders = True
			#log_print("Trigger: Purchase: ",self.symbol_name,self.pos,share,"at",self.symbol.get_time())
		
			if share>0:
				self.ppro_out.send([IOCBUY,self.symbol_name,share,self.symbol_data[ASK]])
				
		elif self.pos ==SHORT:

			self.tradingplan.data[STOP_LEVEL]=self.stop_price#self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.stop_price)

			self.tradingplan.data[BREAKPRICE]=self.entry_price#self.symbol_data[self.stop]
			#self.tradingplan.tkvars[BREAKPRICE].set(self.entry_price)

			if share>0:
				self.ppro_out.send([IOCSELL,self.symbol_name,share,self.symbol_data[BID]])
		else:
			log_print("unidentified side. ")


		self.tradingplan.update_displays()

	def shares_calculator(self):

		if self.pos ==LONG:
			risk_per_share = abs(self.symbol_data[ASK]-self.symbol_data[self.stop])
			self.stop_price = self.symbol_data[self.stop]


			if risk_per_share < self.symbol_data[ASK]*0.0012:
				log_print(self.symbol_name,": stop too close:",round(risk_per_share,2)," adjusted to",str(round(self.symbol_data[ASK]*0.0012,2)))
				risk_per_share = self.symbol_data[ASK]*0.0012

				#overwrite the stop price here 
				self.stop_price = round(self.symbol_data[BID] - risk_per_share,2)

		elif self.pos ==SHORT:
			risk_per_share = abs(self.symbol_data[self.stop]-self.symbol_data[BID])
			self.stop_price = self.symbol_data[self.stop]

			if risk_per_share < self.symbol_data[ASK]*0.0012:
				log_print(self.symbol_name,": stop too close:",round(risk_per_share,2)," adjusted to",str(round(self.symbol_data[ASK]*0.0012,2)))
				risk_per_share = self.symbol_data[ASK]*0.0012
				self.stop_price = round(self.symbol_data[ASK] + risk_per_share,2)

		if self.symbol_data[ASK]>100 and risk_per_share <0.25:
			risk_per_share = 0.25

		if self.symbol_data[ASK]<100 and self.symbol_data[ASK]>5 and risk_per_share <0.15:
			risk_per_share = 0.15

		if self.symbol_data[ASK]<5 and risk_per_share <0.04:
			risk_per_share = 0.04

		shares = int((self.risk)/risk_per_share)

		if self.tradingplan.data[TARGET_SHARE]==0:
			self.tradingplan.data[TARGET_SHARE]=shares

		return int(shares/self.trigger_limit)


class Break_any_Purchase_trigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out):
		super().__init__(description,conditions,trigger_timer,trigger_limit)

		#log_print("purchase_trigger,",self.trigger_timer,self.trigger_limit)
		self.pos = pos

		self.entry = conditions[0][4]

		self.stop = stop
		self.ppro_out =ppro_out
		self.risk = risk 
		#self.conditions = conditions 

		self.entry_text =""
		self.trigger_text = ""

		self.entry_price = 0
		self.stop_price = 0

		checker = False
		for i in conditions:
			if len(i)!=5:
				checker = True
				break

		if checker:
			log_print("Trigger problem on purchase_trigger,conditions:",conditions)
	#add the actual stuff here.


	def trigger_event(self):

		"""
		HERE I NEED TO SEPERATE BY CASES.
		IF IT IS OVERRIDDEN.
		THEN, 1. PUNCH IN DIRECTLY BY # AMOUNT OF SHARES
			  2. DON"T OVERRIDE STOP VALUE.(ANCARTMANAGE WILL DO IT)
		IF NOT, PROCEED AS USUAL. 
		"""

		share = self.shares_calculator()

		self.entry_price = self.symbol_data[self.entry]
		
		log_print(self.symbol_name,"Trigger: ",self.pos,share,"stop :",self.stop_price)

		if self.pos!="":
			self.tradingplan.expect_orders = self.pos
			if self.trigger_count!= self.trigger_limit:
				self.set_mind("Entry: "+str(self.trigger_count)+"/"+str(self.trigger_limit),DEFAULT)
			else:
				self.set_mind("Entry: Complete",GREEN)

		#print()
		if self.pos == LONG:


			self.tradingplan.data[STOP_LEVEL]=self.stop_price#self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.stop_price)

			self.tradingplan.data[BREAKPRICE]=self.entry_price#self.symbol_data[self.stop]
			#self.tradingplan.tkvars[BREAKPRICE].set(self.entry_price)
			#self.tradingplan.expect_orders = True
			#log_print("Trigger: Purchase: ",self.symbol_name,self.pos,share,"at",self.symbol.get_time())
		
			if share>0:

				spread = self.symbol_data[ASK]-self.symbol_data[BID]

				spread_risk = spread*share/self.risk

				log_print(self.symbol_name,"Current spread:,",spread,"immediate risk loss%",spread_risk)


				self.ppro_out.send([IOCBUY,self.symbol_name,share,self.symbol_data[ASK]])
				# if spread_risk < 0.15:
				# 	log_print(self.symbol_name,"Current spread:,",spread,"immediate risk loss%",spread_risk)
				# 	self.ppro_out.send([IOCBUY,self.symbol_name,share,self.symbol_data[ASK]])
				# else:
				# 	log_print(self.symbol_name,"Current spread:,",spread,"immediate risk loss%",spread_risk,"CANCEL ENTRY")
				# 	self.set_mind("Spread TOO HIGH",GREEN)
		elif self.pos ==SHORT:

			self.tradingplan.data[STOP_LEVEL]=self.stop_price#self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.stop_price)

			self.tradingplan.data[BREAKPRICE]=self.entry_price#self.symbol_data[self.stop]
			#self.tradingplan.tkvars[BREAKPRICE].set(self.entry_price)

			if share>0:

				spread = self.symbol_data[ASK]-self.symbol_data[BID]
				spread_risk = spread*share/self.risk

				log_print(self.symbol_name,"Current spread:,",spread,"immediate risk loss%",spread_risk)


				self.ppro_out.send([IOCSELL,self.symbol_name,share,self.symbol_data[BID]])
				# if spread_risk < 0.15:

				# else:
				# 	log_print(self.symbol_name,"Current spread:,",spread,"immediate risk loss%",spread_risk,"CANCEL ENTRY")
				# 	self.set_mind("Spread TOO HIGH",GREEN)

				
		else:
			log_print("unidentified side. ")


		self.tradingplan.update_displays()

	def shares_calculator(self):

		if self.pos ==LONG:

			#if this is the last run, set it to day low. (if day low is greater than current stop and lower than ask.)

			#print(self.trigger_limit)

			risk_per_share = abs(self.symbol_data[ASK]-self.symbol_data[self.stop])
			self.stop_price = self.symbol_data[self.stop]


			if self.trigger_count==self.trigger_limit and self.trigger_limit>1 and self.symbol_data[LOW]>self.symbol_data[self.stop] and self.symbol_data[LOW]!=0:

				mid_ = round((self.symbol_data[LOW]+self.symbol_data[self.stop])/2,2)
				risk_per_share = round(abs(self.symbol_data[ASK]-mid_),2)

				log_print(self.symbol_name,"entry near completion, using day low as new stop,low:",self.symbol_data[LOW]," adjusted:",mid_," risk per share:",risk_per_share)
				#self.stop_price = self.symbol_data[LOW]

				if risk_per_share < self.symbol_data[ASK]*0.0012:
					log_print(self.symbol_name,": stop too close:",round(risk_per_share,2)," adjusted to",str(round(self.symbol_data[ASK]*0.0012,2)))
					risk_per_share = self.symbol_data[ASK]*0.0012

					#overwrite the stop price here
					self.stop_price = round(self.symbol_data[BID] - risk_per_share,2)

				else:
					self.stop_price = mid_

		elif self.pos ==SHORT:
			risk_per_share = abs(self.symbol_data[self.stop]-self.symbol_data[BID])
			self.stop_price = self.symbol_data[self.stop]

			if self.trigger_count==self.trigger_limit and self.trigger_limit>1 and self.symbol_data[HIGH]<self.symbol_data[self.stop] and self.symbol_data[HIGH]!=0:

				mid_ = round((self.symbol_data[HIGH]+self.symbol_data[self.stop])/2,2)
				risk_per_share = round(abs(mid_ -self.symbol_data[BID]),2)

				log_print(self.symbol_name,"entry near completion, using day high as new stop. high:",self.symbol_data[HIGH],"adjusted",mid_," risk per share:",risk_per_share)
				

				if risk_per_share < self.symbol_data[ASK]*0.0012:
					log_print(self.symbol_name,": stop too close:",round(risk_per_share,2)," adjusted to",str(round(self.symbol_data[ASK]*0.0012,2)))
					risk_per_share = self.symbol_data[ASK]*0.0012
					self.stop_price = round(self.symbol_data[ASK] + risk_per_share,2)
				else:
					self.stop_price = mid_

		if self.symbol_data[ASK]>100 and risk_per_share <0.2:
			risk_per_share = 0.2

		if self.symbol_data[ASK]<100 and self.symbol_data[ASK]>5 and risk_per_share <0.15:
			risk_per_share = 0.15

		if self.symbol_data[ASK]<5 and risk_per_share <0.04:
			risk_per_share = 0.04

		shares = int((self.risk)/risk_per_share)

		if self.tradingplan.data[TARGET_SHARE]==0:
			self.tradingplan.data[TARGET_SHARE]=shares

		return int(shares/self.trigger_limit)




class Break_any_Passive_trigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out):
		super().__init__(description,conditions,trigger_timer,trigger_limit)

		#log_print("purchase_trigger,",self.trigger_timer,self.trigger_limit)
		self.pos = pos

		self.entry = conditions[0][4]

		self.stop = stop
		self.ppro_out =ppro_out
		self.risk = risk 
		#self.conditions = conditions 

		self.entry_text =""
		self.trigger_text = ""

		self.entry_price = 0
		self.stop_price = 0

		checker = False
		for i in conditions:
			if len(i)!=5:
				checker = True
				break

		if checker:
			log_print("Trigger problem on purchase_trigger,conditions:",conditions)
	#add the actual stuff here.


	def trigger_event(self):

		"""
		HERE I NEED TO SEPERATE BY CASES.
		IF IT IS OVERRIDDEN.
		THEN, 1. PUNCH IN DIRECTLY BY # AMOUNT OF SHARES
			  2. DON"T OVERRIDE STOP VALUE.(ANCARTMANAGE WILL DO IT)
		IF NOT, PROCEED AS USUAL. 
		"""

		share = self.shares_calculator()

		self.entry_price = self.symbol_data[self.entry]
		
		log_print(self.symbol_name,"Trigger: ",self.pos,share,"stop :",self.stop_price)

		if self.pos!="":
			self.tradingplan.expect_orders = self.pos
			if self.trigger_count!= self.trigger_limit:
				self.set_mind("Entry: "+str(self.trigger_count)+"/"+str(self.trigger_limit),DEFAULT)
			else:
				self.set_mind("Entry: Complete",GREEN)

		#print()
		if self.pos == LONG:


			self.tradingplan.data[STOP_LEVEL]=self.stop_price#self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.stop_price)

			self.tradingplan.data[BREAKPRICE]=self.entry_price#self.symbol_data[self.stop]
			#self.tradingplan.tkvars[BREAKPRICE].set(self.entry_price)
			#self.tradingplan.expect_orders = True
			#log_print("Trigger: Purchase: ",self.symbol_name,self.pos,share,"at",self.symbol.get_time())
		
			if share>0:

				spread = self.symbol_data[ASK]-self.symbol_data[BID]

				spread_risk = spread*share/self.risk

				log_print(self.symbol_name,"Current spread:,",spread,"immediate risk loss%",spread_risk)


				if share<5:
					self.ppro_out.send([IOCBUY,self.symbol_name,share,self.symbol_data[ASK]])
				else:

					quarter = share//4
					self.ppro_out.send([IOCBUY,self.symbol_name,quarter,self.symbol_data[ASK]])
					self.tradingplan.passive_initialization(LONG,share-quarter)
				#self.ppro_out.send([IOCBUY,self.symbol_name,share,self.symbol_data[ASK]])
				# if spread_risk < 0.15:
				# 	log_print(self.symbol_name,"Current spread:,",spread,"immediate risk loss%",spread_risk)
				# 	self.ppro_out.send([IOCBUY,self.symbol_name,share,self.symbol_data[ASK]])
				# else:
				# 	log_print(self.symbol_name,"Current spread:,",spread,"immediate risk loss%",spread_risk,"CANCEL ENTRY")
				# 	self.set_mind("Spread TOO HIGH",GREEN)
		elif self.pos ==SHORT:

			self.tradingplan.data[STOP_LEVEL]=self.stop_price#self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.stop_price)

			self.tradingplan.data[BREAKPRICE]=self.entry_price#self.symbol_data[self.stop]
			#self.tradingplan.tkvars[BREAKPRICE].set(self.entry_price)

			if share>0:

				spread = self.symbol_data[ASK]-self.symbol_data[BID]
				spread_risk = spread*share/self.risk

				log_print(self.symbol_name,"Current spread:,",spread,"immediate risk loss%",spread_risk)

				#self.tradingplan.passive_initialization(SHORT,share)

				if share<5:
					self.ppro_out.send([IOCSELL,self.symbol_name,share,self.symbol_data[BID]])
				else:

					quarter = share//4
					self.ppro_out.send([IOCSELL,self.symbol_name,quarter,self.symbol_data[BID]])
					self.tradingplan.passive_initialization(SHORT,share-quarter)

				#self.ppro_out.send([IOCSELL,self.symbol_name,share,self.symbol_data[BID]])
				# if spread_risk < 0.15:

				# else:
				# 	log_print(self.symbol_name,"Current spread:,",spread,"immediate risk loss%",spread_risk,"CANCEL ENTRY")
				# 	self.set_mind("Spread TOO HIGH",GREEN)

				
		else:
			log_print("unidentified side. ")


		self.tradingplan.update_displays()

	def shares_calculator(self):

		if self.pos ==LONG:

			#if this is the last run, set it to day low. (if day low is greater than current stop and lower than ask.)

			#print(self.trigger_limit)

			risk_per_share = abs(self.symbol_data[ASK]-self.symbol_data[self.stop])
			self.stop_price = self.symbol_data[self.stop]


			if self.trigger_count==self.trigger_limit and self.trigger_limit>1 and self.symbol_data[LOW]>self.symbol_data[self.stop] and self.symbol_data[LOW]!=0:

				mid_ = round((self.symbol_data[LOW]+self.symbol_data[self.stop])/2,2)
				risk_per_share = round(abs(self.symbol_data[ASK]-mid_),2)

				log_print(self.symbol_name,"entry near completion, using day low as new stop,low:",self.symbol_data[LOW]," adjusted:",mid_," risk per share:",risk_per_share)
				#self.stop_price = self.symbol_data[LOW]

				if risk_per_share < self.symbol_data[ASK]*0.0012:
					log_print(self.symbol_name,": stop too close:",round(risk_per_share,2)," adjusted to",str(round(self.symbol_data[ASK]*0.0012,2)))
					risk_per_share = self.symbol_data[ASK]*0.0012

					#overwrite the stop price here
					self.stop_price = round(self.symbol_data[BID] - risk_per_share,2)

				else:
					self.stop_price = mid_

		elif self.pos ==SHORT:
			risk_per_share = abs(self.symbol_data[self.stop]-self.symbol_data[BID])
			self.stop_price = self.symbol_data[self.stop]

			if self.trigger_count==self.trigger_limit and self.trigger_limit>1 and self.symbol_data[HIGH]<self.symbol_data[self.stop] and self.symbol_data[HIGH]!=0:

				mid_ = round((self.symbol_data[HIGH]+self.symbol_data[self.stop])/2,2)
				risk_per_share = round(abs(mid_ -self.symbol_data[BID]),2)

				log_print(self.symbol_name,"entry near completion, using day high as new stop. high:",self.symbol_data[HIGH],"adjusted",mid_," risk per share:",risk_per_share)
				

				if risk_per_share < self.symbol_data[ASK]*0.0012:
					log_print(self.symbol_name,": stop too close:",round(risk_per_share,2)," adjusted to",str(round(self.symbol_data[ASK]*0.0012,2)))
					risk_per_share = self.symbol_data[ASK]*0.0012
					self.stop_price = round(self.symbol_data[ASK] + risk_per_share,2)
				else:
					self.stop_price = mid_

		if self.symbol_data[ASK]>100 and risk_per_share <0.2:
			risk_per_share = 0.2

		if self.symbol_data[ASK]<100 and self.symbol_data[ASK]>5 and risk_per_share <0.15:
			risk_per_share = 0.15

		if self.symbol_data[ASK]<5 and risk_per_share <0.04:
			risk_per_share = 0.04

		shares = int((self.risk)/risk_per_share)

		if self.tradingplan.data[TARGET_SHARE]==0:
			self.tradingplan.data[TARGET_SHARE]=shares

		return int(shares/self.trigger_limit)


class EDGX_break_Purchase_trigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out):
		super().__init__(description,conditions,0,1)

		#log_print("purchase_trigger,",self.trigger_timer,self.trigger_limit)
		self.pos = pos

		self.entry = conditions[0][4]
		
		self.stop = stop
		self.ppro_out =ppro_out
		self.risk = risk 
		#self.conditions = conditions 

		self.entry_text =""
		self.trigger_text = ""


		self.entry_price = 0
		self.stop_price = 0

		checker = False
		for i in conditions:
			if len(i)!=5:
				checker = True
				break

		if checker:
			log_print("Trigger problem on purchase_trigger,conditions:",conditions)


		#self.deploy_stop_order()
	#add the actual stuff here.

	def deploy_stop_order(self):

		if self.pos!="":
			self.tradingplan.expect_orders = self.pos
			if self.trigger_count!= self.trigger_limit:
				self.set_mind("Entry: "+str(self.trigger_count)+"/"+str(self.trigger_limit),DEFAULT)
			else:
				self.set_mind("Entry: Waiting for break",GREEN)

		self.break_price = self.symbol.data[self.entry]
		self.share = self.shares_calculator()

		log_print("deploying stoporders ")
		if self.pos == LONG:
			self.ppro_out.send([BREAKUPBUY,self.symbol_name,self.share,self.break_price])

		else:
			self.ppro_out.send([BREAKDOWNSELL,self.symbol_name,self.share,self.break_price])

	def trigger_event(self):

		"""
		HERE I NEED TO SEPERATE BY CASES.
		IF IT IS OVERRIDDEN.
		THEN, 1. PUNCH IN DIRECTLY BY # AMOUNT OF SHARES
			  2. DON"T OVERRIDE STOP VALUE.(ANCARTMANAGE WILL DO IT)
		IF NOT, PROCEED AS USUAL. 
		"""
		
		#log_print(self.symbol_name,"Trigger: ",self.pos,share,"stop :",self.stop_price)

		#print()
		if self.pos == LONG:


			self.tradingplan.data[STOP_LEVEL]=self.stop_price#self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.stop_price)

			self.tradingplan.data[BREAKPRICE]=self.entry_price#self.symbol_data[self.stop]
			#self.tradingplan.tkvars[BREAKPRICE].set(self.entry_price)
			#self.tradingplan.expect_orders = True
			#log_print("Trigger: Purchase: ",self.symbol_name,self.pos,share,"at",self.symbol.get_time())
		
			# if share>0:

			# 	spread = self.symbol_data[ASK]-self.symbol_data[BID]

			# 	spread_risk = spread*share/self.risk

			# 	if spread_risk < 0.15:
			# 		log_print(self.symbol_name,"Current spread:,",spread,"immediate risk loss%",spread_risk)
			# 		self.ppro_out.send([IOCBUY,self.symbol_name,share,self.symbol_data[ASK]])
			# 	else:
			# 		log_print(self.symbol_name,"Current spread:,",spread,"immediate risk loss%",spread_risk,"CANCEL ENTRY")
			# 		self.set_mind("Spread TOO HIGH",GREEN)
		elif self.pos ==SHORT:

			self.tradingplan.data[STOP_LEVEL]=self.stop_price#self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.stop_price)

			self.tradingplan.data[BREAKPRICE]=self.entry_price#self.symbol_data[self.stop]
			#self.tradingplan.tkvars[BREAKPRICE].set(self.entry_price)

			# if share>0:

			# 	spread = self.symbol_data[ASK]-self.symbol_data[BID]
			# 	spread_risk = spread*share/self.risk

			# 	if spread_risk < 0.15:
			# 		log_print(self.symbol_name,"Current spread:,",spread,"immediate risk loss%",spread_risk)
			# 		self.ppro_out.send([IOCSELL,self.symbol_name,share,self.symbol_data[BID]])
			# 	else:
			# 		log_print(self.symbol_name,"Current spread:,",spread,"immediate risk loss%",spread_risk,"CANCEL ENTRY")
			# 		self.set_mind("Spread TOO HIGH",GREEN)

				
		else:
			log_print("unidentified side. ")


		self.tradingplan.update_displays()

	def shares_calculator(self):

		
		risk_per_share = abs(self.symbol_data[RESISTENCE]-self.symbol_data[SUPPORT])
		self.stop_price = self.symbol_data[self.stop]

		if self.symbol_data[ASK]>100 and risk_per_share <0.2:
			risk_per_share = 0.1

		if self.symbol_data[ASK]<100 and self.symbol_data[ASK]>5 and risk_per_share <0.05:
			risk_per_share = 0.05

		if self.symbol_data[ASK]<5 and risk_per_share <0.03:
			risk_per_share = 0.02

		shares = int((self.risk)/risk_per_share)

		if self.tradingplan.data[TARGET_SHARE]==0:
			self.tradingplan.data[TARGET_SHARE]=shares

		return shares


class TwoToOneTriggerOLD(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,description,ppro_out):
		super().__init__(description,None,trigger_timer=0,trigger_limit=3)

		self.ppro_out =ppro_out
		self.conditions = [] 

	def check_conditions(self):

		level = ""
		if self.tradingplan.current_price_level ==1: level= PXT1
		if self.tradingplan.current_price_level ==2: level= PXT2
		if self.tradingplan.current_price_level ==3: level= PXT3

		if self.tradingplan.data[POSITION] == LONG:
			self.conditions = [[SYMBOL_DATA,ASK,">",TP_DATA,level]]
		elif self.tradingplan.data[POSITION] == SHORT:
			self.conditions = [[SYMBOL_DATA,BID,"<",TP_DATA,level]]

		#if self.tradingplan.data[POSITION]!="" and self.tradingplan.data[CURRENT_SHARE]>0:
		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())
	#add the actual stuff here.
	def trigger_event(self):

		share = min(self.tradingplan.data[TARGET_SHARE]//4,self.tradingplan.data[CURRENT_SHARE])

		self.pos = self.tradingplan.data[POSITION]
		#log_print("Trigger: Purchase PPRO EVENT: ",self.symbol_name,s,share,"at","stop:",self.stop,self.symbol_data[self.stop],self.symbol.get_time())

		####################  SIDE.  ########################################
		action = ""
		if self.pos ==LONG:
			action = SELL
		elif self.pos ==SHORT:
			action = BUY

		if action !="":
			if self.tradingplan.current_price_level == 1:
				self.ppro_out.send([action,self.symbol_name,share,self.description])

				#half way.
				self.tradingplan.data[STOP_LEVEL]=self.tradingplan.data[AVERAGE_PRICE]
				self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[AVERAGE_PRICE])

			if self.tradingplan.current_price_level == 2:
				self.ppro_out.send([action,self.symbol_name,share,self.description])

				self.tradingplan.data[STOP_LEVEL]= self.tradingplan.data[PXT1]
				self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[PXT1])

				#move the stop to break even.

			if self.tradingplan.current_price_level == 3:
				self.ppro_out.send([action,self.symbol_name,self.tradingplan.data[CURRENT_SHARE],"manage "])

				#move the stop to first price level. 
		else:
			log_print("unidentified side. ")

		log_print(self.symbol_name," Hit price target", self.tradingplan.current_price_level,"New Stop:",self.tradingplan.data[STOP_LEVEL])
		self.set_mind("Covered No."+str(self.tradingplan.current_price_level)+" lot.",GREEN)
		self.tradingplan.current_price_level+=1
		self.tradingplan.update_displays()



""" The new trigger only adjust the stops. 
"""


class FibonacciManager(AbstractTrigger):
	def __init__(self,description,strategy):
		super().__init__(description,None,trigger_timer=0,trigger_limit=999)
		self.strategy =strategy
		self.conditions = [] 

	def check_conditions(self):

		if self.tradingplan.data[POSITION] == LONG:
			self.conditions = [[SYMBOL_DATA,ASK,">",TP_DATA,FIBCURRENT_MAX],[SYMBOL_DATA,TIMESTAMP,">",SYMBOL_DATA,TRADE_TIMESTAMP]]
		elif self.tradingplan.data[POSITION] == SHORT:
			self.conditions = [[SYMBOL_DATA,BID,"<",TP_DATA,FIBCURRENT_MAX],[SYMBOL_DATA,TIMESTAMP,">",SYMBOL_DATA,TRADE_TIMESTAMP]]

		#print(self.conditions)
		#if self.tradingplan.data[POSITION]!="" and self.tradingplan.data[CURRENT_SHARE]>0:
		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())
	"""
	Do three things.
	1. Reset tradingplan Fibo level.
	2. Recalculate the Fibo levels. (Break price - current max.)
	3. Bring up the new FIB max.
	"""
	def trigger_event(self):
		#1. reset level.
		#self.tradingplan.data[CURRENT_FIB_LEVEL] == 1:
		self.strategy.fib_level = 1
		self.strategy.FibActivated = True

		#2.  Recalculate the Fibo levels. (Break price - current max.)
		gap = abs(self.tradingplan.data[FIBCURRENT_MAX]-self.tradingplan.data[BREAKPRICE])

		if self.tradingplan.data[POSITION] == LONG:

			self.tradingplan.data[FIBLEVEL1] = round(self.tradingplan.data[FIBCURRENT_MAX] - (0.214*gap),2)
			self.tradingplan.data[FIBLEVEL2] = round(self.tradingplan.data[FIBCURRENT_MAX] - (0.382*gap),2)
			self.tradingplan.data[FIBLEVEL3] = round(self.tradingplan.data[FIBCURRENT_MAX] - (0.5*gap),2)
			self.tradingplan.data[FIBLEVEL4] = round(self.tradingplan.data[FIBCURRENT_MAX] - (0.61*gap),2)
			self.tradingplan.data[STOP_LEVEL] = round(self.tradingplan.data[FIBCURRENT_MAX] - (0.61*gap),2)

		elif self.tradingplan.data[POSITION] == SHORT:

			self.tradingplan.data[FIBLEVEL1] = round(self.tradingplan.data[FIBCURRENT_MAX] + (0.214*gap),2)
			self.tradingplan.data[FIBLEVEL2] = round(self.tradingplan.data[FIBCURRENT_MAX] + (0.382*gap),2)
			self.tradingplan.data[FIBLEVEL3] = round(self.tradingplan.data[FIBCURRENT_MAX] + (0.5*gap),2)
			self.tradingplan.data[FIBLEVEL4] = round(self.tradingplan.data[FIBCURRENT_MAX] + (0.61*gap),2)
			self.tradingplan.data[STOP_LEVEL] = round(self.tradingplan.data[FIBCURRENT_MAX] + (0.61*gap),2)
		#3. Bring up the new FIB max. 

		self.tradingplan.data[PXT1] =self.tradingplan.data[FIBLEVEL1] 
		self.tradingplan.data[PXT2] =self.tradingplan.data[FIBLEVEL2] 
		self.tradingplan.data[PXT3] =self.tradingplan.data[FIBLEVEL3] 

		self.tradingplan.tkvars[PXT1].set(self.tradingplan.data[PXT1])
		self.tradingplan.tkvars[PXT2].set(self.tradingplan.data[PXT2])
		self.tradingplan.tkvars[PXT3].set(self.tradingplan.data[PXT3])
		self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])

		
		if self.tradingplan.data[POSITION] == LONG:
			self.tradingplan.data[FIBCURRENT_MAX] += 0.1*self.strategy.risk_per_share
			
		elif self.tradingplan.data[POSITION] == SHORT:
			self.tradingplan.data[FIBCURRENT_MAX] -= 0.1*self.strategy.risk_per_share

		self.tradingplan.adjusting_risk()
		self.tradingplan.update_displays()
		log_print(self.symbol_name,"Fibo recalibrate:",round(self.tradingplan.data[FIBCURRENT_MAX],2),"levels:",self.tradingplan.data[FIBLEVEL1],self.tradingplan.data[FIBLEVEL2],self.tradingplan.data[FIBLEVEL3],self.tradingplan.data[FIBLEVEL4])

class FibonacciTrigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,description,strategy):
		super().__init__(description,None,trigger_timer=5,trigger_limit=999)

		self.strategy =strategy
		self.conditions = []

	def check_conditions(self):

		if self.strategy.FibActivated:
			level = ""

			if self.strategy.fib_level ==1: level= FIBLEVEL1
			elif self.strategy.fib_level ==2: level= FIBLEVEL2
			elif self.strategy.fib_level ==3: level= FIBLEVEL3
			elif self.strategy.fib_level ==4: level= FIBLEVEL4

			if self.tradingplan.data[POSITION] == LONG:
				self.conditions = [[SYMBOL_DATA,ASK,"<",TP_DATA,level]]
			elif self.tradingplan.data[POSITION] == SHORT:
				self.conditions = [[SYMBOL_DATA,BID,">",TP_DATA,level]]

			#if self.tradingplan.data[POSITION]!="" and self.tradingplan.data[CURRENT_SHARE]>0:
			#print(self.conditions)
			#print(self.strategy.fib_level)
			if self.tradingplan.data[POSITION]!="":
				return(super().check_conditions())

			#add the actual stuff here.

	def bring_up_stop(self,new_stop):

		coefficient = 1
		if self.tradingplan.data[POSITION] ==SHORT:
			coefficient = -1

		#print(new_stop,self.tradingplan.data[STOP_LEVEL])
		if new_stop*coefficient >self.tradingplan.data[STOP_LEVEL]*coefficient:
			self.tradingplan.data[STOP_LEVEL]=new_stop
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])

		#print("new stop:",self.tradingplan.data[STOP_LEVEL])

	def trigger_event(self):

		if self.strategy.fib_level == 1:
			self.tradingplan.manage_trades(self.tradingplan.data[POSITION],MINUS,0.08)
			log_print(self.symbol_name,"retracement level:1","Taking off 8%.")
			self.set_mind("retracement level:1")
		if self.strategy.fib_level == 2:
			self.tradingplan.manage_trades(self.tradingplan.data[POSITION],MINUS,0.15)
			log_print(self.symbol_name,"retracement level:2","Taking off 25%.")
			self.set_mind("retracement level:2")
		if self.strategy.fib_level == 3:
			if self.tradingplan.flatten_order==False:
				self.tradingplan.manage_trades(self.tradingplan.data[POSITION],MINUS,0.4)
				log_print(self.symbol_name,"retracement level:3","Taking off 40%.")
			self.set_mind("retracement level:3")
		if self.strategy.fib_level == 4: #fLATTEN
			log_print(self.symbol_name,"Critial level reached, flattening")


		if self.tradingplan.data[USING_STOP]==False:
			self.set_mind("STOP BYPASSING: ON")

		if self.strategy.fib_level<4:
			self.strategy.fib_level +=1
		self.tradingplan.adjusting_risk()
		self.tradingplan.update_displays()

class FibonacciTrigger_trigger_time0(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,description,strategy):
		super().__init__(description,None,trigger_timer=0,trigger_limit=999)

		self.strategy =strategy
		self.conditions = []

	def check_conditions(self):

		if self.strategy.FibActivated:
			level = ""

			if self.strategy.fib_level ==1: level= FIBLEVEL1
			elif self.strategy.fib_level ==2: level= FIBLEVEL2
			elif self.strategy.fib_level ==3: level= FIBLEVEL3
			elif self.strategy.fib_level ==4: level= FIBLEVEL4

			if self.tradingplan.data[POSITION] == LONG:
				self.conditions = [[SYMBOL_DATA,ASK,"<",TP_DATA,level]]
			elif self.tradingplan.data[POSITION] == SHORT:
				self.conditions = [[SYMBOL_DATA,BID,">",TP_DATA,level]]

			#if self.tradingplan.data[POSITION]!="" and self.tradingplan.data[CURRENT_SHARE]>0:
			#print(self.conditions)
			#print(self.strategy.fib_level)
			if self.tradingplan.data[POSITION]!="":
				return(super().check_conditions())

			#add the actual stuff here.

	def bring_up_stop(self,new_stop):

		coefficient = 1
		if self.tradingplan.data[POSITION] ==SHORT:
			coefficient = -1

		#print(new_stop,self.tradingplan.data[STOP_LEVEL])
		if new_stop*coefficient >self.tradingplan.data[STOP_LEVEL]*coefficient:
			self.tradingplan.data[STOP_LEVEL]=new_stop
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])

		#print("new stop:",self.tradingplan.data[STOP_LEVEL])

	def trigger_event(self):

		if self.strategy.fib_level == 1:
			self.tradingplan.manage_trades(self.tradingplan.data[POSITION],MINUS,0.10)
			log_print(self.symbol_name,"retracement level:1","Taking off 10%.")
			self.set_mind("retracement level:1")
		if self.strategy.fib_level == 2:
			self.tradingplan.manage_trades(self.tradingplan.data[POSITION],MINUS,1)
			log_print(self.symbol_name,"retracement level:2","Taking off all.")
			self.set_mind("retracement level:2")
		if self.strategy.fib_level == 3:
			if self.tradingplan.flatten_order==False:
				self.tradingplan.manage_trades(self.tradingplan.data[POSITION],MINUS,0.4)
				log_print(self.symbol_name,"retracement level:3","Taking off 40%.")
			self.set_mind("retracement level:3")
		if self.strategy.fib_level == 4: #fLATTEN
			log_print(self.symbol_name,"Critial level reached, flattening")


		if self.tradingplan.data[USING_STOP]==False:
			self.set_mind("STOP BYPASSING: ON")

		if self.strategy.fib_level<4:
			self.strategy.fib_level +=1
		self.tradingplan.adjusting_risk()
		self.tradingplan.update_displays()


class TwoToOneTrigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,description,strategy):
		super().__init__(description,None,trigger_timer=0,trigger_limit=9)

		self.strategy =strategy
		self.conditions = [] 

		self.second_oders = {}
		self.third_orders = {}

	def set_orders(self,second,third):
		self.second_oders = second
		self.third_orders = third

	def check_conditions(self):

		level = ""

		if self.strategy.orders_level ==1: level= TRIGGER_PRICE_1
		elif self.strategy.orders_level ==2: level= TRIGGER_PRICE_2
		elif self.strategy.orders_level ==3: level= TRIGGER_PRICE_3
		elif self.strategy.orders_level ==4: level= TRIGGER_PRICE_4
		elif self.strategy.orders_level ==5: level= TRIGGER_PRICE_5
		elif self.strategy.orders_level ==6: level= TRIGGER_PRICE_6
		elif self.strategy.orders_level ==7: level= TRIGGER_PRICE_7
		elif self.strategy.orders_level ==8: level= TRIGGER_PRICE_8
		elif self.strategy.orders_level ==9: level= TRIGGER_PRICE_9

		if self.tradingplan.data[POSITION] == LONG:
			self.conditions = [[SYMBOL_DATA,ASK,">",TP_DATA,level]]
		elif self.tradingplan.data[POSITION] == SHORT:
			self.conditions = [[SYMBOL_DATA,BID,"<",TP_DATA,level]]

		#if self.tradingplan.data[POSITION]!="" and self.tradingplan.data[CURRENT_SHARE]>0:

		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())

		#add the actual stuff here.

	def bring_up_stop(self,new_stop):

		coefficient = 1
		if self.tradingplan.data[POSITION] ==SHORT:
			coefficient = -1

		#print(new_stop,self.tradingplan.data[STOP_LEVEL])
		if new_stop*coefficient >self.tradingplan.data[STOP_LEVEL]*coefficient:
			self.tradingplan.data[STOP_LEVEL]=new_stop
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])

		#print("new stop:",self.tradingplan.data[STOP_LEVEL])

	def trigger_event(self):



		if self.strategy.orders_level == 1:
			
			#75
			pass
			# new_stop = round((self.tradingplan.data[STOP_LEVEL]*3+self.tradingplan.data[AVERAGE_PRICE])/4,2)
			# self.bring_up_stop(new_stop)

			# self.set_mind("75% risk",GREEN)
			self.strategy.deploy_n_batch_torpedoes(3)

		if self.strategy.orders_level == 2:
			
			#BREAK EVEN
			pass
			# new_stop =round((self.tradingplan.data[STOP_LEVEL]*2+self.tradingplan.data[AVERAGE_PRICE])/3,2)
			# self.bring_up_stop(new_stop)

			# self.set_mind("Half risk",GREEN)

		if self.strategy.orders_level == 3:
			
			#BREAK EVEN

			new_stop =round(self.tradingplan.data[AVERAGE_PRICE],2)
			#self.bring_up_stop(new_stop)

			self.set_mind("Break even",GREEN)

		if self.strategy.orders_level == 4:

			new_stop =round(self.tradingplan.data[AVERAGE_PRICE],2)
			#self.bring_up_stop(new_stop)

			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)
			self.tradingplan.current_price_level = 2
			self.set_mind("Covered No."+str(1)+" lot.",GREEN)

		if self.strategy.orders_level == 5:
			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)

			new_stop =round(self.tradingplan.data[TRIGGER_PRICE_3],2)
			#self.bring_up_stop(new_stop)
			
		if self.strategy.orders_level == 6:
			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)
			self.tradingplan.current_price_level = 3
			self.set_mind("Covered No."+str(2)+" lot.",GREEN)

			new_stop =round(self.tradingplan.data[TRIGGER_PRICE_4],2)
			self.bring_up_stop(new_stop)

		if self.strategy.orders_level == 7:
			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)

			new_stop =round(self.tradingplan.data[TRIGGER_PRICE_5],2)
			self.bring_up_stop(new_stop)

		if self.strategy.orders_level == 8:
			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)
			new_stop =round(self.tradingplan.data[TRIGGER_PRICE_6],2)
			self.bring_up_stop(new_stop)
		# log_print(self.symbol_name," Hit price target", self.tradingplan.current_price_level,"New Stop:",self.tradingplan.data[STOP_LEVEL])


		if self.tradingplan.data[USING_STOP]==False:
			self.set_mind("STOP BYPASSING: ON")

		self.strategy.orders_level +=1
		self.tradingplan.adjusting_risk()
		self.tradingplan.update_displays()


### once ema count exceed X. 

class EMAManager(AbstractTrigger):
	def __init__(self,description,strategy):
		super().__init__(description,None,trigger_timer=0,trigger_limit=9999)
		self.strategy =strategy
		self.conditions = [] 

	def check_conditions(self):

		self.conditions = [[SYMBOL_DATA,EMACOUNT,">",SYMBOL_DATA,CUSTOM]]
		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())
	"""
	Do three things.
	1. Reset tradingplan Fibo level.
	2. Recalculate the Fibo levels. (Break price - current max.)
	3. Bring up the new FIB max.
	"""
	def trigger_event(self):
		#1. reset level.
		#self.tradingplan.data[CURRENT_FIB_LEVEL] == 1:

		self.symbol.data[CUSTOM] = self.symbol.data[EMACOUNT]


		if self.tradingplan.data[POSITION] == LONG:

			new_stop = self.symbol.data[EMA8L]

			self.tradingplan.data[STOP_LEVEL]=new_stop
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])

		elif self.tradingplan.data[POSITION] == SHORT:


			new_stop = self.symbol.data[EMA8H]
			self.tradingplan.data[STOP_LEVEL]=new_stop
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])

		self.tradingplan.adjusting_risk()
		self.tradingplan.update_displays()
		log_print(self.symbol_name,"EMA recalibrate:",self.tradingplan.data[STOP_LEVEL])


class TrendEMAManager(AbstractTrigger):
	def __init__(self,description,strategy):
		super().__init__(description,None,trigger_timer=0,trigger_limit=9999)
		self.strategy =strategy
		self.conditions = [] 

		

	def check_conditions(self):

		#print("Checking",self.tradingplan.data[CUR_PROFIT_LEVEL],self.symbol.data[CUSTOM])
		self.conditions = [[TP_DATA,CUR_PROFIT_LEVEL,">",SYMBOL_DATA,CUSTOM]]
		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())
	"""
	Do three things.
	1. Reset tradingplan Fibo level.
	2. Recalculate the Fibo levels. (Break price - current max.)
	3. Bring up the new FIB max.
	"""
	def trigger_event(self):
		#1. reset level.
		#self.tradingplan.data[CURRENT_FIB_LEVEL] == 1:


		if self.tradingplan.data[POSITION] == LONG:

			new_stop = self.symbol.data[EMA21L]

			self.tradingplan.data[STOP_LEVEL]=new_stop
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])

		elif self.tradingplan.data[POSITION] == SHORT:


			new_stop = self.symbol.data[EMA21H]
			self.tradingplan.data[STOP_LEVEL]=new_stop
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])

		self.tradingplan.adjusting_risk()
		self.tradingplan.update_displays()

		#log_print(self.symbol_name,"EMA recalibrate:",self.tradingplan.data[STOP_LEVEL])


#SemiManualManager

class SemiManualManager(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,description,strategy):
		super().__init__(description,None,trigger_timer=0,trigger_limit=1)

		self.strategy =strategy
		self.conditions = [] 

		self.second_oders = {}
		self.third_orders = {}

	def set_orders(self,second,third):
		self.second_oders = second
		self.third_orders = third

	def check_conditions(self):

		#print("chekcing",self.tradingplan.data[TRIGGER_PRICE_1])
		level = TRIGGER_PRICE_1

		if self.tradingplan.data[POSITION] == LONG:
			self.conditions = [[SYMBOL_DATA,ASK,">",TP_DATA,level]]
		elif self.tradingplan.data[POSITION] == SHORT:
			self.conditions = [[SYMBOL_DATA,BID,"<",TP_DATA,level]]

		#if self.tradingplan.data[POSITION]!="" and self.tradingplan.data[CURRENT_SHARE]>0:

		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())

		#add the actual stuff here.



	def trigger_event(self):

		if self.strategy.orders_level == 1:
			action = ""
			if self.tradingplan.data[POSITION] ==LONG:
				action = LIMITSELL
			elif self.tradingplan.data[POSITION] ==SHORT:
				action = LIMITBUY

			#print(action,self.tradingplan.data[CURRENT_SHARE]//2," shares",self.tradingplan.data[TRIGGER_PRICE_2])
			self.ppro_out.send([action,self.symbol_name,self.tradingplan.data[TRIGGER_PRICE_2],self.tradingplan.data[CURRENT_SHARE]//2,0,"Exit price "])
			self.strategy.orders_level+=1
		# new_stop =round(self.tradingplan.data[TRIGGER_PRICE_6],2)
		# self.bring_up_stop(new_stop)
		# log_print(self.symbol_name," Hit price target", self.tradingplan.current_price_level,"New Stop:",self.tradingplan.data[STOP_LEVEL])





class HoldTilCloseManager(AbstractTrigger):
	def __init__(self,description,strategy):
		super().__init__(description,None,trigger_timer=0,trigger_limit=9999)
		self.strategy =strategy
		self.conditions = [] 

	def check_conditions(self):

		self.conditions = [[SYMBOL_DATA,TIMESTAMP,">",SYMBOL_DATA,TRADE_TIMESTAMP]]
		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())

	def trigger_event(self):


		if self.tradingplan.data[POSITION] == LONG:


			new_stop = round(self.symbol.data[BID]+0.5,2)

			self.tradingplan.data[STOP_LEVEL]=new_stop
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])

		elif self.tradingplan.data[POSITION] == SHORT:


			new_stop = round(self.symbol.data[ASK]-0.5,2)
			self.tradingplan.data[STOP_LEVEL]=new_stop
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])

		self.tradingplan.adjusting_risk()
		self.tradingplan.update_displays()

		log_print(self.symbol_name,"HTC finished",self.tradingplan.data[STOP_LEVEL])






class ANCART_trigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,description,ppro_out):
		super().__init__(description,None,trigger_timer=0,trigger_limit=3)

		self.ppro_out =ppro_out
		self.conditions = [] 

	def check_conditions(self):

		level = ""
		if self.tradingplan.current_price_level ==1: level= PXT1
		if self.tradingplan.current_price_level ==2: level= PXT2
		if self.tradingplan.current_price_level ==3: level= PXT3

		if self.tradingplan.data[POSITION] == LONG:
			self.conditions = [[SYMBOL_DATA,ASK,">",TP_DATA,level]]
		elif self.tradingplan.data[POSITION] == SHORT:
			self.conditions = [[SYMBOL_DATA,BID,"<",TP_DATA,level]]

		#if self.tradingplan.data[POSITION]!="" and self.tradingplan.data[CURRENT_SHARE]>0:
		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())
	#add the actual stuff here.
	def trigger_event(self):

		share = min(self.tradingplan.data[TARGET_SHARE]//3,self.tradingplan.data[CURRENT_SHARE])

		self.pos = self.tradingplan.data[POSITION]
		#log_print("Trigger: Purchase PPRO EVENT: ",self.symbol_name,s,share,"at","stop:",self.stop,self.symbol_data[self.stop],self.symbol.get_time())

		####################  SIDE.  ########################################
		action = ""
		if self.pos ==LONG:
			action = SELL
		elif self.pos ==SHORT:
			action = BUY

		if action !="":
			if self.tradingplan.current_price_level == 1:
				self.ppro_out.send([action,self.symbol_name,share,self.description])

				self.tradingplan.data[STOP_LEVEL] = self.tradingplan.data[AVERAGE_PRICE]
				self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[AVERAGE_PRICE])

			if self.tradingplan.current_price_level == 2:

				self.ppro_out.send([action,self.symbol_name,share,self.description])

				self.tradingplan.data[STOP_LEVEL] = self.tradingplan.data[PXT1]

				self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])
				#move the stop to break even.

			if self.tradingplan.current_price_level == 3:
				self.ppro_out.send([action,self.symbol_name,self.tradingplan.data[CURRENT_SHARE],"manage "])

				#move the stop to first price level. 
		else:
			log_print("unidentified side. ")

		log_print(self.symbol_name," Hit price target", self.tradingplan.current_price_level,"New Stop:",self.tradingplan.data[STOP_LEVEL])

		i
		self.set_mind("Covered No."+str(self.tradingplan.current_price_level)+" lot.",GREEN)
		self.tradingplan.current_price_level+=1
		self.tradingplan.update_displays()

class SmartTrailing_trigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,description,SmartTrailStrategy):
		super().__init__(description,None,trigger_timer=0,trigger_limit=2)

		self.SmartTrail =SmartTrailStrategy
		self.conditions = [] 

	def check_conditions(self):

		level = ""
		if self.tradingplan.current_price_level ==1: level= PXT1
		if self.tradingplan.current_price_level ==2: level= PXT2

		#i need to think of a way to let it forever stays at level 3. 
		if self.tradingplan.current_price_level ==3: level= PXT3


		if self.tradingplan.data[POSITION] == LONG:
			self.conditions = [[SYMBOL_DATA,ASK,">",TP_DATA,level]]
		elif self.tradingplan.data[POSITION] == SHORT:
			self.conditions = [[SYMBOL_DATA,BID,"<",TP_DATA,level]]

		#if self.tradingplan.data[POSITION]!="" and self.tradingplan.data[CURRENT_SHARE]>0:
		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())


	#add the actual stuff here.
	def trigger_event(self):

		#share = min(self.tradingplan.data[TARGET_SHARE]//4,self.tradingplan.data[CURRENT_SHARE])

		self.pos = self.tradingplan.data[POSITION]
		#log_print("Trigger: Purchase PPRO EVENT: ",self.symbol_name,s,share,"at","stop:",self.stop,self.symbol_data[self.stop],self.symbol.get_time())

		####################  SIDE.  ########################################
		action = ""
		if self.pos ==LONG:
			action = SELL
		elif self.pos ==SHORT:
			action = BUY

		if action !="":
			if self.tradingplan.current_price_level == 1:

				#just change the STOP!!!!
				#half way.
				half_way = round((self.tradingplan.data[STOP_LEVEL] + self.tradingplan.data[AVERAGE_PRICE])/2,2)
				self.tradingplan.data[STOP_LEVEL]=half_way
				self.tradingplan.tkvars[STOP_LEVEL].set(half_way)

				self.tradingplan.adjusting_risk()
				log_print(self.symbol_name,"Reduce to 0.50 risk.")
				self.set_mind("50% risk",GREEN)


			if self.tradingplan.current_price_level == 2:

				#once it's level 2, it stays here. 

				self.tradingplan.data[STOP_LEVEL]=self.tradingplan.data[AVERAGE_PRICE]
				self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[AVERAGE_PRICE])
				self.SmartTrail.distance = abs(self.tradingplan.data[PXT2]-self.tradingplan.data[STOP_LEVEL])
				self.tradingplan.adjusting_risk()
				#self.set_mind("risk-free",GREEN)
				log_print(self.symbol_name,"Break even initiated.")
				#move the stop to break even.

			#if self.tradingplan.current_price_level == 3:
				#self.ppro_out.send([action,self.symbol_name,self.tradingplan.data[CURRENT_SHARE],"manage "])

				#move the stop to first price level. 
		else:
			log_print("unidentified side. ")

		self.tradingplan.current_price_level+=1
		self.tradingplan.update_displays()

class Three_price_trigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,description,ppro_out):
		super().__init__(description,None,trigger_timer=0,trigger_limit=3)

		self.ppro_out =ppro_out
		self.conditions = [] 

	def check_conditions(self):

		level = ""
		if self.tradingplan.current_price_level ==1: level= PXT1
		if self.tradingplan.current_price_level ==2: level= PXT2
		if self.tradingplan.current_price_level ==3: level= PXT3

		if self.tradingplan.data[POSITION] == LONG:
			self.conditions = [[SYMBOL_DATA,ASK,">",TP_DATA,level]]
		elif self.tradingplan.data[POSITION] == SHORT:
			self.conditions = [[SYMBOL_DATA,BID,"<",TP_DATA,level]]

		#if self.tradingplan.data[POSITION]!="" and self.tradingplan.data[CURRENT_SHARE]>0:
		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())
	#add the actual stuff here.
	def trigger_event(self):

		share = min(self.tradingplan.data[TARGET_SHARE]//4,self.tradingplan.data[CURRENT_SHARE])

		self.pos = self.tradingplan.data[POSITION]
		#log_print("Trigger: Purchase PPRO EVENT: ",self.symbol_name,s,share,"at","stop:",self.stop,self.symbol_data[self.stop],self.symbol.get_time())

		####################  SIDE.  ########################################
		action = ""
		if self.pos ==LONG:
			action = SELL
		elif self.pos ==SHORT:
			action = BUY

		if action !="":
			if self.tradingplan.current_price_level == 1:
				self.ppro_out.send([action,self.symbol_name,share,self.description])

				#half way.
				half_way = round((self.tradingplan.data[STOP_LEVEL] + self.tradingplan.data[AVERAGE_PRICE])/2,2)
				self.tradingplan.data[STOP_LEVEL]=half_way
				self.tradingplan.tkvars[STOP_LEVEL].set(half_way)

			if self.tradingplan.current_price_level == 2:
				self.ppro_out.send([action,self.symbol_name,share,self.description])
				self.tradingplan.data[STOP_LEVEL]=self.tradingplan.data[AVERAGE_PRICE]
				self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[AVERAGE_PRICE])
				#move the stop to break even.

			if self.tradingplan.current_price_level == 3:
				self.ppro_out.send([action,self.symbol_name,self.tradingplan.data[CURRENT_SHARE],"manage "])

				#move the stop to first price level. 
		else:
			log_print("unidentified side. ")

		log_print(self.symbol_name," Hit price target", self.tradingplan.current_price_level,"New Stop:",self.tradingplan.data[STOP_LEVEL])
		self.set_mind("Covered No."+str(self.tradingplan.current_price_level)+" lot.",GREEN)
		self.tradingplan.current_price_level+=1
		self.tradingplan.update_displays()




class EMTrigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,description,strategy):
		super().__init__(description,None,trigger_timer=0,trigger_limit=9)

		self.strategy =strategy
		self.conditions = [] 

		self.second_oders = {}
		self.third_orders = {}

	def set_orders(self,second,third):
		self.second_oders = second
		self.third_orders = third

	def check_conditions(self):

		level = ""

		if self.strategy.orders_level ==1: level= TRIGGER_PRICE_1
		elif self.strategy.orders_level ==2: level= TRIGGER_PRICE_2
		elif self.strategy.orders_level ==3: level= TRIGGER_PRICE_3
		elif self.strategy.orders_level ==4: level= TRIGGER_PRICE_4
		elif self.strategy.orders_level ==5: level= TRIGGER_PRICE_5
		elif self.strategy.orders_level ==6: level= TRIGGER_PRICE_6
		elif self.strategy.orders_level ==7: level= TRIGGER_PRICE_7
		elif self.strategy.orders_level ==8: level= TRIGGER_PRICE_8
		elif self.strategy.orders_level ==9: level= TRIGGER_PRICE_9

		if self.tradingplan.data[POSITION] == LONG:
			self.conditions = [[SYMBOL_DATA,ASK,">",TP_DATA,level]]
		elif self.tradingplan.data[POSITION] == SHORT:
			self.conditions = [[SYMBOL_DATA,BID,"<",TP_DATA,level]]

		#if self.tradingplan.data[POSITION]!="" and self.tradingplan.data[CURRENT_SHARE]>0:

		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())

		#add the actual stuff here.

	def bring_up_stop(self,new_stop):

		coefficient = 1
		if self.tradingplan.data[POSITION] ==SHORT:
			coefficient = -1

		#print(new_stop,self.tradingplan.data[STOP_LEVEL])
		if new_stop*coefficient >self.tradingplan.data[STOP_LEVEL]*coefficient:
			self.tradingplan.data[STOP_LEVEL]=new_stop
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])

		#print("new stop:",self.tradingplan.data[STOP_LEVEL])

	def trigger_event(self):



		if self.strategy.orders_level == 1:

			#75
			new_stop = round((self.tradingplan.data[STOP_LEVEL]*3+self.tradingplan.data[AVERAGE_PRICE])/4,2)
			self.bring_up_stop(new_stop)
			self.set_mind("Break even",GREEN)

		if self.strategy.orders_level == 2:

			#BREAK EVEN

			new_stop =round(self.tradingplan.data[AVERAGE_PRICE],2)
			self.bring_up_stop(new_stop)
			# new_stop =round((self.tradingplan.data[STOP_LEVEL]*2+self.tradingplan.data[AVERAGE_PRICE])/3,2)
			# self.bring_up_stop(new_stop)
			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)

			self.set_mind("30%",GREEN)

		if self.strategy.orders_level == 3:

			#BREAK EVEN

			# new_stop =round(self.tradingplan.data[AVERAGE_PRICE],2)
			# self.bring_up_stop(new_stop)

			self.set_mind("50%",GREEN)
			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)

		if self.strategy.orders_level == 4:

			# new_stop =round(self.tradingplan.data[AVERAGE_PRICE],2)
			# self.bring_up_stop(new_stop)

			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)
			self.tradingplan.current_price_level = 2
			self.set_mind("70%",GREEN)

		if self.strategy.orders_level == 5:
			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)

			self.set_mind("100%",GREEN)
			# new_stop =round(self.tradingplan.data[TRIGGER_PRICE_3],2)
			# self.bring_up_stop(new_stop)

		if self.strategy.orders_level == 6:
			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)
			self.tradingplan.current_price_level = 3
			self.set_mind("120%",GREEN)

			# new_stop =round(self.tradingplan.data[TRIGGER_PRICE_4],2)
			# self.bring_up_stop(new_stop)

		if self.strategy.orders_level == 7:
			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)

			# new_stop =round(self.tradingplan.data[TRIGGER_PRICE_5],2)
			# self.bring_up_stop(new_stop)
			self.set_mind("130%",GREEN)
		if self.strategy.orders_level == 8:
			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)
			# new_stop =round(self.tradingplan.data[TRIGGER_PRICE_6],2)
			# self.bring_up_stop(new_stop)
			self.set_mind("150%",GREEN)
		# log_print(self.symbol_name," Hit price target", self.tradingplan.current_price_level,"New Stop:",self.tradingplan.data[STOP_LEVEL])


		if self.tradingplan.data[USING_STOP]==False:
			self.set_mind("STOP BYPASSING: ON")

		self.strategy.orders_level +=1
		self.tradingplan.adjusting_risk()
		self.tradingplan.update_displays()

