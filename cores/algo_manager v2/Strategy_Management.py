from constant import *
from Symbol import *
from Triggers import *
from Util_functions import *
from Strategy import *
import threading
import time
#import sys, inspect
# "Omnissiah, Omnissiah.

try:
	import keyboard
except:
	print("keyboard not found")

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

""" MANAGEMENT PLAN"""

class ManagementStrategy(Strategy):

	def __init__(self,name,symbol:Symbol,tradingplan):
		super().__init__(name,symbol,tradingplan)

		self.management_start = False
		self.initialized = False
		self.shares_loaded = False
	""" for management plan only """
	def on_loading_up(self):
		pass

	""" for management plan only """
	def on_start(self):
		self.manaTrigger.total_reset()
		self.tradingplan.current_price_level = 1
		self.set_mind("")
		log_print(self.symbol_name," ",self.strategy_name ," starts")


	""" for management plan only """
	def on_deploying(self):
		self.current_triggers = set()
		for i in self.initial_triggers:
			self.current_triggers.add(i)

	def reset(self):
		pass

class OneToTWORiskReward(ManagementStrategy):

	def __init__(self,symbol,tradingplan):

		super().__init__("Management: 1-to-2 risk-reward ",symbol,tradingplan)

		self.manaTrigger = TwoToOneTrigger("manage",self)

		self.add_initial_triggers(self.manaTrigger)

		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		###upon activating, reset all parameters. 
		self.total_orders = None
		self.orders_level = 1

		self.price = self.tradingplan.data[AVERAGE_PRICE]
		self.stop = self.tradingplan.data[STOP_LEVEL]

	def on_loading_up(self): #call this whenever the break at price changes. 

		self.price = self.tradingplan.data[AVERAGE_PRICE]
		self.stop = self.tradingplan.data[STOP_LEVEL]
		self.gap = abs(self.price-self.stop)

		coefficient = 1

		if self.tradingplan.data[POSITION] == LONG:
			coefficient = 1
		elif self.tradingplan.data[POSITION] == SHORT:
			coefficient = -1

		"""
		px1 = 0.3 #break even
		px2 = 1 #set second barage 
		px3 = 2 #set third barage
		px4 = 3.2 #over and out.

		"""
		self.tradingplan.data[TRIGGER_PRICE_1] = round(self.price+coefficient*self.gap*0.2,2)  #75%
		self.tradingplan.data[TRIGGER_PRICE_2] = round(self.price+coefficient*self.gap*0.3,2)  #half
		self.tradingplan.data[TRIGGER_PRICE_3] = round(self.price+coefficient*self.gap*0.5,2)  #br even
		self.tradingplan.data[TRIGGER_PRICE_4] = round(self.price+coefficient*self.gap*0.7,2)  #second
		self.tradingplan.data[TRIGGER_PRICE_5] = round(self.price+coefficient*self.gap*1.2,2)  #third
		self.tradingplan.data[TRIGGER_PRICE_6] = round(self.price+coefficient*self.gap*1.7,2)  #fourth
		self.tradingplan.data[TRIGGER_PRICE_7] = round(self.price+coefficient*self.gap*2.2,2)  #fifth
		self.tradingplan.data[TRIGGER_PRICE_8] = round(self.price+coefficient*self.gap*2.7,2)  #sixth
		self.tradingplan.data[TRIGGER_PRICE_9] = round(self.price+coefficient*self.gap*3.2,2)  #FINAL

		#set the price levels.
		#log_print(id_,"updating price levels.",price,self.price_levels[id_][1],self.price_levels[id_][2],self.price_levels[id_][3])

		self.tradingplan.tkvars[AUTOMANAGE].set(True)
		self.tradingplan.tkvars[PXT1].set(self.tradingplan.data[TRIGGER_PRICE_1])
		self.tradingplan.tkvars[PXT2].set(self.tradingplan.data[TRIGGER_PRICE_7])
		self.tradingplan.tkvars[PXT3].set(self.tradingplan.data[TRIGGER_PRICE_9])

		log_print(self.symbol_name,"Management price target adjusted:",self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])

		self.shares_loaded = True

		if self.initialized == False and self.management_start==True:
			self.on_start()

	def on_start(self):

		if self.shares_loaded:

			super().on_start()

			""" send out the limit orders """

			if self.tradingplan.data[USING_STOP]==False:
				self.set_mind("STOP BYPASSING: ON")

			self.tradingplan.current_price_level = 1
			self.orders_level = 1
			first_lot,second_lot,third_lot = self.shares_calculator(self.tradingplan.data[TARGET_SHARE])
			self.orders_organizer(first_lot,second_lot,third_lot)
			#self.deploy_n_batch_torpedoes(3)
			self.initialized == True
		else:
			self.management_start=True

	def shares_calculator(self,shares):

		if shares<3:
			return 0,shares,0
		else:
			# first_lot = int(shares/3)
			# third_lot = shares - 2*first_lot
			third_lot = int(shares/2)
			first_lot = int((shares - third_lot)/3)
			second_lot = shares - first_lot - third_lot
			#print(first_lot,second_lot,third_lot)
			return first_lot,second_lot,third_lot

	def deploy_n_batch_torpedoes(self,n):

		self.deploy_orders(self.total_orders[n-3])


	def deploy_orders(self,orders):

		coefficient = 1
		action = ""
		if self.tradingplan.data[POSITION] == LONG:
			action = LIMITSELL

		elif self.tradingplan.data[POSITION] == SHORT:
			action = LIMITBUY
			coefficient = -1

		#add some delay in here, random seconds. 
		#wait = [0.5,1.1,1.3,1.4,1.6]
		wait = [0,1,2,3,0]
		c = 0
		for key in sorted(orders.keys()):
			if orders[key]>0:
				price = round(self.price+coefficient*self.gap*key,2)
				share = orders[key]
				self.ppro_out.send([action,self.symbol_name,price,share,wait[c],"Exit price "])
				c+=1 

	def orders_organizer(self,first,second,third):

		### Arange this way to distribute it around the key areas. 
		first_lot  =  [0.5,1.0,0.4,0.9,0.6,1.1,0.7,1.2,0.35,0.8]
		second_lot =  [1.5,2.0,1.4,1.9,1.6,2.1,1.7,2.2,1.3,1.8]
		third_lot  =  [2.5,3.0,2.4,2.9,2.6,3.1,2.7,3.2,2.3,2.8]

		all_lots = [first_lot,second_lot,third_lot]
		shares = [first,second,third]

		new_shares = [[0,0,0,0,0,0,0,0,0,0] for i in range(3)]

		for i in range(len(new_shares)):
			for j in range(shares[i]):
				new_shares[i][j%10] +=1

		share_distribution = {}
		for i in range(len(new_shares)):
			for j in range(len(new_shares[i])):
				share_distribution[all_lots[i][j]] = new_shares[i][j]

		# Now we have all orders. let's slice them up.

		total_list = []
		total_list.extend(first_lot)
		total_list.extend(second_lot)
		total_list.extend(third_lot)
		list.sort(total_list)
		orders = [total_list[5*i:5*i+5] for i in range(6)]
		#now chop the total_list into 6 sections. then grab the shares from all_orders

		total_orders = []
		for i in range(len(orders)):
			total_orders.append({})
			for j in range(len(orders[i])):
				total_orders[i][orders[i][j]] = share_distribution[orders[i][j]]
			
		self.total_orders = total_orders

