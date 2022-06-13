from constant import *
from Symbol import *
from Triggers import *
from Util_functions import *
from Strategy import *
import threading
import time

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

class ManagementStrategyPair():

	def __init__(self,name,symbol1:Symbol,symbol2:Symbol,tradingplan):

		self.management_start = False
		self.initialized = False
		self.shares_loaded = False

		self.name = name
		self.symbol1 = symbol1
		self.symbol2 = symbol2
		self.tradingplan = tradingplan


	def update(self):

		pass

	def on_start(self):

		pass 

	def on_deploying(self):

		pass

	def reset(self):

		pass


class MarketMaking(ManagementStrategyPair):


	def __init__(self,symbol1:Symbol,symbol2:Symbol,tradingplan):

		### previously it is relayed on trigger. 

		super().__init__("Management:Market Making ",symbol1,symbol2,tradingplan)

		self.symbol1 = symbol1
		self.symbol2 = symbol2
		
		self.symbol1.turn_market_making(tradingplan)
		self.symbol2.turn_market_making(tradingplan)

	def update(self):

		print("hello")

	# """ for management plan only """
	# def on_loading_up(self):
	# 	pass

	# """ for management plan only """
	# def on_start(self):
	# 	self.manaTrigger.total_reset()
	# 	self.tradingplan.current_price_level = 1
	# 	self.set_mind("")
	# 	log_print(self.symbol_name," ",self.strategy_name ," starts")


	# """ for management plan only """
	# def on_deploying(self):
	# 	self.current_triggers = set()
	# 	for i in self.initial_triggers:
	# 		self.current_triggers.add(i)

	# def reset(self):
	# 	pass

