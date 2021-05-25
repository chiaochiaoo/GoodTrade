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

class OneToTWORiskReward(ManagementStrategy):

	def __init__(self,symbol,tradingplan):

		super().__init__("Management: 1-to-2 risk-reward ",symbol,tradingplan)

		self.manaTrigger = TwoToOneTrigger("manage",self)

		self.add_initial_triggers(self.manaTrigger)

		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		###upon activating, reset all parameters. 

		self.first_orders = None
		self.second_orders = None
		self.third_orders = None

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

		self.tradingplan.data[PXT1] = round(self.price+coefficient*self.gap*0.3,2) #break even price
		self.tradingplan.data[PXT2] = round(self.price+coefficient*self.gap*1,2)  #transitional
		self.tradingplan.data[PXT3] = round(self.price+coefficient*self.gap*2,2)  #transitional
		self.tradingplan.data[PXT4] = round(self.price+coefficient*self.gap*3.2,2)

		#set the price levels.
		#log_print(id_,"updating price levels.",price,self.price_levels[id_][1],self.price_levels[id_][2],self.price_levels[id_][3])

		self.tradingplan.tkvars[AUTOMANAGE].set(True)
		self.tradingplan.tkvars[PXT1].set(self.tradingplan.data[PXT1])
		self.tradingplan.tkvars[PXT2].set(self.tradingplan.data[PXT3])
		self.tradingplan.tkvars[PXT3].set(self.tradingplan.data[PXT4])

		log_print(self.symbol_name,"Management price target adjusted:",self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3],self.tradingplan.data[PXT4])

		self.shares_loaded = True

		if self.initialized == False and self.management_start==True:
			self.on_start()

	def on_start(self):

		if self.shares_loaded:

			super().on_start()

			""" send out the limit orders """
			self.tradingplan.current_price_level = 0
			first_lot,second_lot,third_lot = self.shares_calculator(self.tradingplan.data[TARGET_SHARE])
			self.orders_organizer(first_lot,second_lot,third_lot)
			self.deploy_first_batch_torpedoes()
			self.initialized == True
		else:
			self.management_start=True

	def shares_calculator(self,shares):

		if shares<3:
			return 0,shares,0
		else:
			first_lot = int(shares/3)
			third_lot = shares - 2*first_lot

			return first_lot,first_lot,third_lot

	def deploy_first_batch_torpedoes(self):
		self.deploy_orders(self.first_orders)

	def deploy_second_batch_torpedoes(self):
		self.deploy_orders(self.second_orders)
	def deploy_third_batch_torpedoes(self):
		self.deploy_orders(self.third_orders)

	def deploy_orders(self,orders):

		coefficient = 1
		action = ""
		if self.tradingplan.data[POSITION] == LONG:
			action = LIMITSELL

		elif self.tradingplan.data[POSITION] == SHORT:
			action = LIMITBUY
			coefficient = -1

		for key in sorted(orders.keys()):
			if orders[key]>0:
				price = round(self.price+coefficient*self.gap*key,2)
				share = orders[key]
				self.ppro_out.send([action,self.symbol_name,price,share,"Exit price "])

	def orders_organizer(self,first,second,third):

		first_lot  =  [0.7,0.8,0.6,0.9,0.5,1.0,0.4,1.1,0.3,1.2]
		second_lot =  [1.7,1.8,1.6,1.9,1.5,2.0,1.4,2.1,1.3,2.2]
		third_lot  =  [2.7,2.8,2.6,2.9,2.5,3.0,2.4,3.1,2.3,3.2]

		all_lots = [first_lot,second_lot,third_lot]
		shares = [first,second,third]

		new_shares = [[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]]

		for i in range(len(new_shares)):
			for j in range(shares[i]):
				new_shares[i][j%10] +=1

		all_orders = [{},{},{}]
		for i in range(len(all_lots)):
			for j in range(len(new_shares[i])):
				all_orders[i][all_lots[i][j]] = new_shares[i][j]

		self.first_orders = all_orders[0]
		self.second_orders = all_orders[1]
		self.third_orders = all_orders[2]

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