class FibonacciOnly(ManagementStrategy):

	def __init__(self,symbol,tradingplan):

		super().__init__("Management: 1-to-2 risk-reward with Fibo",symbol,tradingplan)

		self.manaTrigger = FibonacciManager("Fibonacci manager",self)
		self.fiboTrigger = FibonacciTrigger("Fibonacci trigger",self)

		self.add_initial_triggers(self.manaTrigger)
		self.add_initial_triggers(self.fiboTrigger)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		###upon activating, reset all parameters. 
		self.total_orders = None
		self.FibActivated = False
		self.risk_per_share = 0
		self.orders_level = 1
		self.fib_level = 1
		self.initialized = False

		self.price = self.tradingplan.data[AVERAGE_PRICE]
		self.stop = self.tradingplan.data[STOP_LEVEL]



	def on_loading_up(self): #call this whenever the break at price changes. Onl
		#print("loading up:",self.initialized)
		if not self.initialized:
			log_print("LOADING UP!!!!","init:",self.initialized,self.management_start)
			self.price = self.tradingplan.data[AVERAGE_PRICE]
			self.stop = self.tradingplan.data[STOP_LEVEL]
			self.risk_per_share = abs(self.price-self.stop)

			coefficient = 1

			if self.tradingplan.data[POSITION] == LONG:
				coefficient = 1
			elif self.tradingplan.data[POSITION] == SHORT:
				coefficient = -1

			"""
			px1 = 0.3 #break even
			px2 = 1 #set second barage
			px3 = 2 #set third barage
			px4 = 3.2 #over and out.

			"""
			self.tradingplan.data[TRIGGER_PRICE_1] = round(self.price+coefficient*self.risk_per_share*0.2,2)  #75%
			self.tradingplan.data[TRIGGER_PRICE_2] = round(self.price+coefficient*self.risk_per_share*0.3,2)  #half
			self.tradingplan.data[FIBCURRENT_MAX] = round(self.price+coefficient*self.risk_per_share*0.5,2)  #br even
			self.tradingplan.data[TRIGGER_PRICE_3] = round(self.price+coefficient*self.risk_per_share*0.5,2)  #br even


			self.tradingplan.data[PXT1] =self.tradingplan.data[FIBCURRENT_MAX]
			self.tradingplan.tkvars[PXT1].set(self.tradingplan.data[PXT1])


			self.tradingplan.tkvars[AUTOMANAGE].set(True)
			# self.tradingplan.tkvars[PXT1].set(self.tradingplan.data[TRIGGER_PRICE_1])
			# self.tradingplan.tkvars[PXT2].set(self.tradingplan.data[TRIGGER_PRICE_7])
			# self.tradingplan.tkvars[PXT3].set(self.tradingplan.data[TRIGGER_PRICE_9])

			#log_print(self.symbol_name,"Management price target adjusted:",self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])

			self.shares_loaded = True

			#shouldn't start here. because, sometime multiple entry is required. 7/10
			#No. This is a mechanism that works for INSTANT. if already started, but not intialized. restart the whole thing.

			if self.initialized == False and self.management_start==True:
				self.on_start()

	def on_start(self):

		if self.shares_loaded:

			self.symbol.data[TRADE_TIMESTAMP] = self.symbol.data[TIMESTAMP]+180

			super().on_start()

			""" send out the limit orders """
			log_print(self.symbol_name,"Fib-only starting")
			if self.tradingplan.data[USING_STOP]==False:
				self.set_mind("STOP BYPASSING: ON")

			self.fib_level = 1
			self.FibActivated = False
			self.tradingplan.current_price_level = 1
			self.orders_level = 1
			self.initialized = True
			#log_print("HELLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLO",self.initialized)
		else:
			self.management_start=True

	def shares_calculator(self,shares):

		if shares<3:
			return 0,shares,0
		else:
			# first_lot = int(shares/3)
			# third_lot = shares - 2*first_lot
			third_lot = int(shares/2)
			first_lot = int((shares - third_lot)/3)
			second_lot = shares - first_lot - third_lot
			#print(first_lot,second_lot,third_lot)
			return first_lot,second_lot,third_lot

	def on_deploying(self): #refresh it when reusing.
		#print("ON DEPLOYING")
		self.initialized = False
		self.shares_loaded = False
		self.fib_level = 1
		self.FibActivated = False
		self.tradingplan.current_price_level = 1
		self.orders_level = 1
		super().on_deploying()

	def reset(self):
		self.initialized = False

