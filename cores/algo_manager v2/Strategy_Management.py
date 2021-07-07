from constant import *
from Symbol import *
from Triggers import *
from Util_functions import *
from Strategy import *
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
			self.deploy_n_batch_torpedoes(3)
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
		wait = [0.5,1.1,1.3,1.4,1.6]
		c = 0
		for key in sorted(orders.keys()):
			if orders[key]>0:
				price = round(self.price+coefficient*self.gap*key,2)
				share = orders[key]
				self.ppro_out.send([action,self.symbol_name,price,share,wait[c],"Exit price "])
				c+=1 

	def orders_organizer(self,first,second,third):

		### Arange this way to distribute it around the key areas. 
		first_lot  =  [0.5,1.0,0.4,0.9,0.6,1.1,0.7,1.2,0.3,0.8]
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
		
		self.price = self.tradingplan.data[AVERAGE_PRICE]
		self.stop = self.tradingplan.data[STOP_LEVEL]

	def on_loading_up(self): #call this whenever the break at price changes. 

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
		# self.tradingplan.data[TRIGGER_PRICE_4] = round(self.price+coefficient*self.gap*0.7,2)  #second
		# self.tradingplan.data[TRIGGER_PRICE_5] = round(self.price+coefficient*self.gap*1.2,2)  #third
		# self.tradingplan.data[TRIGGER_PRICE_6] = round(self.price+coefficient*self.gap*1.7,2)  #fourth
		# self.tradingplan.data[TRIGGER_PRICE_7] = round(self.price+coefficient*self.gap*2.2,2)  #fifth
		# self.tradingplan.data[TRIGGER_PRICE_8] = round(self.price+coefficient*self.gap*2.7,2)  #sixth
		# self.tradingplan.data[TRIGGER_PRICE_9] = round(self.price+coefficient*self.gap*3.2,2)  #FINAL

		#set the price levels.
		#log_print(id_,"updating price levels.",price,self.price_levels[id_][1],self.price_levels[id_][2],self.price_levels[id_][3])

		self.tradingplan.tkvars[AUTOMANAGE].set(True)
		# self.tradingplan.tkvars[PXT1].set(self.tradingplan.data[TRIGGER_PRICE_1])
		# self.tradingplan.tkvars[PXT2].set(self.tradingplan.data[TRIGGER_PRICE_7])
		# self.tradingplan.tkvars[PXT3].set(self.tradingplan.data[TRIGGER_PRICE_9])

		#log_print(self.symbol_name,"Management price target adjusted:",self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])

		self.shares_loaded = True

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
			# first_lot,second_lot,third_lot = self.shares_calculator(self.tradingplan.data[TARGET_SHARE])
			# self.orders_organizer(first_lot,second_lot,third_lot)
			# self.deploy_n_batch_torpedoes(3)
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

# clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)

# log_print(clsmembers)

# for i in clsmembers:
# 	log_print(i)