class FiboNoSoft(ManagementStrategy):

	def __init__(self,symbol,tradingplan):

		super().__init__("Management: 1-to-2 risk-reward with Fibo",symbol,tradingplan)

		self.manaTrigger = FibonacciManager("Fibonacci manager",self)
		self.fiboTrigger = FibonacciTrigger_trigger_time0("Fibonacci trigger",self)

		self.add_initial_triggers(self.manaTrigger)
		self.add_initial_triggers(self.fiboTrigger)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		###upon activating, reset all parameters.
		self.total_orders = None
		self.FibActivated = False
		self.risk_per_share = 0
		self.orders_level = 1
		self.fib_level = 1
		self.initialized = False

		self.price = self.tradingplan.data[AVERAGE_PRICE]
		self.stop = self.tradingplan.data[STOP_LEVEL]

	def on_loading_up(self): #call this whenever the break at price changes. Onl

		log_print("LOADING UP!!!!","init:",self.initialized,self.management_start)
		if not self.initialized:

			self.price = self.tradingplan.data[AVERAGE_PRICE]
			self.stop = self.tradingplan.data[STOP_LEVEL]
			self.risk_per_share = abs(self.price-self.stop)

			coefficient = 1

			if self.tradingplan.data[POSITION] == LONG:
				coefficient = 1
			elif self.tradingplan.data[POSITION] == SHORT:
				coefficient = -1

			"""
			px1 = 0.3 #break even
			px2 = 1 #set second barage
			px3 = 2 #set third barage
			px4 = 3.2 #over and out.

			"""
			self.tradingplan.data[TRIGGER_PRICE_1] = round(self.price+coefficient*self.risk_per_share*0.2,2)  #75%
			self.tradingplan.data[TRIGGER_PRICE_2] = round(self.price+coefficient*self.risk_per_share*0.3,2)  #half
			self.tradingplan.data[FIBCURRENT_MAX] = round(self.price+coefficient*self.risk_per_share*0.5,2)  #br even
			self.tradingplan.data[TRIGGER_PRICE_3] = round(self.price+coefficient*self.risk_per_share*0.5,2)  #br even


			self.tradingplan.data[PXT1] =self.tradingplan.data[FIBCURRENT_MAX]
			self.tradingplan.tkvars[PXT1].set(self.tradingplan.data[PXT1])


			self.tradingplan.tkvars[AUTOMANAGE].set(True)
			# self.tradingplan.tkvars[PXT1].set(self.tradingplan.data[TRIGGER_PRICE_1])
			# self.tradingplan.tkvars[PXT2].set(self.tradingplan.data[TRIGGER_PRICE_7])
			# self.tradingplan.tkvars[PXT3].set(self.tradingplan.data[TRIGGER_PRICE_9])

			#log_print(self.symbol_name,"Management price target adjusted:",self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])

			self.shares_loaded = True

			#shouldn't start here. because, sometime multiple entry is required. 7/10
			#No. This is a mechanism that works for INSTANT. if already started, but not intialized. restart the whole thing.

			if self.initialized == False and self.management_start==True:
				self.on_start()

	def on_start(self):

		if self.shares_loaded:

			super().on_start()


			""" send out the limit orders """

			if self.tradingplan.data[USING_STOP]==False:
				self.set_mind("STOP BYPASSING: ON")

			self.fib_level = 1
			self.FibActivated = False
			self.tradingplan.current_price_level = 1
			self.orders_level = 1
			self.initialized = True
			#log_print("HELLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLO",self.initialized)
		else:
			self.management_start=True

	def shares_calculator(self,shares):

		if shares<3:
			return 0,shares,0
		else:
			# first_lot = int(shares/3)
			# third_lot = shares - 2*first_lot
			third_lot = int(shares/2)
			first_lot = int((shares - third_lot)/3)
			second_lot = shares - first_lot - third_lot
			#print(first_lot,second_lot,third_lot)
			return first_lot,second_lot,third_lot

	def on_deploying(self): #refresh it when reusing.
		self.initialized = False
		super().on_deploying()

#################### ARCHIVED ########################################

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

class OneToTWORiskReward_OLD(ManagementStrategy):

	def __init__(self,symbol,tradingplan):

		super().__init__("Management: 1-to-2 risk-reward ",symbol,tradingplan)

		self.manaTrigger = TwoToOneTriggerOLD("manage",self.ppro_out)

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


class ExpectedMomentum(ManagementStrategy):

	def __init__(self,symbol,tradingplan):

		super().__init__("Management: ExpectedMomentum ",symbol,tradingplan)

		self.manaTrigger = EMTrigger("manage",self)

		self.add_initial_triggers(self.manaTrigger)

		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		###upon activating, reset all parameters.
		self.total_orders = None
		self.orders_level = 1

		self.price = self.tradingplan.data[AVERAGE_PRICE]
		self.stop = self.tradingplan.data[STOP_LEVEL]

	def on_deploying(self): #refresh it when reusing.

		#print("ON DEPLOYING")
		self.initialized = False
		self.shares_loaded = False
		self.orders_level = 1
		super().on_deploying()

	def on_loading_up(self): #call this whenever the break at price changes. 

		self.price = self.tradingplan.data[BREAKPRICE]
		self.stop = self.tradingplan.data[STOP_LEVEL]
		self.gap = self.symbol.data[EXPECTED_MOMENTUM]

		coefficient = 1

		if self.tradingplan.data[POSITION] == LONG:
			coefficient = 1
		elif self.tradingplan.data[POSITION] == SHORT:
			coefficient = -1

		"""
		px1 = 0.3 #break even
		px2 = 1 #set second barage 
		px3 = 2 #set third barage
		px4 = 3.2 #over and out.

		"""
		self.tradingplan.data[TRIGGER_PRICE_1] = round(self.price+coefficient*self.gap*0.2,2)  #breakeven.
		self.tradingplan.data[TRIGGER_PRICE_2] = round(self.price+coefficient*self.gap*0.25,2)  #1
		self.tradingplan.data[TRIGGER_PRICE_3] = round(self.price+coefficient*self.gap*0.45,2)  #2
		self.tradingplan.data[TRIGGER_PRICE_4] = round(self.price+coefficient*self.gap*0.65,2)  #3
		self.tradingplan.data[TRIGGER_PRICE_5] = round(self.price+coefficient*self.gap*0.9,2)  #4
		self.tradingplan.data[TRIGGER_PRICE_6] = round(self.price+coefficient*self.gap*1.1,2)  #5
		self.tradingplan.data[TRIGGER_PRICE_7] = round(self.price+coefficient*self.gap*1.35,2)  #6
		self.tradingplan.data[TRIGGER_PRICE_8] = round(self.price+coefficient*self.gap*1.55,2)  #7
		self.tradingplan.data[TRIGGER_PRICE_9] = round(self.price+coefficient*self.gap*1.7,2)  #FINAL

		#set the price levels.
		#log_print(id_,"updating price levels.",price,self.price_levels[id_][1],self.price_levels[id_][2],self.price_levels[id_][3])

		self.tradingplan.tkvars[AUTOMANAGE].set(True)
		self.tradingplan.tkvars[PXT1].set(self.tradingplan.data[TRIGGER_PRICE_1])
		self.tradingplan.tkvars[PXT2].set(self.tradingplan.data[TRIGGER_PRICE_6])
		self.tradingplan.tkvars[PXT3].set(self.tradingplan.data[TRIGGER_PRICE_9])

		log_print(self.symbol_name,"Management price target adjusted:",self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])

		self.shares_loaded = True

		if self.initialized == False and self.management_start==True:
			self.on_start()

	def on_start(self):

		if self.shares_loaded:

			super().on_start()

			""" send out the limit orders """

			if self.tradingplan.data[USING_STOP]==False:
				self.set_mind("STOP BYPASSING: ON")

			self.tradingplan.current_price_level = 1
			self.orders_level = 1
			first_lot,second_lot,third_lot = self.shares_calculator(self.tradingplan.data[TARGET_SHARE])
			self.orders_organizer(first_lot,second_lot,third_lot)
			#self.deploy_n_batch_torpedoes(3)
			self.initialized == True
		else:
			self.management_start=True

	def shares_calculator(self,shares):

		if shares<3:
			return 0,shares,0
		else:
			# first_lot = int(shares/3)
			# third_lot = shares - 2*first_lot
			third_lot = int(shares/3)
			first_lot = int((shares - third_lot)/2)
			second_lot = shares - first_lot - third_lot
			#print(first_lot,second_lot,third_lot)
			return first_lot,second_lot,third_lot


	def deploy_n_batch_torpedoes(self,n):

		self.deploy_orders(self.total_orders[n-2])


	def deploy_orders(self,orders):

		coefficient = 1
		action = ""
		if self.tradingplan.data[POSITION] == LONG:
			action = LIMITSELL

		elif self.tradingplan.data[POSITION] == SHORT:
			action = LIMITBUY
			coefficient = -1

		#add some delay in here, random seconds. 
		#wait = [0.5,1.1,1.3,1.4,1.6]
		wait = [0,1,2,3,0]
		c = 0
		for key in sorted(orders.keys()):
			if orders[key]>0:
				price = round(self.price+coefficient*self.gap*key,2)
				share = orders[key]
				self.ppro_out.send([action,self.symbol_name,price,share,wait[c],"Exit price "])
				c+=1 

	def orders_organizer(self,first,second,third):

		### Arange this way to distribute it around the key areas.
		first_lot  =  [0.3,0.7,0.35,0.65,0.4,0.6,0.45,0.55,0.5]
		second_lot =  [0.8, 1.2, 0.85, 1.15, 0.9, 1.1, 0.95, 1.05, 1.0]
		third_lot  =  [1.3, 1.7, 1.35, 1.65, 1.4, 1.6, 1.45, 1.55, 1.5]

		all_lots = [first_lot,second_lot,third_lot]
		shares = [first,second,third]

		new_shares = [[0,0,0,0,0,0,0,0,0] for i in range(3)]

		for i in range(len(new_shares)):
			for j in range(shares[i]):
				new_shares[i][j%9] +=1

		share_distribution = {}
		for i in range(len(new_shares)):
			for j in range(len(new_shares[i])):
				share_distribution[all_lots[i][j]] = new_shares[i][j]

		# Now we have all orders. let's slice them up.

		total_list = []
		total_list.extend(first_lot)
		total_list.extend(second_lot)
		total_list.extend(third_lot)
		list.sort(total_list)
		orders = [total_list[4*i:4*i+4] for i in range(7)]
		#now chop the total_list into 6 sections. then grab the shares from all_orders

		total_orders = []
		for i in range(len(orders)):
			total_orders.append({})
			for j in range(len(orders[i])):
				total_orders[i][orders[i][j]] = share_distribution[orders[i][j]]
			
		self.total_orders = total_orders


class EMAStrategy(ManagementStrategy):

	def __init__(self,symbol,tradingplan):

		super().__init__("Management: EMA8",symbol,tradingplan)

		self.manaTrigger = EMAManager("EMA trigger",self)

		self.add_initial_triggers(self.manaTrigger)

		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		###upon activating, reset all parameters. 

		self.total_orders = None
		self.risk_per_share = 0

		self.initialized = False

		self.price = self.tradingplan.data[AVERAGE_PRICE]
		self.stop = self.tradingplan.data[STOP_LEVEL]


	def on_loading_up(self): #call this whenever the break at price changes. Onl
		#print("loading up:",self.initialized)
		if not self.initialized:
			log_print("LOADING UP!!!!","init:",self.initialized,self.management_start)
			self.price = self.tradingplan.data[AVERAGE_PRICE]
			self.stop = self.tradingplan.data[STOP_LEVEL]

			coefficient = 1

			self.tradingplan.tkvars[AUTOMANAGE].set(True)

			self.shares_loaded = True

			#shouldn't start here. because, sometime multiple entry is required. 7/10
			#No. This is a mechanism that works for INSTANT. if already started, but not intialized. restart the whole thing.

			if self.initialized == False and self.management_start==True:
				self.on_start()

	def on_start(self):

		if self.shares_loaded:

			super().on_start()
			log_print(self.symbol_name,"EMA manage starting")

			self.symbol.data[CUSTOM] = self.symbol.data[EMACOUNT]+5
			self.tradingplan.current_price_level = 1
			self.initialized = True

		else:
			self.management_start=True


	def on_deploying(self): #refresh it when reusing.
		#print("ON DEPLOYING")
		self.initialized = False
		self.shares_loaded = False
		self.tradingplan.current_price_level = 1
		self.orders_level = 1
		super().on_deploying()

	def reset(self):
		self.initialized = False


class TrendStrategy(ManagementStrategy):

	def __init__(self,symbol,tradingplan):

		super().__init__("Management: TrendStrategy EMA21",symbol,tradingplan)

		self.manaTrigger = TrendEMAManager("EMA trigger",self)

		self.add_initial_triggers(self.manaTrigger)

		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		###upon activating, reset all parameters. 

		self.total_orders = None
		self.risk_per_share = 0

		self.initialized = False

		self.price = self.tradingplan.data[AVERAGE_PRICE]
		self.stop = self.tradingplan.data[STOP_LEVEL]


	def on_loading_up(self): #call this whenever the break at price changes. Onl
		#print("loading up:",self.initialized)
		if not self.initialized:
			log_print("LOADING UP!!!!","init:",self.initialized,self.management_start)
			self.price = self.tradingplan.data[AVERAGE_PRICE]
			self.stop = self.tradingplan.data[STOP_LEVEL]

			coefficient = 1

			self.tradingplan.tkvars[AUTOMANAGE].set(True)

			self.shares_loaded = True

			#shouldn't start here. because, sometime multiple entry is required. 7/10
			#No. This is a mechanism that works for INSTANT. if already started, but not intialized. restart the whole thing.

			if self.initialized == False and self.management_start==True:
				self.on_start()

	def on_start(self):

		if self.shares_loaded:

			super().on_start()
			log_print(self.symbol_name,"TrendStrategy manage starting")

			#self.symbol.data[CUSTOM] = self.symbol.data[EMACOUNT]+5
			self.symbol.data[CUSTOM] = 1
			self.tradingplan.current_price_level = 1
			self.initialized = True

		else:
			self.management_start=True


	def on_deploying(self): #refresh it when reusing.
		#print("ON DEPLOYING")

		self.symbol.data[CUSTOM] = 1

		self.initialized = False
		self.shares_loaded = False
		self.tradingplan.current_price_level = 1
		self.orders_level = 1
		super().on_deploying()

	def reset(self):
		self.initialized = False
		

class FullManual(ManagementStrategy):

	def __init__(self,symbol,tradingplan):

		self.supress_warning = True

		super().__init__("Management: FullManual",symbol,tradingplan)

		#self.manaTrigger = HoldTilCloseManager("FullManual",self)

		#self.add_initial_triggers(self.manaTrigger)

		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		###upon activating, reset all parameters. 

		self.total_orders = None
		self.risk_per_share = 0

		self.initialized = False

		self.price = self.tradingplan.data[AVERAGE_PRICE]
		self.stop = self.tradingplan.data[STOP_LEVEL]


	def on_loading_up(self): #call this whenever the break at price changes. Onl
		#print("loading up:",self.initialized)
		if not self.initialized:
			log_print("LOADING UP!!!!","init:",self.initialized,self.management_start)
			self.price = self.tradingplan.data[AVERAGE_PRICE]
			self.stop = self.tradingplan.data[STOP_LEVEL]

			coefficient = 1

			self.tradingplan.tkvars[AUTOMANAGE].set(True)

			self.shares_loaded = True

			#shouldn't start here. because, sometime multiple entry is required. 7/10
			#No. This is a mechanism that works for INSTANT. if already started, but not intialized. restart the whole thing.

			if self.initialized == False and self.management_start==True:
				self.on_start()

	def on_start(self):

		if self.shares_loaded: 

			self.symbol.data[TRADE_TIMESTAMP] = 55800#self.symbol.data[TIMESTAMP]+300

			#super().on_start()
			log_print(self.symbol_name,"FullManual starting")

			
			self.tradingplan.current_price_level = 1
			self.initialized = True

		else:
			self.management_start=True


	def on_deploying(self): #refresh it when reusing.
		#print("ON DEPLOYING")
		self.initialized = False
		self.shares_loaded = False
		self.tradingplan.current_price_level = 1
		self.orders_level = 1
		#super().on_deploying()

	def reset(self):
		self.initialized = False


class SemiManual(ManagementStrategy):

	def __init__(self,symbol,tradingplan):

		super().__init__("Management: SemiManual",symbol,tradingplan)

		self.supress_warning = True

		self.manaTrigger = SemiManualManager("SemiManual Trigger",self)

		self.add_initial_triggers(self.manaTrigger)

		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		###upon activating, reset all parameters. 
		self.total_orders = None
		self.risk_per_share = 0

		self.initialized = False

		self.orders_level = 1

		self.price = self.tradingplan.data[BREAKPRICE]
		self.stop = self.tradingplan.data[STOP_LEVEL]


	def on_loading_up(self): #call this whenever the break at price changes. Onl
		#print("loading up:",self.initialized)
		if not self.initialized:
			log_print("LOADING UP!!!!","init:",self.initialized,self.management_start)
			self.price = self.tradingplan.data[AVERAGE_PRICE]
			self.stop = self.tradingplan.data[STOP_LEVEL]

			coefficient = 1

			self.tradingplan.tkvars[AUTOMANAGE].set(True)

			self.shares_loaded = True

			gap = abs(self.price-self.stop)/2

			if self.tradingplan.data[POSITION] ==LONG:
				self.tradingplan.data[TRIGGER_PRICE_1] = self.price+gap
				self.tradingplan.data[TRIGGER_PRICE_2] = self.price+gap*2
			elif self.tradingplan.data[POSITION] ==SHORT:
				self.tradingplan.data[TRIGGER_PRICE_1] = self.price-gap
				self.tradingplan.data[TRIGGER_PRICE_2] = self.price-gap*2
			

			print("checking price at ",self.tradingplan.data[TRIGGER_PRICE_1])
			# toss out half of the orders here. Don't because may not have enough shares.

			#shouldn't start here. because, sometime multiple entry is required. 7/10
			#No. This is a mechanism that works for INSTANT. if already started, but not intialized. restart the whole thing.

			if self.initialized == False and self.management_start==True:
				self.on_start()

	def on_start(self):

		if self.shares_loaded: 

			super().on_start()
			log_print(self.symbol_name,"SemiManual starting")

			self.initialized = True

		else:
			self.management_start=True


	def on_deploying(self): #refresh it when reusing.
		#print("ON DEPLOYING")
		self.initialized = False
		self.shares_loaded = False

		self.orders_level = 1
		super().on_deploying()

	def reset(self):
		self.initialized = False

class ScalpaTron(ManagementStrategy):

	def __init__(self,symbol,tradingplan):

		super().__init__("ScalpaTron",symbol,tradingplan)

		#self.manaTrigger = HoldTilCloseManager("HTC trigger",self)

		#self.add_initial_triggers(self.manaTrigger)

		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		###upon activating, reset all parameters. 

		self.initialized = False
		self.shares_loaded = False

		self.price = self.tradingplan.data[AVERAGE_PRICE]
		self.stop = self.tradingplan.data[STOP_LEVEL]

		self.gear = 1

		###KEY BOARD EVENT HERE.
		keyboard = threading.Thread(target=self.keyboard, daemon=True)
		keyboard.start()

	def update(self):
		pass

	def keyboard(self):
		print("KEY BAORD ACTIVEAETED")
		last_key = ""
		while True:  # making a loop
			key = keyboard.read_key(True)

			#################################################################################
			# self.ppro_out.send([BUY,self.symbol_name,share,self.description])
			# self.ppro_out.send([SELL,self.symbol_name,share,self.description])
			# self.ppro_out.send([LIMITBUY,self.symbol_name,price,share,wait[c],"Exit price "])
			# self.ppro_out.send([LIMITSELL,self.symbol_name,price,share,wait[c],"Exit price "])
			# self.ppro_out.send([STOPBUY,self.symbol_name,price,share])
			# self.ppro_out.send([STOPSELL,self.symbol_name,price,share])
			# self.ppro_out.send([CANCEL,self.symbol_name])
			##################################################################################
			last_key = key 


			if key == "+":
				self.ppro_out.send([BUY,self.symbol_name,5,""])
			elif key =="-":

				self.ppro_out.send([SELL,self.symbol_name,5,""])


			elif key =="8":
				self.gear = 3
				log_print("Gear swithching:",3)
			elif key =="5":
				self.gear = 2
				log_print("Gear swithching:",2)
			elif key =="2":
				self.gear = 1
				log_print("Gear swithching:",1)

			elif key =="3":
				bid = self.symbol.get_bid()
				l = round(bid+0.05*self.gear,2)
				self.ppro_out.send([LIMITSELL,self.symbol_name,l,5,0,"Exit price "])
			elif key =="6":
				bid = self.symbol.get_bid()
				l = round(bid+0.08*self.gear,2)
				self.ppro_out.send([LIMITSELL,self.symbol_name,l,5,0,"Exit price "])
			elif key =="9":
				bid = self.symbol.get_bid()
				l = round(bid+0.12*self.gear,2)
				self.ppro_out.send([LIMITSELL,self.symbol_name,l,5,0,"Exit price "])
			elif key =="1":
				bid = self.symbol.get_ask()
				l = round(bid-0.05*self.gear,2)
				self.ppro_out.send([LIMITBUY,self.symbol_name,l,5,0,"Exit price "])
			elif key =="4":
				bid = self.symbol.get_ask()
				l = round(bid-0.08*self.gear,2)
				self.ppro_out.send([LIMITBUY,self.symbol_name,l,5,0,"Exit price "])
			elif key =="7":
				bid = self.symbol.get_ask()
				l = round(bid-0.12*self.gear,2)
				self.ppro_out.send([LIMITBUY,self.symbol_name,l,5,0,"Exit price "])

			elif key =="*":
				self.ppro_out.send([CANCEL,self.symbol_name])

			elif key =="/":
				self.ppro_out.send(["Flatten",self.symbol_name])
			time.sleep(0.25)


	def on_loading_up(self): #call this whenever the break at price changes. Onl
		#print("loading up:",self.initialized)
	

		log_print("LOADING UP!!!!","init:",self.initialized)

		self.price = self.tradingplan.data[AVERAGE_PRICE]
		self.stop = self.tradingplan.data[STOP_LEVEL]

		self.shares_loaded = True

		if self.tradingplan.data[POSITION] ==LONG:
			self.stop = self.price-0.2
			self.tradingplan.data[STOP_LEVEL]=self.stop#self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(round(self.stop,2))

		elif self.tradingplan.data[POSITION] ==SHORT:
			self.stop = self.price+0.2
			self.tradingplan.data[STOP_LEVEL]=self.stop#self.symbol_data[self.stop]
			self.tradingplan.tkvars[STOP_LEVEL].set(round(self.stop,2))

		if self.initialized == False and self.management_start==True:
			self.on_start()

	def on_start(self):
		pass


	def on_deploying(self): #refresh it when reusing.

		#print("ON DEPLOYING")
		self.shares_loaded = False
		self.tradingplan.data[RELOAD_TIMES] +=1
		super().on_deploying()


	def reset(self):
		self.tradingplan.data[RELOAD_TIMES] +=1
		self.initialized = False
		self.shares_loaded = False


# clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)

# log_print(clsmembers)

# for i in clsmembers:
# 	log_print(i)
if __name__ == '__main__':
	
	while True:  # making a loop14564qerz
		print(keyboard.read_key(True))
		time.sleep(0.15)
	# def shares_calculator(shares):

	# 	if shares<3:
	# 		return 0,shares,0
	# 	else:
	# 		# first_lot = int(shares/3)
	# 		# third_lot = shares - 2*first_lot
	# 		third_lot = int(shares/3)
	# 		first_lot = int((shares - third_lot)/2)
	# 		second_lot = shares - first_lot - third_lot
	# 		#print(first_lot,second_lot,third_lot)
	# 		return first_lot,second_lot,third_lot
	# def orders_organizer(first,second,third):

	# 	### Arange this way to distribute it around the key areas.
	# 	first_lot  =  [0.3,0.7,0.35,0.65,0.4,0.6,0.45,0.55,0.5]
	# 	second_lot =  [0.8, 1.2, 0.85, 1.15, 0.9, 1.1, 0.95, 1.05, 1.0]
	# 	third_lot  =  [1.3, 1.7, 1.35, 1.65, 1.4, 1.6, 1.45, 1.55, 1.5]

	# 	all_lots = [first_lot,second_lot,third_lot]
	# 	shares = [first,second,third]

	# 	new_shares = [[0,0,0,0,0,0,0,0,0] for i in range(3)]

	# 	for i in range(len(new_shares)):
	# 		for j in range(shares[i]):
	# 			new_shares[i][j%9] +=1

	# 	share_distribution = {}
	# 	for i in range(len(new_shares)):
	# 		for j in range(len(new_shares[i])):
	# 			share_distribution[all_lots[i][j]] = new_shares[i][j]

	# 	# Now we have all orders. let's slice them up.

	# 	total_list = []
	# 	total_list.extend(first_lot)
	# 	total_list.extend(second_lot)
	# 	total_list.extend(third_lot)
	# 	list.sort(total_list)

	# 	print(len(total_list))
	# 	orders = [total_list[4*i:4*i+4] for i in range(7)]
	# 	#now chop the total_list into 6 sections. then grab the shares from all_orders

	# 	total_orders = []
	# 	for i in range(len(orders)):
	# 		total_orders.append({})
	# 		for j in range(len(orders[i])):
	# 			total_orders[i][orders[i][j]] = share_distribution[orders[i][j]]
			
	# 	for i in total_orders:
	# 		print(i)

	# 	return total_orders


	# first_lot,second_lot,third_lot = shares_calculator(200)
	# t=orders_organizer(first_lot,second_lot,third_lot)
	# count = 0

	# for i in t:
	# 	for key,v in i.items():
	# 		count+= key*v

	# print(count)